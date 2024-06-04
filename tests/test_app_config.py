from quartapp.app import create_app
from quartapp.config import AppConfig


def test_config():
    """test the AppConfig class"""
    app_config = AppConfig()
    assert not create_app(app_config=app_config).testing
    assert create_app(app_config=app_config, test_config={"TESTING": True}).testing
