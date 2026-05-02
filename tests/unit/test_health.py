from backend.app.main import app


def test_app_metadata() -> None:
    assert app.title == "Zhuotuan Backend"
