import pytest


def vprint_func(*args, **kwargs):
    pass


@pytest.fixture(scope='session')
def vprint():
    yield vprint_func


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    verbose = config.getoption('verbose')
    if verbose:
        global vprint_func
        vprint_func = print


@pytest.fixture(autouse=True)
def load_fixtures_by_scope(request):
    """
    loads fixtures in order: session => module => class => function
    """
    skip_fixtures = set([request.fixturename, 'module_transaction', 'request'])
    for scope in ['session', 'module', 'class', 'function']:
        for name in set(request.fixturenames) - skip_fixtures:
            fdef = request._arg2fixturedefs[name][0]
            if fdef.scope == scope:
                request.getfixturevalue(name)
                skip_fixtures.add(name)


def finish_unused_fixtures(item, nextitem):
    if not nextitem:
        return
    defs = item._fixtureinfo.name2fixturedefs

    skip_finishing = set(item.fixturenames) & set(nextitem.fixturenames)
    vprint_func('Skip finishing: {}'.format(skip_finishing))

    to_finish = set(item.fixturenames) - set(nextitem.fixturenames)
    for name in to_finish:
        fdef = defs[name][0]
        vprint_func('Finish fixture: {}'.format(name))
        fdef.finish()


def pytest_runtest_teardown(item, nextitem):
    finish_unused_fixtures(item, nextitem)
