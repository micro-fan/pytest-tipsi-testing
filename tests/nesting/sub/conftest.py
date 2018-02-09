import pytest

_globals = {}


@pytest.fixture(scope='module')
def finish_test():
    _globals['finish_test'] = True
    yield
    _globals['finish_test'] = False


@pytest.fixture
def ensure_finished():
    def _inner():
        assert _globals['finish_test'] == False
    yield _inner
