from quartapp.app import create_app
from quartapp.config import AppConfig

app_config = AppConfig()
app = create_app(app_config=app_config)
