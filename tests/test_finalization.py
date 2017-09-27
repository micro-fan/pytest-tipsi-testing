import pytest


A = None
B = None
C = None


@pytest.fixture(scope='session')
def fixture_a():
    global A
    A = True
    yield
    A = False


@pytest.fixture(scope='session')
def fixture_b():
    global B
    B = True
    yield
    B = False


@pytest.fixture(scope='session')
def fixture_c():
    global C
    C = True
    yield
    C = False


def test_a(fixture_a):
    assert A
    assert not B
    assert not C


def test_b(fixture_b):
    assert not A
    assert B
    assert not C


def test_c(fixture_c):
    assert not A
    assert not B
    assert C


def test_ab(fixture_a, fixture_b):
    assert A
    assert B
    assert not C


def test_bc(fixture_b, fixture_c):
    assert not A
    assert B
    assert C


def test_ac(fixture_a, fixture_c):
    assert A
    assert not B
    assert C
