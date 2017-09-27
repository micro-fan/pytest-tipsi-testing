import pytest


_session = False
_module = False
_function = False


@pytest.fixture(scope='session')
def session_fixture():
    global _session
    _session = True
    assert not _module
    assert not _function
    yield
    # TODO: fix shutdown order
    # assert not _module
    # assert not _function
    _session = False


@pytest.fixture(scope='module')
def module_fixture():
    global _module
    _module = True
    assert _session
    assert not _function
    yield
    # TODO: fix shutdown order
    # assert not _function
    # assert _session
    _module = False


@pytest.fixture(scope='function')
def function_fixture():
    global _function
    _function = True
    assert _session
    assert _module
    yield
    # TODO: fix shutdown order
    # assert _session
    # assert _module
    _function = False


def test_1(function_fixture, module_fixture, session_fixture):
    pass
