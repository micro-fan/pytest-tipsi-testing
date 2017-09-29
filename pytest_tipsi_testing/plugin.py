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


_set_fixtures = set()
_lvl = None


def pytest_fixture_setup(fixturedef, request):
    """
    loads fixtures in order: session => module => class => function
    """
    global _lvl
    if _lvl or fixturedef.scope == _lvl:
        return

    print('FDEF: {} {}'.format(fixturedef, request))
    skip_fixtures = set([request.fixturename, 'module_transaction', 'request', 'auto_transaction'])

    for scope in ['session', 'module', 'class', 'function']:
        _lvl = scope
        if fixturedef.scope == _lvl:
            print('Call => {}'.format(fixturedef))
            _lvl = None
            return

        for name in set(request.fixturenames) - skip_fixtures - _set_fixtures:
            if name == fixturedef.argname:
                print('Call => {}'.format(fixturedef))
                _set_fixtures.add(name)
                _lvl = None
                return

            fdef = request._arg2fixturedefs[name][0]

            if fdef.scope == scope:
                print('CALL => : {} {}'.format(fdef, _set_fixtures))
                request.getfixturevalue(name)
                skip_fixtures.add(name)
    _set_fixtures.add(fixturedef.argname)
    _lvl = None


def pytest_fixture_post_finalizer(fixturedef):
    print('Descard: {}'.format(fixturedef))
    _set_fixtures.discard(fixturedef.argname)


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
