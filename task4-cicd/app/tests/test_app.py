import importlib.util
from pathlib import Path


APP_ENTRY = Path(__file__).resolve().parents[1] / "run.py"


def _load_main():
    spec = importlib.util.spec_from_file_location("run", APP_ENTRY)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_smoke():
    assert True


def test_app_exports():
    mod = _load_main()
    assert hasattr(mod, "app")


def test_flask_app_type():
    mod = _load_main()
    from flask import Flask
    assert isinstance(mod.app, Flask)
