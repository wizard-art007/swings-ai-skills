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

# k1LoW/tbls

`tbls` is a CI-friendly command-line tool written in Go to automatically document databases, lint database schemas, measure documentation coverage, and render ER diagrams in multiple formats.

## When to use

Use `tbls` when you need to:
- **Generate Database Documentation**: Automatically produce GFM (GitHub Flavored Markdown), HTML, JSON, YAML, or Excel database documentation.
- **Draw ER Diagrams**: Generate ER diagrams using Mermaid, PlantUML, PNG, or SVG.
- **Lint Database Schemas**: Enforce conventions such as mandatory column comments, table naming schemes, primary key presence, or foreign key constraints.
- **Check Schema Diffs**: Verify diffs between a running database and current documentation or between two database instances in CI/CD pipelines.
- **Track Doc Coverage**: Calculate and enforce documentation coverage metrics across tables and columns.
- **Enhance Schemas Virtually**: Define virtual relations, extra comments, and viewpoints without modifying the database schema directly.

---

## How to use

### Basic CLI Commands

#### 1. Generate Documentation
Generate GFM markdown files in the `./docs/` directory from a database DSN:

```bash
# PostgreSQL
tbls doc postgres://user:password@localhost:5432/dbname?sslmode=disable docs/

# MySQL / MariaDB
tbls doc my://user:password@tcp(localhost:3306)/dbname docs/

# SQLite
tbls doc sq://path/to/sqlite.db docs/
```

#### 2. Diff Database and Documentation
Compare current database state against existing generated documentation:

```bash
tbls diff postgres://user:password@localhost:5432/dbname docs/
```

Compare two databases:
```bash
tbls diff postgres://user:pass@host1:5432/db postgres://user:pass@host2:5432/db
```

#### 3. Lint Database Schema
Run schema linting using default or configured rules:

```bash
tbls lint postgres://user:password@localhost:5432/dbname
```

#### 4. Measure Documentation Coverage
Check documentation percentage for tables and columns:

```bash
tbls coverage postgres://user:password@localhost:5432/dbname
```

---

### Configuration (`.tbls.yml`)

Save a `.tbls.yml` file in the project root to store credentials, virtual relations, lint rules, and formatting options.

```yaml
dsn: postgres://root:secret@127.0.0.1:5432/my_db?sslmode=disable
docPath: docs

er:
  format: mermaid # options: mermaid, plantuml, png, svg
  comment: true

comments:
  - table: users
    tableComment: Primary application user accounts.
    columnComments:
      id: Unique user identifier
      email: User login email address

relations:
  - table: orders
    columns:
      - user_id
    parentTable: users
    parentColumns:
      - id
    def: "Virtual relation for unconstrained user_id foreign key"

lint:
  requireTableComment:
    enabled: true
  requireColumnComment:
    enabled: true
    exclude:
      - created_at
      - updated_at
  requireUnqiueIndexName:
    enabled: true
```

---

## Limitations

- **Database Connectivity**: Requires direct network access to the target database server or supported exported metadata.
- **External Image Rendering Dependencies**: Generating image-based ER diagrams (`png`, `svg`) via PlantUML or Mermaid requires external CLI installations (`plantuml`, `@mermaid-js/mermaid-cli`), unless outputting native text format (`mermaid` / `plantuml`).
- **Static Schema Inspection**: Linting and documentation rely on schema reflection metadata rather than runtime query analysis.
- **Driver-Specific Features**: Advanced data types or vendor-specific features across cloud databases (e.g., BigQuery, DynamoDB, Spanner) may have partial metadata support compared to standard relational databases (PostgreSQL/MySQL).
