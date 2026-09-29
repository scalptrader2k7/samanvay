# Samanvay final architecture and workflows

These diagrams show implemented components only. Dashed external deployment paths are prepared but not validated with managed accounts.

## End-to-end architecture

```mermaid
flowchart LR
    A[Protected CSV or conservative XLSX input] --> B[Phase 2 canonical source record]
    X[CPSE or SAP-shaped CSV contract] --> P[Phase 12 read-only mapping and preview]
    P --> B
    B --> C[Phase 3 normalization and evidence extraction]
    C --> D[Phase 4 bounded lexical candidate retrieval]
    D --> E[Phase 5 pair evidence and safety rules]
    E --> F[Reviewer interface]
    F --> G[Transactional decision service]
    G --> H[Prototype registry and source mappings]
    G --> I[Append-only decisions audit and mapping history]
    H --> J[Quality dashboard and CSV JSON XLSX exports]
    I --> J
    K[(Local SQLite)] --- G
    L[(Managed PostgreSQL prepared externally pending)] -.-> G
```

## Material matching workflow

```mermaid
flowchart TD
    A[Original source ID and description] --> B[Derived normalized text and supported attributes]
    B --> C[Top-k lexical candidates with retrieval reasons]
    C --> D[Field-by-field comparison]
    D --> E{Supported critical conflict?}
    E -- Yes --> F[Conflict and identity merge blocked]
    E -- No --> G{Evidence disposition}
    G --> H[Exact duplicate proposal]
    G --> I[Near duplicate proposal]
    G --> J[Possible functional equivalent suggestion]
    G --> K[No match or insufficient evidence]
    F --> L[Qualified reviewer]
    H --> L
    I --> L
    J --> L
    K --> L
```

## Reviewer and governance lifecycle

```mermaid
stateDiagram-v2
    [*] --> Proposed
    Proposed --> Approved: explicit reviewer action
    Proposed --> Rejected: explicit reviewer action
    Proposed --> Deferred: explicit reviewer action
    Approved --> Deferred: reconsider with reason
    Approved --> Rejected: reconsider with reason
    Deferred --> Approved: reconsider and repeat safety checks
    Rejected --> Approved: reconsider and repeat safety checks
    Approved --> PrototypeRegistry: identity only
    Approved --> FunctionalRelationship: possible equivalence only
    PrototypeRegistry --> AuditHistory
    FunctionalRelationship --> AuditHistory
    Rejected --> AuditHistory
    Deferred --> AuditHistory
```

## Integration boundary

```mermaid
flowchart LR
    A[Sponsor-owned export] --> B[Explicit versioned field mapping]
    B --> C[Validation and retained raw fields]
    C --> D[Canonical source contract]
    D --> E[Existing unchanged matching core]
    C --> F[Read-only preview response]
    F -. no persistence .-> G[Reviewer browser]
    H[SAP or ERP] -. no live connection or writes .- B
```

Final acceptance note: committed-checkout seeding uses a tested fallback from committed candidate data when the ignored Phase 3 pack is absent.
