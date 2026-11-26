---
name: agents365-ai-drawio-skill
description: Agent skill that turns natural language, code, Terraform/K8s, SQL, OpenAPI, AsyncAPI, Protobuf and GraphQL sources into editable, tested draw.io architecture diagrams: incremental sync, multi-view projections, and architecture-as-code validation.
source: https://github.com/Agents365-ai/drawio-skill
license: MIT
stars: 10947
language: Python
topics: agent-skills, architecture, architecture-diagram, asyncapi, bpmn, c4-model, claude-code, diagram, diagrams-as-code, drawio, flowchart, github-actions, graphql, image-to-diagram, kubernetes, mcp-server, protobuf, sysml, terraform, uml
saved: 2026-11-26
---

# agents365-ai-drawio-skill

A specialized architecture-as-code skill that converts natural language, source code, and infrastructure specifications into production-grade, editable `.drawio` architecture diagrams with support for incremental synchronization, multi-view projections, and contract validation.

## When to use

Use this skill when you need to:
- **Generate Architecture Diagrams**: Create structured `.drawio` diagrams from natural language descriptions, user stories, or RFCs.
- **Reverse-Engineer from Code & Specs**: Ingest Terraform modules, Kubernetes manifests, SQL DDL, OpenAPI, AsyncAPI, GraphQL, or Protobuf schemas and project them into visual components.
- **Maintain C4 Models & Multi-View Projections**: Generate and align Context, Container, Component, and Deployment views from a single underlying architectural model.
- **Incrementally Sync Diagrams**: Update diagrams to reflect code or infrastructure changes without wiping out manual visual tweaks and customized positioning.
- **Validate Architecture Contracts**: Run topology checks, evaluate blast radiuses, analyze failure propagation paths, and enforce architectural rules in CI/CD pipelines.
- **Export and Embed**: Convert `.drawio` XML into SVG, PNG, or PDF representations for documentation and pull request previews.

## How to use

The skill provides integration scripts and CLI utilities (such as `diagram_helper.py`) to parse, generate, and synchronize diagrams.

### 1. Generate a Diagram from Natural Language or Specification

Use `diagram_helper.py` to parse an architecture description or input specification into `.drawio` format:

```bash
# Generate from a textual description or architecture prompt
python diagram_helper.py generate \
  --input "Three-tier web app on AWS with ALB, ECS Fargate, Aurora Postgres, and ElastiCache" \
  --output ./docs/architecture.drawio \
  --style modern \
  --model c4-container
```

### 2. Ingest Infrastructure and Schema Sources

Parse infrastructure definitions (Terraform, Kubernetes) or API schemas directly:

```bash
# Ingest Terraform configuration
python diagram_helper.py ingest \
  --type terraform \
  --source ./terraform/environments/prod \
  --output ./docs/infra-deployment.drawio

# Ingest OpenAPI and SQL schemas into a component model
python diagram_helper.py ingest \
  --type openapi \
  --source ./api/openapi.yaml \
  --output ./docs/api-contracts.drawio
```

### 3. Incremental Synchronization

Update an existing `.drawio` file with new services or connections while preserving node coordinates and manual layout:

```bash
python diagram_helper.py sync \
  --existing ./docs/architecture.drawio \
  --source ./k8s/manifests/ \
  --output ./docs/architecture.drawio \
  --preserve-positions
```

### 4. Architecture Validation and Blast Radius Analysis

Audit an existing diagram model against constraints or analyze impact:

```bash
# Validate compliance rules (e.g., prevent direct database access from public tier)
python diagram_helper.py validate \
  --diagram ./docs/architecture.drawio \
  --rules ./rules/architecture-rules.yaml

# Simulate blast radius for a service failure
python diagram_helper.py simulate-failure \
  --diagram ./docs/architecture.drawio \
  --failed-node "PaymentGatewayService"
```

### 5. Export to Vector/Raster Images

Render editable `.drawio` files to documentation-ready formats:

```bash
python diagram_helper.py export \
  --input ./docs/architecture.drawio \
  --format svg \
  --output ./docs/architecture.svg
```

## Limitations

- **Headless Export Dependencies**: Exporting to raster/vector formats (PNG/PDF/SVG) requires local rendering engines or headless Draw.io CLI / browser binaries installed in the environment.
- **Extreme Scale Constraints**: Topologies with thousands of interconnected nodes can become visually dense; these require partitioning into modular C4 views or hierarchical sub-diagrams.
- **Static vs. Dynamic Realities**: Static extraction from IaC and API schemas reflects declared infrastructure and interfaces, not transient runtime states or dynamic service mesh routes.
- **Semantic Heuristics**: Automated visual grouping (e.g., trust boundaries, security zones) depends on standard naming conventions or explicit tagging in source definitions.