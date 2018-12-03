"""
Tests for: EXAMPLE-001
Part of:   WEEK 0
"""
import logging
from grader import grade


def test_EXAMPLE_001():
    """
    Problem name: EXAMPLE-001
    Part of:      WEEK 0
    Exercise:     Ask the user to input a time in seconds and print
                  the time formatted as `H:M:S``.
                  Example input from the user: `4928`
                  Expected result: '1:22:8' (Note: not '1:22:08')
    """
    # Specify problem ID
    id = 'EXAMPLE-001'

    # Assert, the sample solution is accepted as correct
    code = """
user_in = input('Please enter an integer number of seconds: ')
total_sec = int(user_in)
hours = total_sec // 3600
minutes = (total_sec // 60) % 60
seconds = total_sec % 60
print('{}:{}:{}'.format(hours, minutes, seconds))
"""
    out = grade(id, code)
    logging.warning(out)       # pytest will display warnings if assert fails.
    assert out['correct']


