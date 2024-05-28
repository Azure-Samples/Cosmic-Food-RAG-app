python3 -m pip install --user --upgrade pip
python3 -m pip install -e 'src[dev]'
pre-commit install
cd ./frontend
nvm use 18
npm install && npm run build
cd ../
