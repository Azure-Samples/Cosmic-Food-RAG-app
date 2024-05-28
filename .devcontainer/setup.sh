python3 -m pip install --user --upgrade pip
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -e 'src[dev]'
pre-commit install
cd ./frontend
npm install && npm run build
cd ../
