"""
Problem name: EXAMPLE-001
Part of:      WEEK 0
Exercise:     Ask the user to input a time in seconds and print the time
              formatted as `H:M:S`.
              Example input from the user: `4928`
              Expected result: '1:22:8' (Note: not '1:22:08').
"""
import random
import grading_tools as gt


def check_raw(code):

    # Define a correct solution
    def solution(user_in):
        total_sec = int(user_in)
        hours = total_sec // 3600
        minutes = (total_sec // 60) % 60
        seconds = total_sec % 60
        return '{}:{}:{}'.format(hours, minutes, seconds)

    # Using 2 fixed and 18 random test values
    test_values = ['0', '1']
    while len(test_values) < 20:
        # Random magnitude and value for better distributed random values.
        new = str(int(random.random() * 10**(random.randint(0, 7))+1))
        if new not in test_values:
            test_values.append(new)

    # Compare code with solution
    return gt.userinput(code=code, values=test_values, solution=solution)
