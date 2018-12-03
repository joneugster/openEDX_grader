import logging
import sys, os
from grader import grade

def test_grader():
    name = 'TEST_001'

    code = """def f(x, y):\n    return x+y"""
    out = grade(name, code)
    logging.warning(out)
    assert out['correct']
    assert out['score'] == 1


    code = """def f(x,y):\n    print x+y"""
    out = grade(name, code)
    logging.warning(out)
    assert not out['correct']
    assert out['score'] == 0
