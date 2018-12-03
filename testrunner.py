"""Imports the student code and the solution test runner as modules.
The solution tests must be in the folder 'solution' saved with the
name 'check_{}.py' where {} is the unique exercise identifier specified
on openEDX (in the grader-payload). The file must contain a function
def check(code, stdout=None, stderr=None):
    ...
    return result
which takes the loaded module with the student code and returns a list of
dictionaries representing all test cases. Each dictionary must have one
of the following formats:
{'correct': (bool), 'func_call': (str), 'user_out': (str), 'exp_out': (str)}
{'correct': False, 'error': (str)}
stdout and stderr are StringIO() objects and contain the output at
sys.stdout and sys.stderr while evaluating the code. You can access the content
at any time with `stdout.getvalue()`.

Remark: No need to change anything here.
"""
import importlib
import sys
import json
import re
import traceback
from io import StringIO

# Compatibility with verwsions below 3.6
if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and
                               sys.version_info[1] < 6):
    ModuleNotFoundError = ImportError


class RedirectedOutput:         # pylint: disable=too-few-public-methods
    """Redirect stdout and stderr into string variables."""
    def __enter__(self):
        """Redirect stdout and stderr into string variables.
        Returns:
            student_stdout (StringIO): Redirected stdout
            student_stderr (StringIO): Redirected stderr
        """
        student_stdout = StringIO()
        student_stderr = StringIO()
        sys.stdout = student_stdout
        sys.stderr = student_stderr
        return (student_stdout, student_stderr)
    def __exit__(self, *args):
        """Set stdout and stderr back to default value."""
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


def main():
    with RedirectedOutput():
        # Load solution
        problem = str(sys.argv[1])
        try:
            sol = importlib.import_module('solutions.check_{}'.format(problem))
        except ModuleNotFoundError:
            result = {'correct': False, 'error': 'There is no solution '
                                                 'available for this problem '
                                                 '(key: {})'.format(problem)}
            return result

        # We need a big try-block because student errors can raise Either
        # in teh line with `import_module` or in the line where we
        # execute the code with `grading_fct(code)`.
        try:
            # import the usercode
            # Either as module or as string
            # (string: usable for redirecting `input` before evaluating)
            user_file = str(sys.argv[2]).split('.')[0]
            if hasattr(sol, 'check_raw'):
                grading_fct = sol.check_raw
                with open(('tmp/{}.py'.format(user_file)), 'r') as f:
                    code = f.read()
            elif hasattr(sol, 'check'):
                grading_fct = sol.check
                try:
                    code = importlib.import_module('tmp.{}'.format(user_file))
                # Handling errors during import of student code
                except ModuleNotFoundError:
                    # This shouldn't happen under normal conditions...
                    result = {'correct': False,
                              'error': 'There has been a problem with '
                                       'loading your code for evaluation. '
                                       'Please try again.'}
                    return result
            else:
                # Should not happen unless the instructors are careless.
                result = {'correct': False,
                          'error': 'It seems that the solution for this problem '
                                   '(key: {}) is not set up correctly. '
                                   'Please contact the '
                                   'course staff.'.format(problem)}
                return result

            # Call the grading function.
            result = grading_fct(code)

        except EOFError:
            result = {'correct': False,
                      'error': 'EOFError: Your code contains too '
                               'many `input()` statements.\n'
                               'Make sure you answered the question '
                               'correctly and you did not add '
                               'more `input()` statements than '
                               'required.'}

        except SyntaxError as err:
            _msg = traceback.format_exc(limit=0)
            # Replace filename in syntax error message
            _msg = re.sub('(?<=File ")[^"]*', 'StudentCode', _msg)
            result = {'correct': False, 'error': _msg}

        except BaseException:       #pylint: disable=broad-except
            # Unhandled exceptions
            result = {'correct': False,
                      'error': traceback.format_exc(limit=0)}
        return result


if __name__ == '__main__':
    # pylint: disable=invalid-name
    # Return the result. We print it so that the grader.py can read it
    # from stdout. During execution stdout and stderr have been redirected,
    # so that this should be the only thing printed.
    result = main()
    print(json.dumps(result))
