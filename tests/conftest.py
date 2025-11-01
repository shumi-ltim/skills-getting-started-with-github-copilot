"""Configuration file for pytest"""

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test"
    )