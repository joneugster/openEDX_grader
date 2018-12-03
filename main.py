"""Script to start the grader.

Note: if your behind a router you might want to put the local IP here
      and not the global one.

Logs: If you want to save the log somewhere different, provide
      keyword argument 'log_file'.
      (Default is 'log/%Y/%m/%d/grader_%Y-%m-%dT%H%M.log' and the string
      will be processed by `time.strftime`)
"""
from grader import start_grader
start_grader(host='localhost', port=10101)

