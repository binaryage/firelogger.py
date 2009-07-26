import nose.tools as NT
import mock

import firepython as FPY
import firepython.utils as FU


def test_tolerant_json_encoder_strs_on_default():
    encoder = FU.TolerantJSONEncoder()
    yield NT.assert_equal, "{'ho': 'hum'}", encoder.default({'ho': 'hum'})
    yield NT.assert_equal, '[9, 8, 7, 6]', encoder.default([9, 8, 7, 6])


def test_json_encode():
    real_json = FU.json
    FU.json = mock.Mock()
    FU.json.dumps = mock.Mock()

    in_data = {'foo': 'bar', 'ham': 9000}
    FU.json_encode(in_data)
    yield NT.assert_equal, [((in_data,), dict(cls=FU.TolerantJSONEncoder))], \
                           FU.json.dumps.call_args_list

    FU.json = real_json


def test_get_version_header():
    ret = FU.get_version_header('bork')
    yield NT.assert_equal, EXPECTED_VERSION_HEADER, ret


def test_get_auth_token():
    ret = FU.get_auth_token('fashizzle')
    yield NT.assert_equal, EXPECTED_AUTH_TOK, ret


EXPECTED_VERSION_HEADER = (FPY.FIRELOGGER_VERSION_HEADER, 'bork')
EXPECTED_AUTH_TOK = 'c5d00db3f939c1cc523f57d67e5cc319'
