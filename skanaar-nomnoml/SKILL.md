---
name: skanaar-nomnoml
description: The sassy UML diagram renderer
source: https://github.com/skanaar/nomnoml
license: MIT
stars: 2842
language: TypeScript
topics: class-diagram, diagram, flowchart, nomnoml, uml
saved: 2026-11-26
---

# skanaar-nomnoml

Nomnoml is a tool and JavaScript library for rendering simple, text-driven UML diagrams, flowcharts, and architecture models without relying on heavy visual editors or verbose XML/JSON formats.

## When to use

Use this skill when you need to:
- Generate SVG or Canvas UML class diagrams, sequence flows, or state diagrams from simple text syntax.
- Render diagrams dynamically within Node.js, browser applications, or automated pipelines.
- Integrate text-based diagramming into web interfaces with clickable SVG shapes via `data-name` attributes.
- Use command-line utilities or Python helpers (`nomnoml_helper.py`) to compile `.nomnoml` files into SVG images.

## How to use

### 1. Command Line Interface (CLI)

Generate SVG diagrams directly from `.nomnoml` files:

```bash
npx nomnoml input.nomnoml output.svg
```

### 2. Node.js API (SVG Rendering)

Install the library:
```bash
npm install nomnoml
```

Render diagram source code to an SVG string:
```javascript
const nomnoml = require('nomnoml');

const source = `
#direction: right
[<package> System |
  [User] -> [Frontend]
  [Frontend] -> [API Gateway]
  [API Gateway] -> [<database> Database]
]
`;

const svgContent = nomnoml.renderSvg(source);
console.log(svgContent);
```

### 3. Web / HTML Canvas Target

Render directly onto an HTML5 `<canvas>` element:

```html
<canvas id="target-canvas"></canvas>
<script src="node_modules/graphre/dist/graphre.js"></script>
<script src="node_modules/nomnoml/dist/nomnoml.js"></script>
<script>
  var canvas = document.getElementById('target-canvas');
  var source = '[Customer] -> [Order]';
  nomnoml.draw(canvas, source);
</script>
```

### 4. Interactivity via SVG attributes

Elements in the generated SVG are tagged with `data-name` attributes corresponding to the node labels:

```javascript
document.querySelector('svg').onclick = function (e) {
  const nodeName = e.target.closest('g[data-name]')?.getAttribute('data-name');
  if (nodeName) {
    console.log('Clicked node:', nodeName);
  }
};
```

### 5. Using Python Helper (`nomnoml_helper.py`)

Run the local wrapper script to compile nomnoml syntax programmatically within Python scripts or pipelines.

## Limitations

- **Complex Layout Control**: Relies on the internal layout engine (`graphre`), which does not offer fine-grained manual node positioning compared to tools like Graphviz (dot).
- **Styling Customization**: Custom visual styles are restricted to supported directives (e.g., `#fill`, `#stroke`, `#direction`, `#fontSize`); arbitrary CSS styles on individual nested elements require post-processing.
- **Large Diagram Scaling**: Large diagrams with dozens of nodes and complex multi-directional relations can become hard to read due to automatic edge routing limits.
- **Standard UML Coverage**: Designed for concise visual representation rather than full, strict compliance with official UML 2.x specifications.