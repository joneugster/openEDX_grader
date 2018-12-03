""" Helper functions to do most common testings.

A tester function should return a dictionary or a list of dictionaries, each one
representing the output of one test case and with one of the
following formats:

{'correct': (bool), 'function': (str), 'result': (str), 'expected': (str)}
{'correct': False, 'error': (str)}
"""
import logging
import sys
import traceback


def function(fct=None, values=None, solution=None, expected=None):
    """Tests a function against a solution function or solution list.

    Arguments:
        fct (function): function to be tested
        values (list): list of test values.
                       Either like [(0,1), (2,4), ...] or [3, 4, 6, 9, ...]
                       In the former case we call `fct(*val)` for each
                       element, in the latter we call `fct(val)`
                       each `val` in this list.
        solution (function): function that returns the correct results
                                 when called `solution(val)`
        expected (list): List of expected output values.

    Note:
        You must specify either `solution` or `expected`.

    Returns:
        details (list): List of test results.
    """

    if solution is None and expected is None:
        logging.error('In `grading_tools.function` you must specify '
                      "one of 'solution' and 'expected'!")
        raise ValueError('Expected exactly one of the kwargs '
                         "'solution' or 'expected'.")
    elif solution is not None and expected is not None:
        logging.warning('In `grading_tools.function` you must only specify '
                        "one of 'solution' and 'expected'! "
                        "Ignoring 'expected'.")

    details = []
    for i, val in enumerate(values):
        # FIXME: This does certainly not work with all types of
        #        iterable inputs.
        try:
            iter(val)
        except TypeError:
            val = list(val)
        else:
            if isinstance(val, str):
                val = [val]

        out = dict()

        # Create test case info text
        out['function'] = '{}({})'.format(fct.__name__, ', '.join(
            "'{}'".format(v) if isinstance(v, str) else str(v) for v in val))

        # Get correct solution
        if solution is not None:
            out['expected'] = solution(*val)
        else:
            out['expected'] = expected[i]

        # Get student solution
        try:
            out['result'] = fct(*val)
        except Exception as err:                # pylint: disable=broad-except
            out['result'] = '{}: {}'.format(type(err).__name__, str(err))
            out['correct'] = False
        else:
            out['correct'] = bool(out['result'] == out['expected'])

        details.append(out)
    return details


def userinput(code, values, solution=None, expected=None):
    """Tests usercode with `input` and `print` against a solution.

    This is for student code that gets values with a single
    `input` statement and returns the result with print.

    Arguments:
        code (str): student code as string.
        values (list): list of test values, like [val1, val2, val3, ...]
                       When `input()` is called, it will return `str(val1)`.
        solution (function): function that returns the correct results
                             when called `solution(val1)`
        expected (list): List of expected output values.

    Note:
        You must specify either `solution` or `expected`.

    Returns:
        details (list): List of test results.
    """
    if solution is None and expected is None:
        logging.error('In `grading_tools.function` you must specify '
                      "one of 'solution' and 'expected'!")
        raise ValueError('Expected exactly one of the kwargs '
                         "'solution' or 'expected'.")
    elif solution is not None and expected is not None:
        logging.warning('In `grading_tools.function` you must only specify '
                        "one of 'solution' and 'expected'! "
                        "Ignoring 'expected'.")

    # overwrite builtin input function.
    class Input():                     # pylint: disable=too-few-public-methods
        """Overwriting standard input function."""
        def __init__(self, value):
            self.value = str(value)

        def __call__(self, msg=''):
            # calling `input()` inside the usercode will return `str(value)`.
            return self.value

    details = []
    for i, val in enumerate(values):
        # pylint: disable=redefined-builtin, possibly-unused-variable
        input = Input(val)

        # Create test case info text
        out = dict()
        out['function'] = 'Testing with input: {}'.format(val)

        # Get correct solution
        if solution is not None:
            out['expected'] = solution(val)
        else:
            out['expected'] = expected[i]

        # evaluate the user code.
        try:
            sys.stdout.truncate(0)
            exec(code, locals())                   # pylint: disable=exec-used
            # Note: sys.stdout will be redirected to a StringIO
            # pylint: disable=no-member
            out['result'] = sys.stdout.getvalue().strip('\u0000\n')
        except Exception:           # pylint: disable=broad-except
            out['error'] = traceback.format_exc(limit=0)
            out['correct'] = False
        else:
            out['correct'] = bool(out['result'] == out['expected'])
        details.append(out)
    return details
