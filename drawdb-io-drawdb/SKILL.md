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

Use this skill when the task involves: database, database-design, database-diagram, database-schema, dbml, diagram-editor, editor, er-diagram, erd, erdiagram.

- Source code: cloned on demand (`ensure_repo(skill)`); licence file(s): see source
- Original README: `README_source.md`

## Summary from README
drawDB Free, simple, and intuitive database schema editor and SQL generator. DrawDB is a robust and user-friendly database entity relationship diagram (ERD) editor right in your browser. Build diagrams with a few clicks, export and import SQL scripts, generate migrations, customize your editor, and more without creating an account. See the full set of features on [here](https://drawdb.app/). ## Getting Started ### Local Development ```bash git clone https://github.com/drawdb-io/drawdb cd drawdb npm install npm run dev ``` ### Build ```bash git clone https://github.com/drawdb-io/drawdb cd drawdb npm install npm run build ``` ### Docker Build ```bash docker build -t drawdb . docker run -p 3000:80 drawdb ``` If you want to enable sharing, set up the [server](https://github.com/drawdb-io/drawdb-server) and environment variables according to `.env.sample`. This is optional unless you need to share files. With the Docker image, pass the server URL when starting the container. No rebuild is needed: ```bash docker run -p 3000:80 -e VITE_BACKEND_URL=https://your-drawdb-server.example.com ghcr.io/drawdb-io/drawdb:latest ``` ## Contributing Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project. ## Support - Join discussions: [Discord](https://discord.gg/BrjZgNrmR6)
