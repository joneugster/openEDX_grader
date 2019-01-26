# openEDX External Grader in Python
(This is not in any way affiliated to openEDX or EDX. Just a student hack)

A simple openEDX external grader to correct Python code.
Download the code to your grading server, edit host and port in `main.py` and run `python main.py`
(See more under [How to use this code](#usage)).

## Table of Contents
1. [Security warning](#security)
1. [Description](#description)  
1. [How to use this code](#usage)
   1. [Run server](#run-server)
   1. [Add exercise](#add-exercise)
1. [Detailed description](#doc)
   1. [Solution checker](#solutions)  
   1. [Testing your code](#tests)  
   1. [OpenEDX exercises](#advanced-blank-problem)  
   1. [Setting up the XQueue](#xqueue)  
   1. [Setting up the grader on Linux](#set-up-grader)  

<a name="security"/>

## Security Warning
This project does not make any attempt to make the evaluation secure!

Any submitted Python code will be executed without any checks. This means all system commands can be called and one can even read the expected solution. Therefore, **it is not recommended to use it for exams or exercises that count towards the final grade.**

One way to reduce these security problems is to run the code inside a virtual machine, use a user with limited rights and use `systemctl` to automatically restart it on a crash.


<a name="description"/>

## Description

This is an external grader that makes it possible to automatically evaluate Python code from students in openEDX.

You can create coding exercises with an input field:
![Example exercise](doc/images/unanswered_problem.png "Example exercise")

The student can then write their code, submit it and receive feedbac and points. This score can also be displayed in the Progress tab of openEDX.
![Solved example exercise](doc/images/answered_problem.png "Solved example exercise")

By clicking on "See full output" the student can see all test cases to figure out what was wrong with their code.
![Feedback per test case](doc/images/test_cases.png "Possible test cases")

<a name="usage"/>

## How to use this code
You have to setup this grader on a server with an open port and specify this address as X-Queue in the openEDX installation. (More on that later)

<a name="run-server"/>

### To run this server:
1. Setup the XQueue in the openEDX installation (see later)
1. Change 'host' and 'port' inside `main.py`
1. run `python main.py`

<a name="add-exercise"/>

### To add new exercises:

#### In the openEDX course
1. Copy the template from `sample/EDX_problem.txt` into a 'Blank Advanced Problem' in your openEDX course.
1. Change the problem ID in `"problem_name": "PROBLEM-ID"` to a unique identifier.
1. Change `QUEUENAME` to your XQueue's name.
1. Replace `TASK DESCRIPTION` with HTML formatted text describing the exercise.
1. Optionally, add a sample solution inside the `<answer_display>` tag.
1. You can define at which point the students should see the answer of the problem by changing "Edit > Settings > Show Answer" or by changing the default value under "Settings > Advanced Settings > Show Answer".
#### On the grading server
1. Create a file `solutions/check_PROBLEM-ID.py` where you change `PROBLEM-ID` to the exercise's unique identifier. (Use the template `sample/check_PROBLEM-ID.py`)
1. Copy `sample/test_PROBLEM-ID.py` to `tests/test_PROBLEM-ID.py` and add some basic tests. This is not mandatory but it is recommended to add at least a test where you test if it works with correct solution to catch things like syntax errors.
1. Run `run_pytest` to check that everything works
1. Restart grader with `python main.py`

<a name="doc"/>

## Detailed description


<a name="solutions"/>

### Solution checker
This section explains the files like `solutions/check_PROBLEM-ID.py` in more details.

Those files contains the solutions to a problem. it is important that the filename is as in the example, whiet `PROBLEM-ID` replaced by a unique identifier you have to write into the openEDX-exercise.

The file contains one of two possible functions, either `check(code)` or `check_raw(code)`.

`check` takes the code as imported module, which means you can access a function `f` defined by the student as `code.f`, `check_raw` takes the code as string and you have to evaluate it manually. This is useful if the code contains plain `input()` statements.

Both functions should return a list of dictionaries, each dict. representing one test case. For example

```Python
[{'correct': True,  'function': 'fct(1)',
  'result': '1', 'expected': '1'},
 {'correct': True,  'function': 'fct(2)',
  'result': '0.5', 'expected': '0.5'},
 {'correct': False, 'function': 'fct(3)',
  'result': '4', 'expected': '0.3'},
 {'correct': False,
  'error': 'ZeroDivisionError'}]
```

These test cases will then be displayed as in the image above.
You can use the functions from `grading_tools.py` to automate it a bit or you can create your own tests.

<a name="tests"/>

### Testing your code

run the tests by running the bash-script `run_tests`.
You should add tests for all solutions. The simplest possible test looks something like this:

```Python
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
    id = 'EXAMPLE-001'

    # Correct solution
    code = '\n'.join(
      "user_in = input('Please enter an integer number of seconds: ')",
      "total_sec = int(user_in)",
      "hours = total_sec // 3600",
      "minutes = (total_sec // 60) % 60",
      "seconds = total_sec % 60",
      "print('{}:{}:{}'.format(hours, minutes, seconds))")

    out = grade(id, code)
    assert out['correct']
```

<a name="advanced-blank-problem"/>

### OpenEDX exercises
This section explains how to setup your exercise in the openEDX course.

Create a new Unit, then select to add a "Blank Advanced Problem" and copy the sample code from `sample/EDX_problem.txt` into it:

```HTML
<problem>
  <coderesponse queuename="QUEUENAME">

    <label>TASK DESCRIPTION</label>

    <textbox rows="10" cols="80" mode="python" tabsize="4"/>
    <codeparam>
      <initial_display>
# Please write your program here
</initial_display>
      <answer_display>
# There is no solution available at the moment.
# Please ask one of the course assistants.
      </answer_display>
      <grader_payload>
        {"problem_name": "PROBLEM-ID"}
      </grader_payload>
    </codeparam>
  </coderesponse>
</problem>
```

You have to change `PROBLEM-ID` to the one used in the solution and `QUEUENAME` to the xQueue name of your server.

You can add a sample solution inside the `<answer_display>` tag and some pre-written code for the student inside the `<initial_display>` tag, for example you could already provide a class framework and they'd only need to fill in certain parts.

The `TASK DESCRIPTION` can be HTML-formatted text.

<a name="xqueue"/>

### Setting up the XQueue
This needs to be done by the system admin managing the openEDX installation. They need the host & port your grader will be running on.

*coming soon*

<a name="set-up-grader"/>

### Setting up the grader on a linux machine
Here I describe what I did to set it up on a Ubuntu 16.04 LTS, maybe this is a helpful reference. This might be incomplete and it was kind of weirdly set up, but maybe it helps to some extend.

#### 1. Set up the VM with an open port
Set up a VM with Ubuntu and check with the system admin, that there is a port, that is not blocked by the Firewall. The public address and port must be specified in `main.py`.

#### 2. Create new users
I created one user `grader` which will be used for git and a user `executor` that can only run python and write to one specific folder.

```bash
sudo useradd -d /home/grader -m grader
sudo passwd grader

sudo useradd executor
sudo passwd executor

sudo usermod -s /bin/bash executor
sudo usermod -d /home/grader/python_grader executor
```

#### 3. Install Python
I Installed Anaconda. Important here is that all users can execute Python.

I installed Python globally using Anaconda's installer and then created a group `anaconda` and added all users that should be able to use it.

```bash
wget "https://repo.anaconda.com/archive/Anaconda3-5.2.0-Linux-x86_64.sh"
chmod a+x Anaconda3-5.2.0-Linux-x86_64.sh
sudo ./Anaconda3-5.2.0-Linux-x86_64.sh
# Specified '/opt/anaconda/' as directory

sudo groupadd -g 1004 anaconda
chown -R .anaconda /opt/anaconda/
sudo usermod -a -G anaconda grader
sudo usermod -a -G anaconda executor
```

Nowadays, I would create a conda env:
```
conda create -n grader python=3.7 anaconda
```
And then use it with `source activate grader` and `source deactivate`.



#### 3. Created git repository
As user `grader` I created a bare repository `python_grader.py` and a clone thereof called `python_grader`:

```bash
su grader
mkdir /home/grader/python_grader.git
cd /home/grader/python_grader.git
git init --bare  --shared=group
cd /home/grader/
git clone python_grader.git python_grader

exit
```

Now you can commit the code to that repository, and test running

```bash
cd home/grader/python_grader
python main.py
```

Make sure everything belongs to the group `grader` but the two folders `tmp` and `log` must belong to the group `anaconda`:
```
sudo chgrp -R grader /home/grader
sudo chgrp -R anaconda /home/grader/python_grader/log
sudo chgrp -R anaconda /home/grader/python_grader/tmp
```
#### 4. Fixed all permission porblems so that the executor can run `python main.py`

#### 5. Used `systemctl` to run the grader automatically:

  Create a file `/lib/systemd/system/python-grader.service` with the following content:

  ```
  [Unit]
  Description=Python grader for openEDX
  After=network.target

  [Service]
  Type=simple
  Restart=always
  RestartSec=1
  StartLimitBurst=0
  User=executor
  ExecStart=/opt/anaconda/anaconda3/bin/python  /home/grader/python_grader/main.py

  [Install]
  WantedBy=multi-user.target
  ```

  You can activate it with `systemctl daemon-reload` and then the four important commands are:
  ```
systemctl status python-grader
systemctl start python-grader
systemctl stop python-grader
systemctl restart python-grader
```


#### 6. Created a file`/home/grader/python_grader.git/hooks/post-receive` to update the live version whenever somebody pushes a change:
```bash
#!/bin/bash
TARGET="/home/grader/python_grader"
GIT_DIR="/home/grader/python_grader.git"
BRANCH="master"
while read oldrev newrev ref
do

        # only checking out the master (or whatever branch you would like to deploy)
        if [[ $ref = refs/heads/$BRANCH ]];
        then
                echo "Ref $ref received. Deploying ${BRANCH} branch to production..."
                git --work-tree=$TARGET --git-dir=$GIT_DIR checkout -f
                # Restart grader automatically
                sudo systemctl restart python-grader
        else
                echo "Ref $ref received. Doing nothing: only the ${BRANCH} branch may be deployed on this server."
        fi
done
```
