import os
import json
from unittest.mock import patch
import requests


def test_docme(tmpdir, log_requests):
    with patch.dict('os.environ', {'DOCS_ROOT': tmpdir.strpath}):
        with log_requests('out'):
            r = requests.get('http://echo.jsontest.com/key/value/one/two')
            assert r.status_code == 200, r

    outfile = tmpdir.join('tests.test_log_requests.out.json')
    assert os.path.exists(outfile.strpath)

    data = json.loads(outfile.read())
    assert len(data) == 1, data
    data = data[0]
    assert data['method'] == 'get', data
    assert data['response_full'] == "{'key': 'value', 'one': 'two'}", data
