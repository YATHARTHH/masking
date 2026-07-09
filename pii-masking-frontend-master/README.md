# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
})
```

---

<!-- DEVHUB-GITHOOKS:START (managed by rollout) -->
## Git Hooks & Pre-Commit Checks

This repo is pre-configured with the DevHub git hooks — every `git commit` is automatically scanned (gitleaks, detect-secrets, Semgrep, Ruff, Biome, terraform fmt, repo hygiene).

### First-time setup

Run **once** after cloning — installs the tools and activates the hooks:

**Windows (PowerShell):**
```powershell
.\tasks\mise-install.cmd
```

**macOS / Linux / Git Bash:**
```bash
bash tasks/mise-install.sh
```

> Run this **before committing** — until you do, your commits are blocked. If `mise` was just installed, open a new terminal first.

### Get the hooks into an existing branch

These hooks are merged into `main`/`master`. To pull them into a branch you already have, **rebase onto the latest `main` and re-run setup**:

```bash
git checkout main
git pull origin main
git checkout your-feature-branch
git rebase main
.\tasks\mise-install.cmd      # Windows  (bash tasks/mise-install.sh on macOS/Linux)
```

### Run the checks manually

```bash
mise scan
```

### Troubleshooting — hook ignored on macOS / Linux

If a commit goes through **without** the checks running, Git skipped the hook because it isn't executable:

```
hint: The '.githooks/pre-commit' hook was ignored because it's not set as executable.
```

Setup (`mise-install.sh`) marks the hooks executable, but if you still hit this, fix it manually — the executable bit is tracked by Git, so committing it keeps the gate working for everyone who clones:

```bash
chmod +x .githooks/*
git add .githooks/
git commit -m "chore: make git hooks executable"
```

Verify: `ls -la .githooks/` shows `-rwxr-xr-x`, and `git config core.hooksPath` prints `.githooks`.
<!-- DEVHUB-GITHOOKS:END -->

