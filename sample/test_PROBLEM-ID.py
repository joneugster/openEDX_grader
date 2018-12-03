"""
A test case must be named "test_..." and should test the grader for typical
user input.

You can always use:

    out = grade(name, code)
    or
    out = grade(name, code, do_processing=False)
    
The first one will return a dict. of the form
{'correct': (bool), 'score': (float), 'msg': (HTML formatted str)}
with 'score' in [0,1] and 'msg' the message that will be displayed in openEDX.

The second option returns a dict or list of dicts as you output
it in `check_PROBLEM-ID.py`.
Concretely this is of the form
{'correct': (bool), 'function': (str), 'result': (str), 'expected': (str)}
or
{'correct': False, 'error': (str)}
or
list of such dicts.
"""
import logging
from grader import grade

def test_PROBLEM_ID():
    """
    Problem name: PROBLEM-ID    # This name must be put in the openEDX problem.
    Part of:      WEEK 0
    Exercise:     <Put a short task description here>
    """
    id = 'PROBLEM-ID'

    # Assert, the sample solution is accepted as correct
    code = """def add(x,y):\n    return x+y"""
    out = grade(id, code)
    logging.warning(out)       # pytest will display warnings if assert fails.
    assert out['correct']

    # Assert some common errors are recognized
    code = """def add(x,y):\n    return x-y"""
    out = grade(id, code)
    logging.warning(out)
    assert not out['correct']

    code = """def f(x,y):\n    return x+y"""
    out = grade(id, code)
    logging.warning(out)
    assert not out['correct']
