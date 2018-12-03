#!/usr/bin/env python3
"""Many thanks to the outstanding example written by Github user 'dagg'.
This code has been forked from the following repository:

    https://github.com/dagg/OpenEdxExternalGrader
    
Remark: No need to change anything here.
"""
import gc
import json
import logging
import os
import random
import re
import shutil
import subprocess
import sys
import time
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from json.decoder import JSONDecodeError
from socketserver import ThreadingMixIn

from setup_logging import setup_logging


class Handler(BaseHTTPRequestHandler):
    """Handle the basic communication with the XQueue."""
    # pylint: disable=invalid-name
    def do_HEAD(self):
        """."""
        pass
#         self.send_response(200)
#         self.send_header('Content-type', 'text/html')
#         self.end_headers()

    def do_GET(self):
        """Handling a normal GET request.

        This will be called if somebody enters the adress in his browser:
        http://gradermat101.math.uzh.ch:10101

        You can for example return some HTML.
        """
        with open('doc/Tutorial.html', 'br') as file:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(file.read())

    def do_POST(self):
        """This handles a POST request."""
        _time_start = time.time()
        body_len = int(self.headers['Content-Length'])
        _body = self.rfile.read(body_len).decode()
        logging.debug('Received content: %s', _body)
        try:
            body_content = json.loads(_body)
        except JSONDecodeError:
            logging.error('JSON: could not parse received content.')
#             result = process_result({'correct': False, 'error': 'Could not parse POST.'})
        else:

            problem_name, student_response, _user_id = get_info(body_content)

            # Grade the student response and format the results.
            logging.info('(%s) submitted code for problem %s.', _user_id, problem_name)
            result = grade(problem_name, student_response)

            logging.debug('Result: %s', result)

            _send = json.dumps(result).encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(_send)
            logging.info('answered (%s) in %f seconds.', _user_id, time.time()-_time_start)
            logging.debug('answer data: %s', _send)

    # Capture HTTP logging into our logging file.
    def log_message(self, format, *args):   # pylint: disable=redefined-builtin
        logging.debug(format, *args)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
        No further content needed, don't touch this. """


def grade(problem_name, student_response, do_processing=True):
    """
    Arguments:
        problem_name ():
        student_response (str): Str containing python code

    Keyword argument:
        do_processing (bool): return formatted text ready to send back.
                              If False, it will return the output from
                              the `check` function.
                              default: True

    Returns:
        result: (List of dict): dictionary or list of dictionaries.
                                Each dict is the result of one test
                                case and has the following form:
                                {'correct': True/False
                                 'function': Message/code to be
                                              displayed as input
                                 'result': Output of evaluation.
                                 'expected': Solution (only if correct==False)
                                }
    """
    try:
        randfilename = randgen()

        # Create tmp directory if it does not exist
        if not os.path.exists('tmp'):
            logging.warning('Creating new directory ./tmp')
            os.makedirs('tmp')

        # Create python file to be tested from student's submitted program
        student_program = 'Program{}_{}'.format(problem_name, randfilename)
        source_file = open('tmp/{}.py'.format(student_program), 'w')
    
    
