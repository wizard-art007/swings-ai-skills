---
name: purocean-yn
description: A highly extensible Markdown editor featuring version control, AI Copilot, document annotations, mind maps, document encryption, executable code snippets, chart embedding, HTML applets, plugins, and m
source: https://github.com/purocean/yn
license: AGPL-3.0
stars: 6784
language: TypeScript
topics: agent, chatgpt, deepseek, drawio, editor, electron, gemini, koa2, markdown, markdown-editor, markdown-it, mermaid, monaco-editor, notebook, openai, opencode, plantuml, reveal-js, vscode, vue
saved: 2026-11-26
---

# Yank Note (purocean/yn)

Yank Note is an extensible Markdown editor built on Electron, Vue 3, Koa, and Monaco Editor. It combines local-first note-taking with IDE capabilities, including runnable code snippets, embedded diagrams (Draw.io, PlantUML, Mermaid), version history, client-side encryption, and multi-model AI Copilot/Agent integrations.

## When to use

- **Extending Yank Note**: Developing custom plugins, macros, themes, or custom Markdown renderers for Yank Note.
- **Integrating AI Assistants**: Adding or debugging LLM-assisted workflows (OpenAI, DeepSeek, Gemini, Ollama, OpenCode agent) inside a Monaco-based Markdown editor.
- **Embedding Interactive Media & Tools**: Building workflows that embed runnable code blocks (Node, Python, Bash), interactive HTML applets, Draw.io diagrams, or PlantUML schemas directly inside Markdown notes.
- **Investigating Electron + Monaco Architecture**: Studying hybrid desktop architecture using Monaco Editor with a local Koa backend and Vue frontend.

---

## How to use

### 1. Prerequisites and Setup

Clone the repository and install dependencies using Node.js (v18+ recommended):

```bash
git clone https://github.com/purocean/yn.git
cd yn
npm install
```

### 2. Development Commands

Run Yank Note in development mode:

```bash
# Run the renderer development server (Vue/Vite)
npm run dev

# Run the Electron main process in dev mode
npm run dev:electron

# Build web application bundle
npm run build

# Package Electron desktop application for the current platform
npm run package
```

### 3. Writing Custom Plugins

Yank Note provides an extension system exposed via the global `window.yanknote` object or plugin interface:

```typescript
// Example: Basic Yank Note Plugin structure
export default {
  name: 'my-custom-plugin',
  register(ctx: any) {
    // Add command to command palette
    ctx.commands.registerCommand({
      id: 'my-plugin.hello',
      name: 'Hello from Plugin',
      run: () => {
        ctx.ui.showToast('Plugin executed successfully!');
      }
    });

    // Register Markdown-it hook or Monaco action
    ctx.editor.registerAction({
      id: 'insert-timestamp',
      label: 'Insert Timestamp',
      run: (editor: any) => {
        const text = new Date().toISOString();
        editor.trigger('keyboard', 'type', { text });
      }
    });
  }
};
```

### 4. Running Code Snippets Inside Markdown

Yank Note allows executing code blocks directly within documents by annotating code fences:

````markdown
```bash:run
echo "Current directory:"
pwd
```

```python:run
import sys
print(f"Python version: {sys.version}")
```
````

---

## Limitations

- **Intentional Security Trade-offs**: Yank Note deliberately permits arbitrary command execution and local file read/write operations to support runnable code blocks, local shell integration, and custom extensions. **Do not run or preview untrusted Markdown files.**
- **Desktop Dependency**: Advanced system-level features (direct terminal execution, local file synchronization, external tool execution) rely on the Electron environment and local backend services; they may not function fully in web-only builds.
- **Resource Consumption**: The combination of Electron, Monaco Editor, and multiple embedded rendering engines (Mermaid, PlantUML, Draw.io) can lead to significant memory usage on large workspaces.
- **Licensing**: Licensed under AGPL-3.0, imposing strict copyleft requirements on derivative works and network-hosted variants.