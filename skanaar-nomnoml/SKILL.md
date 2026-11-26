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

# skanaar/nomnoml

Use this skill when the task involves: class-diagram, diagram, flowchart, nomnoml, uml.

- Code copy: `repo/` (licence file(s): LICENSE)
- Original README: `README_source.md`

## Summary from README
nomnoml [![npm version](https://badge.fury.io/js/nomnoml.svg)](https://badge.fury.io/js/nomnoml) [![Known Vulnerabilities](https://snyk.io/test/npm/nomnoml/badge.svg)](https://snyk.io/test/npm/nomnoml) [![web site](https://img.shields.io/badge/web-nomnoml.com-brightgreen)](https://www.nomnoml.com) ======= Hello, this is [nomnoml](http://www.nomnoml.com), a tool for drawing UML diagrams based on a simple syntax. It tries to keep its syntax visually as close as possible to the generated UML diagram without resorting to ASCII drawings. Created by [Daniel Kallin](https://github.com/skanaar) with help from a group of [contributors](https://github.com/skanaar/nomnoml/graphs/contributors). ## Library The [nomnoml](https://www.nomnoml.com) javascript library can render diagrams on your web page. The only dependency is [graphre](https://github.com/skanaar/graphre). Install nomnoml using either _npm_ or good old script inclusion. ## SVG output in NodeJS ``` npm install nomnoml ``` ```js var nomnoml = require('nomnoml') var src = '[nomnoml] is -> [awesome]' console.log(nomnoml.renderSvg(src)) ``` In the SVG output the node name is attached to SVG shapes and `` containers with `data-name` attribute. You can use this to implement interactive diagrams. ```js document.querySelector('svg').onclick = function (e) { console.log(e.target.closest('g[data-name]')?.attributes['data-name']) } ``` ## HTML Canvas rendering target ```html var canvas = document.getElementById('target-canvas') var [...]
