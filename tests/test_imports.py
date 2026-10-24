def test_config_import():
    import app.config
    assert app.config.DATA_DIR.exists()

def test_desktop_import():
    from app.tools.desktop import launcher
    assert launcher is not None
