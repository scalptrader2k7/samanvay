"""Workspace persistence boundary for local and managed Phase 8 service storage."""
from contextlib import closing, contextmanager
import hashlib
from pathlib import Path
import re
import sqlite3

from prototype_registry import RegistryStore, utc_now


WORKSPACE_RE = re.compile(r"^[a-z][a-z0-9_-]{2,63}$")


class WorkspaceAccessError(PermissionError):
    pass


class WorkspaceNotFoundError(KeyError):
    pass


class LocalWorkspaceStorage:
    """Durable local-development storage using one SQLite file per workspace."""
    backend_name = "sqlite-local"
    durable_for_deployment = False

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.catalog_path = self.root / "workspace_catalog.sqlite3"
        with closing(sqlite3.connect(self.catalog_path)) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS workspaces (
                    workspace_id TEXT PRIMARY KEY,
                    owner_subject TEXT NOT NULL,
                    public_read INTEGER NOT NULL DEFAULT 0 CHECK(public_read IN (0,1)),
                    created_at TEXT NOT NULL
                )
            """)

    @staticmethod
    def validate_workspace_id(workspace_id):
        if not WORKSPACE_RE.fullmatch(workspace_id):
            raise ValueError("workspace_id must match ^[a-z][a-z0-9_-]{2,63}$")

    def _database_path(self, workspace_id):
        digest = hashlib.sha256(workspace_id.encode()).hexdigest()
        return self.root / f"workspace-{digest}.sqlite3"

    def create_workspace(self, workspace_id, owner_subject, *, public_read=False):
        self.validate_workspace_id(workspace_id)
        if not owner_subject or len(owner_subject) > 200:
            raise ValueError("owner_subject is required and must be at most 200 characters")
        with closing(sqlite3.connect(self.catalog_path)) as connection:
            existing = connection.execute(
                "SELECT owner_subject, public_read FROM workspaces WHERE workspace_id=?",
                (workspace_id,)).fetchone()
            if existing:
                if existing != (owner_subject, int(public_read)):
                    raise WorkspaceAccessError("Workspace already exists with different ownership")
                return False
            connection.execute("INSERT INTO workspaces VALUES (?,?,?,?)",
                               (workspace_id, owner_subject, int(public_read), utc_now()))
            connection.commit()
        with RegistryStore(self._database_path(workspace_id), workspace_id=workspace_id):
            pass
        return True

    def metadata(self, workspace_id):
        self.validate_workspace_id(workspace_id)
        with closing(sqlite3.connect(self.catalog_path)) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM workspaces WHERE workspace_id=?", (workspace_id,)).fetchone()
        if not row:
            raise WorkspaceNotFoundError(workspace_id)
        return dict(row)

    @contextmanager
    def open_workspace(self, workspace_id, subject=None, *, write=False):
        meta = self.metadata(workspace_id)
        if write and subject != meta["owner_subject"]:
            raise WorkspaceAccessError("Only the workspace owner may modify it")
        if not write and not meta["public_read"] and subject != meta["owner_subject"]:
            raise WorkspaceAccessError("Workspace read access denied")
        with RegistryStore(self._database_path(workspace_id), workspace_id=workspace_id) as store:
            yield store

    def readiness(self):
        with closing(sqlite3.connect(self.catalog_path)) as connection:
            connection.execute("SELECT 1").fetchone()
        return {"backend": self.backend_name, "available": True,
                "durable_for_deployment": self.durable_for_deployment}


def serialize_registry(store):
    return bytes(store.connection.serialize())


def restore_registry(database_image, *, workspace_id="standalone"):
    store = RegistryStore(":memory:", workspace_id=workspace_id)
    if database_image:
        store.connection.deserialize(bytes(database_image))
        store._create_schema()
    return store


class PostgresWorkspaceStorage:
    """Durable Neon-compatible workspace storage; SQLite runs only in memory."""
    backend_name = "postgres-workspace-image"
    durable_for_deployment = True

    def __init__(self, database_url):
        if not database_url:
            raise ValueError("DATABASE_URL is required for PostgreSQL storage")
        self.database_url = database_url
        self._create_schema()

    def _connect(self):
        import psycopg
        return psycopg.connect(self.database_url)

    def _create_schema(self):
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS samanvay_workspaces (
                    workspace_id VARCHAR(64) PRIMARY KEY,
                    owner_subject VARCHAR(200) NOT NULL,
                    public_read BOOLEAN NOT NULL DEFAULT FALSE,
                    database_image BYTEA NOT NULL,
                    revision BIGINT NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)

    def create_workspace(self, workspace_id, owner_subject, *, public_read=False):
        LocalWorkspaceStorage.validate_workspace_id(workspace_id)
        if not owner_subject or len(owner_subject) > 200:
            raise ValueError("owner_subject is required and must be at most 200 characters")
        blank = RegistryStore(":memory:")
        try:
            image = serialize_registry(blank)
        finally:
            blank.close()
        with self._connect() as connection:
            row = connection.execute("""
                SELECT owner_subject, public_read FROM samanvay_workspaces
                WHERE workspace_id=%s
            """, (workspace_id,)).fetchone()
            if row:
                if row != (owner_subject, public_read):
                    raise WorkspaceAccessError("Workspace already exists with different ownership")
                return False
            connection.execute("""
                INSERT INTO samanvay_workspaces
                (workspace_id,owner_subject,public_read,database_image)
                VALUES (%s,%s,%s,%s)
            """, (workspace_id, owner_subject, public_read, image))
        return True

    def metadata(self, workspace_id):
        LocalWorkspaceStorage.validate_workspace_id(workspace_id)
        with self._connect() as connection:
            row = connection.execute("""
                SELECT workspace_id, owner_subject, public_read, revision
                FROM samanvay_workspaces WHERE workspace_id=%s
            """, (workspace_id,)).fetchone()
        if not row:
            raise WorkspaceNotFoundError(workspace_id)
        return {"workspace_id": row[0], "owner_subject": row[1],
                "public_read": row[2], "revision": row[3]}

    @contextmanager
    def open_workspace(self, workspace_id, subject=None, *, write=False):
        LocalWorkspaceStorage.validate_workspace_id(workspace_id)
        with self._connect() as connection:
            query = """
                SELECT owner_subject, public_read, database_image, revision
                FROM samanvay_workspaces WHERE workspace_id=%s
            """ + (" FOR UPDATE" if write else "")
            row = connection.execute(query, (workspace_id,)).fetchone()
            if not row:
                raise WorkspaceNotFoundError(workspace_id)
            owner, public_read, image, revision = row
            if write and subject != owner:
                raise WorkspaceAccessError("Only the workspace owner may modify it")
            if not write and not public_read and subject != owner:
                raise WorkspaceAccessError("Workspace read access denied")
            store = restore_registry(image, workspace_id=workspace_id)
            try:
                yield store
                if write:
                    updated = serialize_registry(store)
                    result = connection.execute("""
                        UPDATE samanvay_workspaces
                        SET database_image=%s, revision=revision+1, updated_at=NOW()
                        WHERE workspace_id=%s AND revision=%s
                    """, (updated, workspace_id, revision))
                    if result.rowcount != 1:
                        raise RuntimeError("Workspace revision changed during transaction")
            finally:
                store.close()

    def readiness(self):
        with self._connect() as connection:
            connection.execute("SELECT 1").fetchone()
        return {"backend": self.backend_name, "available": True,
                "durable_for_deployment": self.durable_for_deployment}
