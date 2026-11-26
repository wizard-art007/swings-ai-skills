---
name: k1low-tbls
description: tbls is a CI-Friendly tool to document a database, written in Go.
source: https://github.com/k1LoW/tbls
license: MIT
stars: 4407
language: Go
topics: bigquery, continuous-integration, database-document, database-schema, documentation-tool, dynamodb, er-diagram, excel, hacktoberfest, mariadb, markdown, mermaid, mysql, plantuml, postgresql, redshift, snowflake, spanner, sqlite, sqlserver
saved: 2026-11-26
---

# tbls

`tbls` is a CI-friendly documentation and linting tool for databases written in Go. It introspects schema metadata across major relational, NoSQL, and analytical engines to generate living Markdown, HTML, JSON, or ER diagrams, verify schema consistency in CI, and measure documentation coverage.

---

## When to use

- **Living Database Documentation**: Keep schema documentation version-controlled in Git alongside application code, updating automatically upon schema migrations.
- **CI/CD Schema Drift Detection**: Detect discrepancies between production/staging database schemas and documented repository schemas during pull requests.
- **Automated Schema Linting**: Enforce organization-wide rules like mandatory column comments, snake_case naming conventions, foreign key definitions, and primary key existence.
- **Documentation Coverage Gates**: Measure percentage of tables and columns with descriptions and fail builds if documentation drops below a threshold.
- **Domain-Specific ER Diagrams (Viewpoints)**: Partition large enterprise schemas (hundreds of tables) into isolated, domain-focused Mermaid or PlantUML ER diagrams.
- **Virtual Relationships**: Document logical relationships and foreign keys when the underlying database engine lacks physical foreign key constraints (e.g., partitioned tables, BigQuery, microservices with shared tables).

---

## How to use

### 1. Installation

```bash
# macOS via Homebrew
brew install k1LoW/tap/tbls

# Go install
go install github.com/k1LoW/tbls@latest

# Run via Docker
docker run --rm -v $(pwd):/work -w /work k1low/tbls:latest [command]
```

### 2. Supported Connection Strings (DSNs)

| Database | DSN Format Example |
| :--- | :--- |
| **PostgreSQL** | `postgres://user:pass@127.0.0.1:5432/dbname?sslmode=disable` |
| **MySQL / MariaDB** | `mysql://user:pass@tcp(127.0.0.1:3306)/dbname` |
| **SQLite** | `sqlite://path/to/database.db` |
| **SQL Server** | `sqlserver://user:pass@127.0.0.1:1433?database=dbname` |
| **Snowflake** | `snowflake://user:pass@account/dbname/schemaname?warehouse=whname` |
| **BigQuery** | `bigquery://project-id/dataset-id` |
| **DynamoDB** | `dynamodb://` (uses AWS environment variables) |

---

### 3. Core CLI Commands

#### Generate Documentation
Generate GFM (GitHub Flavored Markdown) documentation with embedded Mermaid diagrams:

```bash
# Generate docs from DSN into docs/db directory
tbls doc postgres://user:password@localhost:5432/app_db docs/db

# Use existing .tbls.yml configuration
tbls doc --force
```

#### Export Formats (`tbls out`)
Export database schema metadata directly to specific file formats:

```bash
# Export schema to JSON
tbls out postgres://user:password@localhost:5432/app_db -t json -o schema.json

# Export to single HTML report
tbls out postgres://user:password@localhost:5432/app_db -t html -o schema.html

# Export schema to Excel sheet
tbls out postgres://user:password@localhost:5432/app_db -t xlsx -o schema.xlsx

# Export ER diagram to PlantUML / Mermaid directly
tbls out postgres://user:password@localhost:5432/app_db -t plantuml -o schema.puml
tbls out postgres://user:password@localhost:5432/app_db -t mermaid -o schema.mmd
```

#### Diff Database Against Documentation
Verify if the target database matches documented files:

