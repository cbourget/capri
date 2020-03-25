import pytest

from capri.core.app import App


@pytest.fixture(scope='session')
def settings():
    return {}


@pytest.fixture(scope='function')
def app(settings):
    return App(settings)
