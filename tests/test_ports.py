from core.settings.ports import get_port

def test_get_port(): assert get_port('UI_FRONTEND', 7602) > 0 