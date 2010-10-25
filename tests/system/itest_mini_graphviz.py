import os
from hashlib import md5

from nose import SkipTest
import nose.tools as NT
import firepython.mini_graphviz as FM


HERE = os.path.dirname(os.path.abspath(__file__))
CLUSTERS_DOT = os.path.join(HERE, 'clusters.dot')
EXPECTED_MD5SUM = 'f889300cc5e22e860ba8e9c28864d1e2'
EXPECTED_MD5SUM_MAC = 'a4925b08632f65aceac09d903a6aa2c5'

def test_mini_graphviz():
    if os.name != 'posix':
        def raiser(exc, msg):
            raise exc(msg)
        yield raiser, SkipTest, 'mini graphviz helper is very much geared ' \
                                'toward linux as it makes use of the `dot` ' \
                                'and `eog` binaries by default'
        raise StopIteration
    mini_graphviz = FM.MiniGraphviz()
    mini_graphviz.viewer = ''
    out_png = mini_graphviz.view_as_png(CLUSTERS_DOT)

    md5sum = md5(open(out_png).read()).hexdigest()
    yield NT.assert_true, EXPECTED_MD5SUM==md5sum or EXPECTED_MD5SUM_MAC==md5sum, 'MD5 sum match'

    os.remove(out_png)
