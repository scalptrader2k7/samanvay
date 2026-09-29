# Phase 13 clean-copy reproduction record

A clean filesystem copy of the current working tree was created outside the repository on 30 September 2026. `.git`, `.local`, Python caches and local storage were excluded. In that copy:

1. Python 3.13 created a new virtual environment.
2. `pip install -r requirements.txt` completed successfully.
3. `phase13_demo.py` seeded all 9,245 records into new SQLite storage.
4. The copied application completed retrieval, pair evidence, a critical-conflict block, approval, reconsideration, registry/mapping, audit, dashboard, exports and both integration previews.
5. All three protected raw-file hashes remained unchanged.

The copied run returned `status: passed`, 9,245 inserted records, 2 active mappings, 3 retained audit actions and one active prototype registry entry. Its prototype code was generated for that isolated workspace; prototype IDs are not compared across workspaces.

This proves installation and execution from a clean copy of the current implementation. It is not yet proof of a fresh Git checkout because major Phase 5–13 files in the source working tree remain untracked. Once the project owner commits all intended implementation and evidence files, repeat these commands from `git clone` and replace this qualification with the resulting commit ID.

Managed Neon/OIDC/Vercel reproduction was not attempted because the required accounts and credentials were unavailable. Local SQLite and demo authentication were used.

## Final repository note

Local commit `e38c8e1` first captured the complete Phase 5–13 tree. The following reproducibility fix makes seeding rebuild the enriched records from committed candidate data when the ignored Phase 3 output pack is absent. The final amended commit is the clone-test target. Push to `origin/main` was attempted but GitHub returned HTTP 403 because the authenticated account `scalptrader2k7` lacks permission to `latenth3-crypto/samanvay`.

The evidence runner uses temporary SQLite storage outside its output pack; database files are not submission artifacts.
