from quartapp.app import create_app


def test_config() -> None:
    """test the AppConfig class"""
    assert not create_app().testing
    assert create_app(test_config={"TESTING": True}).testing
