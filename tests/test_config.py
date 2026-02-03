from src.config import Settings


def _settings_fields():
    if hasattr(Settings, "model_fields"):
        return list(Settings.model_fields.keys())
    if hasattr(Settings, "__fields__"):
        return list(Settings.__fields__.keys())
    return []


def _settings_dict(settings):
    if hasattr(settings, "model_dump"):
        return settings.model_dump()
    return settings.dict()


def test_settings_loads():
    settings = Settings()
    field_names = _settings_fields()

    assert field_names
    data = _settings_dict(settings)
    for name in field_names:
        assert name in data
