from tools.ui_audit import allowed_url
def test_loopback_only():
    assert allowed_url("http://localhost:8000/")
    assert allowed_url("http://127.0.0.1:8000/")
    assert not allowed_url("https://example.com")
    assert not allowed_url("http://169.254.169.254/")
    assert not allowed_url("file:///etc/passwd")
    assert not allowed_url("http://user:pass@localhost:8000")
