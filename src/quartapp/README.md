# Quart Backend API

This is a simple Quart API to handel requests coming from the frontend.

To install the application requirements, run these commands from the **repository root**:

```bash
uv venv .venv
source .venv/bin/activate
uv lock --directory src
uv sync --directory src --active --all-groups
```

> [!NOTE]
> This installs all dependencies including dev dependencies. The lockfile (`src/uv.lock`) ensures reproducible installs.
>

To start the application run inside the `src/` directory:

```bash
quart --app quartapp.app run -h localhost -p 50505
```
