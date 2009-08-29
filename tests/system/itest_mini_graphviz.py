import os
from hashlib import md5

import nose.tools as NT
import firepython.mini_graphviz as FM


HERE = os.path.dirname(os.path.abspath(__file__))
CLUSTERS_DOT = os.path.join(HERE, 'clusters.dot')
EXPECTED_MD5SUM = 'f889300cc5e22e860ba8e9c28864d1e2'


def test_mini_graphviz():
    mini_graphviz = FM.MiniGraphviz()
    mini_graphviz.viewer = ''
    out_png = mini_graphviz.view_as_png(CLUSTERS_DOT)

    md5sum = md5(open(out_png).read()).hexdigest()
    yield NT.assert_equal, EXPECTED_MD5SUM, md5sum

    os.remove(out_png)