```bash
# Diff current database against saved docs/ directory
tbls diff postgres://user:password@localhost:5432/app_db docs/db

# Diff two databases directly
tbls diff postgres://user:password@host1:5432/db postgres://user:password@host2:5432/db
```

#### Lint Schema Conformance
Validate schema rules against production or migration databases:

```bash
tbls lint postgres://user:password@localhost:5432/app_db
```

#### Measure Documentation Coverage
Audit schema description percentages:

```bash
tbls coverage postgres://user:password@localhost:5432/app_db
```

---

### 4. Configuration File (`.tbls.yml`)

Place `.tbls.yml` in the root of your repository to define linting rules, viewpoints, virtual relationships, and custom descriptions:

```yaml
dsn: postgres://app_user:app_pass@localhost:5432/app_db?sslmode=disable
docPath: docs/db

er:
  format: mermaid      # mermaid, plantuml, svg, png
  comment: true        # Show column descriptions in ER diagram
  distance: 1          # Relation traversal depth for table diagrams

# Virtual descriptions without modifying database metadata
comments:
  - table: orders
    tableComment: "Stores all customer checkout records"
    columnComments:
      status: "Values: pending, processing, completed, refunded"

# Define virtual foreign keys (useful if engine lacks physical constraints)
relations:
  - table: audit_logs
    columns:
      - user_id
    parentTable: users
    parentColumns:
      - id
    def: "Virtual link between logs and user entities"

# Break down massive schemas into functional domain sub-diagrams
viewpoints:
  - name: "Billing Subsystem"
    desc: "Tables supporting payments, subscriptions, and invoicing"
    tables:
      - accounts
      - invoices
      - payment_methods
      - subscriptions

# Schema linting rules
lint:
  requireTableComment:
    enabled: true
  requireColumnComment:
    enabled: true
    exclude:
      - id
      - created_at
      - updated_at
      - deleted_at
  requireColumns:
    - name: id
    - name: created_at
  unneededIndex:
    enabled: true
  duplicateIndex:
    enabled: true
```

---

### 5. Automation / CI Pipeline Example (GitHub Actions)

Run `tbls` in CI to ensure documentation is committed and schema lint passes:

```yaml
name: Schema Check & Documentation

on:
  pull_request:
    paths:
      - 'migrations/**'
      - '.tbls.yml'
      - 'docs/db/**'

jobs:
  tbls-check:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: app_db
          POSTGRES_USER: runner
          POSTGRES_PASSWORD: password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Install tbls
        run: |
          curl -sL https://git.io/use-tbls | bash
          sudo mv tbls /usr/local/bin/

      - name: Run Database Migrations
        run: |
          # Replace with your migration tool (e.g., migrate, flyway, goose)
          psql "postgres://runner:password@localhost:5432/app_db?sslmode=disable" -f schema.sql

      - name: Run Schema Lint
        run: |
          tbls lint "postgres://runner:password@localhost:5432/app_db?sslmode=disable"

      - name: Verify Documentation Diff
        run: |
          tbls diff "postgres://runner:password@localhost:5432/app_db?sslmode=disable" docs/db
```

---

## Limitations

- **Image Generation Dependencies**: Generating rasterized/vector formats (`.png`, `.svg`) directly from `tbls` requires external rendering CLI binaries (such as `plantuml` with Graphviz or `@mermaid-js/mermaid-cli`). Using native text output formats (`mermaid`, `plantuml`) circumvents this dependency.
- **Static Schema Introspection Only**: Rules and docs are generated from schema metadata tables/information schema. It cannot analyze runtime query patterns, query plans, or dynamic JSON payload structures within columns.
- **Heterogeneous Driver Metadata Depth**: Cloud analytical and NoSQL engines (BigQuery, Redshift, Snowflake, DynamoDB) do not expose the same depth of metadata (e.g., index types, trigger definitions, check constraints) as mature RDBMS engines (PostgreSQL, MySQL).
- **Network & Credential Access**: CI/CD jobs must have direct TCP connectivity or SSH tunneling to a populated database or apply migration scripts to a dedicated ephemeral container.