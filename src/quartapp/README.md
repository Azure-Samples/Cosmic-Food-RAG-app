# Quart Backend API

This is a simple Quart API to handel requests coming from the frontend.

To install the application requirements run this command inside the `src/` directory:

```bash
pip install -e .
```

> [!NOTE]
> To install the development dependencies you need to use the following command:
>
> ```bash
> pip install -e '.[dev]'
> ```
>

To start the application run inside the `src/` directory:

```bash
quart --app quartapp.app run -h localhost -p 50505
```
