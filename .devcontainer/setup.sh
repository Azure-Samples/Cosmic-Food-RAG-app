curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv venv .venv && source .venv/bin/activate
uv lock --directory src
uv sync --directory src --active --all-groups
uv tool install pre-commit
pre-commit install
cd ./frontend
npm install && npm run build
cd ../
