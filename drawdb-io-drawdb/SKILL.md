---
name: drawdb-io-drawdb
description: Free, simple, and intuitive online database diagram editor and SQL generator.
source: https://github.com/drawdb-io/drawdb
license: AGPL-3.0
stars: 40444
language: JavaScript
topics: database, database-design, database-diagram, database-schema, dbml, diagram-editor, editor, er-diagram, erd, erdiagram, indexeddb, mariadb, mcp, oracle-database, oracle-db, postgresql, schema-design, sql, sql-server, sqlite
saved: 2026-11-26
---

# drawdb-io/drawdb

## Summary from README
drawDB Free, simple, and intuitive database schema editor and SQL generator. DrawDB is a robust and user-friendly database entity relationship diagram (ERD) editor right in your browser. Build diagrams with a few clicks, export and import SQL scripts, generate migrations, customize your editor, and more without creating an account. See the full set of features on [here](https://drawdb.app/).

## When to use
Use this skill when the task involves:
- Designing or editing database schemas and entity-relationship diagrams (ERDs).
- Generating or parsing SQL scripts for various databases (PostgreSQL, MySQL/MariaDB, SQLite, SQL Server, Oracle).
- Working with DBML or database diagram representations.
- Automating ERD generation or schema migration tasks using scripts like `erd_generator.py`.

## How to use

### Local Development
```bash
git clone https://github.com/drawdb-io/drawdb
cd drawdb
npm install
npm run dev
```

### Build
```bash
git clone https://github.com/drawdb-io/drawdb
cd drawdb
npm install
npm run build
```

### Docker Build & Run
```bash
docker build -t drawdb .
docker run -p 3000:80 drawdb
```

To enable sharing with a backend server:
```bash
docker run -p 3000:80 -e VITE_BACKEND_URL=https://your-drawdb-server.example.com ghcr.io/drawdb-io/drawdb:latest
```

### Running Scripts
To generate or manipulate ERDs programmatically:
```bash
python erd_generator.py
```

## Limitations
- Advanced diagram collaboration and sharing features require setting up a separate `drawdb-server` instance.
- Direct database connection imports depend on browser-supported clients or backend proxy endpoints depending on the deployment configuration.