#         student_code = re.sub(r'(?<!\\)\t+', '    ', student_code)
    
        source_file.write(student_response)
        source_file.close()

        # Use pytest to test the student's submitted program with the
        # help of the appropriate test runner

        # When called with systemd we need absolute paths, so I
        # entered it here.
        
        # FIXME: This is very hacky. On the executing machine, we need absolute path, on thinlinc `python3`
        # and on modern devices propably `python`
        
        if os.path.exists('/opt/anaconda/anaconda3/bin/python'):
        
            _path = '/opt/anaconda/anaconda3/bin/python'
        elif shutil.which('python3') is not None:
            _path = 'python3'
        else:
            _path = 'python'
            

        process = subprocess.Popen([_path,
                                    'testrunner.py',
                                    problem_name, student_program],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

        _timeout = 20
        try:
            out, err = process.communicate(timeout=_timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            res = {'correct':False, 'error': 'Timeout: Evaluation aborded after '
                                             '{} seconds (Check for infinite '
                                             'loops)'.format(_timeout)}

        else:
            logging.debug('testrunner qutput:\n%s', out.decode())
            if err:
                logging.warning('testrunner crashed: %s', _wrap(err.decode()))
                #logging.debug('testrunner quit with error:\n%s', err.decode())
                res = {'correct':False, 'error':err.decode()}
            else:
                if isinstance(out, bytes):
                    out = out.decode('utf-8')
                try:
                    res = json.loads(out)

                except JSONDecodeError:
                    logging.error(_wrap(traceback.format_exc()))
                    res = {'correct':False, 'error': 'There was an error evaluating your code! Check your Syntax.'}

            # remove student's program from disk
            os.remove('tmp/{}.py'.format(student_program))

        # garbage collect, TODO: why do we need that?
        gc.collect()

    except Exception:
        logging.error(_wrap(traceback.format_exc()))
        res = {'correct':False, 'error': 'There seems to be a System error :('}          
    
    logging.debug('processing output...')
    
    if do_processing:
        return process_result(res)
    return res


def process_result(result):
    """ Take a list of test results and create xqueue response.

    The test results will be formatted with HTML.

    Arguments:
        result (list): List of test cases, each test case is a dict.
                       A test case dict is of either of the following forms:
                       {'correct': (bool), 'function': (str),
                        'result': (str), 'expected': (str)}
                       or
                       {'correct': False, 'error': (str)}
                       where we have
                       correct (bool): result
                       function (str): Explains what has been tested.
                       result (str): output of the student's code
                       expected (str): correct result.
                       error (str): Error message of error that did not allow
                                    to do the test (SyntaxError, NameError, ...)

    Returns:
        msg (byte): json dump of xqueue response. This contains a dict
                    {'correct': (bool), 'score': (float), 'msg': (str)}
                    with
                    correct (bool): overall result
                    score (float): between 0 and 1.
                    msg (str): HTML formatted test results
    """

    _start = """
<div class="test">
<header>Test results</header>
  <section>
    <div class="shortform">
      {}
      <a href="#" class="full full-top">See full output</a>
      <a href="#" class="full full-bottom">See full output</a>
    </div>
    <div class="longform" style="display: none;">"""

    _end = """
    </div>
  </section>
</div>"""

    _correct = """
      <div class="result-output result-correct">
        <h4>{header}</h4>
        <pre>{function}</pre>
        <dl>
          <dt>Output:</dt>
          <dd class="result-actual-output"><pre>{result}</pre></dd>
        </dl>
      </div>"""

    _wrong = """
      <div class="result-output result-incorrect">
        <h4>{header}</h4>
        <pre>{function}</pre>
        <dl>
          <dt>Your output:</dt>
          <dd class="result-actual-output"><pre>{result}</pre></dd>
          <dt>Correct output:</dt>
          <dd><pre>{expected}</pre></dd>
        </dl>
      </div>"""

    _fatal = """
      <div class="result-output result-incorrect">
        <h4>Error</h4>
        <dl>
          <dt>Message:</dt>
          <dd class="result-actual-output"><pre>{error}</pre></dd>
        </dl>
      </div>"""

    out = {}

    # Embed single grader results into a list
    if isinstance(result, dict):
        result = [result]
    
    logging.debug(result)
    logging.debug(type(result))  
    if not result:
        logging.warning('Empty result!')
        result = [{'correct':False, 'error': 'It seems like you crashed the evaluator.\n\n'
                                             'Please check if your code runs on your computer, '
                                             'and that you read the question correctly. '
                                             'Afterwards retry or contact the '
                                             'course staff, sorry :('}]

    # Correct if all tests passed
    n_correct = sum(r['correct'] for r in result)
    out['correct'] = (n_correct == len(result))

    # Percentage of score
    out['score'] = n_correct / len(result)


    # HTML formatted message
    # _start contains the header with the overall message and and links to
    # open a tab with the detailed results (_fatal/_correct/_wrong).
    if any(('error' in res) for res in result):
        msg = _start.format('ERROR')
    elif out['correct']:
        msg = _start.format('CORRECT')
    else:
        msg = _start.format('INCORRECT')

    # This middle part is hidden by default and shows detailed test results
    for i, res in enumerate(result):

        # Define defaults for all components
        answer = {'correct': False, 'function': '', 'result': '', 'expected': ''}
        answer.update(res)

        if 'error' in res:
            msg += _fatal.format(**answer)
        else:
            _name = 'Test Case {}'.format(i+1)
            if res['correct']:
                msg += _correct.format(header=_name, **answer)
            else:
                msg += _wrong.format(header=_name, **answer)
    # _end closes all opened html-tags
    msg += _end
    out['msg'] = msg

    return out


def get_info(json_object):
    """Parse xqueue input.

    Note: If you specify more parameters for the grader payload (in openEDX)
          you could extract them here (as we did with 'problem_name')

    Returns:
        problem_name (str): Unique identifier for the exercise.
        student_response (str): Python code from the student.
    """
    json_object = json.loads(json_object['xqueue_body'])
    grader_payload = json.loads(json_object['grader_payload'])
    student_response = json_object['student_response']
    _id = json.loads(json_object['student_info']).get('anonymous_student_id', 'unknown')
    return grader_payload['problem_name'], student_response, _id


def randgen():
    """Random file name generator."""
    return '_'.join([time.strftime('%Y%m%d%H%M%S'),
                     str(time.time()).split('.')[-1],
                     str(random.random()).split('.')[-1]])


def _wrap(msg):
    """Takes a string and wraps it in horizontal dashes."""
    return ('\n---------------------------------'
            '---------------------------------\n'
            '{}'
            '\n---------------------------------'
            '---------------------------------\n'.format(msg))


def start_grader(host='localhost', port=10101,
                 log_file='log/%Y/%m/%d/grader_%Y-%m-%dT%H%M.log'):
    # Set working directory
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

    setup_logging(logfile=time.strftime(log_file),
                  lvl_bash=logging.INFO, lvl_logfile=logging.INFO, symlink='log')

    # Start the server
    try:
        SERVER = ThreadedHTTPServer((host, port), Handler)
        logging.info('Starting grader on %s:%s...', host, port)
        SERVER.serve_forever()

    except KeyboardInterrupt:
        logging.info('Server shut down with ^C')


if __name__ == '__main__':
    start_grader()
