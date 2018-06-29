import json
import os
from contextlib import suppress, contextmanager
from pprint import pformat
from unittest.mock import patch
from urllib.parse import urlparse

import pytest


def gen_vprint(curr_level):
    def _inner(*args, level=1, **kwargs):
        if level <= curr_level:
            print(*args, **kwargs)
    return _inner


def vprint_func(*args, level=1, **kwargs):
    pass


@pytest.fixture(scope='session')
def vprint():
    yield vprint_func


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    verbose = config.getoption('verbose')
    if verbose:
        global vprint_func
        vprint_func = gen_vprint(verbose)


_set_fixtures = set()
_lvl = None


def pytest_fixture_setup(fixturedef, request):
    """
    loads fixtures in order: session => module => class => function
    """
    global _lvl
    if _lvl or fixturedef.scope == _lvl:
        return

    vprint_func('FDEF: {} {}'.format(fixturedef, request), level=4)
    skip_fixtures = set([request.fixturename, 'module_transaction', 'request', 'auto_transaction'])

    for scope in ['session', 'module', 'class', 'function']:
        _lvl = scope
        if fixturedef.scope == _lvl:
            vprint_func('Call => {}'.format(fixturedef), level=4)
            _lvl = None
            return

        for name in set(request.fixturenames) - skip_fixtures - _set_fixtures:
            if name == fixturedef.argname:
                vprint_func('Call => {}'.format(fixturedef), level=4)
                _set_fixtures.add(name)
                _lvl = None
                return

            assert name in request._arg2fixturedefs, \
                'There is no fixture `{}` in scope => {}'.format(name, request.node.nodeid)
            fdef = request._arg2fixturedefs[name][0]

            if fdef.scope == scope:
                vprint_func('CALL => : {} {}'.format(fdef, _set_fixtures), level=4)
                request.getfixturevalue(name)
                skip_fixtures.add(name)
    _set_fixtures.add(fixturedef.argname)
    _lvl = None


def pytest_fixture_post_finalizer(fixturedef):
    vprint_func('Discard: {}'.format(fixturedef), level=3)
    _set_fixtures.discard(fixturedef.argname)


def finish_unused_fixtures(item, nextitem):
    if not nextitem:
        return
    defs = item._fixtureinfo.name2fixturedefs

    skip_finishing = set(item.fixturenames) & set(nextitem.fixturenames)
    vprint_func('Skip finishing: {}'.format(skip_finishing), level=4)

    skip_fixtures = set(['request'])

    to_finish = set(item.fixturenames) - set(nextitem.fixturenames) - skip_fixtures
    for name in to_finish:
        # see: tests/nesting for test
        # fixes finishing of imported from one conftest into upper conftest
        for fdef in reversed(defs[name]):
            vprint_func('Finish fixture: {} {}'.format(name, fdef), level=4)
            fdef.finish(item._request)


def pytest_runtest_teardown(item, nextitem):
    finish_unused_fixtures(item, nextitem)


def tipsi_pformat(something):
    if isinstance(something, str):
        with suppress(Exception):
            something = json.loads(something)
    return pformat(something, indent=2)


@pytest.fixture
def log_requests(request):
    """
    read more in README.rst
    we don't force to install requests into project as a dependency
    if you're not using log_requests
    """
    import requests  # see docstring
    original_request = requests.sessions.Session.request
    records = []

    def _logreq(*args, **kwargs):
        nonlocal records
        response = original_request(*args, **kwargs)
        record = {
            'method': kwargs['method'],
            'path': urlparse(kwargs['url']).path,
            'query': kwargs.get('params', ''),
            'payload': tipsi_pformat(kwargs.get('json', kwargs.get('data'))),
            'status_code': response.status_code,
            'status_text': response.reason,
            'response_headers': repr(response.headers),
            'response_full': response.text,
            'response': tipsi_pformat(response.text),
        }
        records.append(record)
        return response

    @contextmanager
    def _ret(doc_path, items=slice(None)):
        nonlocal records
        with patch.object(requests.sessions.Session, 'request', _logreq):
            yield
        path = os.environ.get('DOCS_ROOT', './.doc')
        if not os.path.exists(path):
            os.mkdir(path)
        fname = os.path.join(path, '{}.{}.json'.format(request.function.__module__, doc_path))
        with open(fname, 'w') as f:
            json.dump(records[items], f)
        records = []
    yield _ret
