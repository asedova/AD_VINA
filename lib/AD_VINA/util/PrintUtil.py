import functools
import pprint, json
import subprocess
import sys
import os

MAX_LINES = 70
print = functools.partial(print, flush=True)
subprocess.run = functools.partial(subprocess.run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


def dprint(*args, run=False, **kwargs):
    print = functools.partial(globals()['print'], **kwargs)

    def try_json_print(arg):
        if isinstance(arg, (dict, list)):
            try:
                arg_json = json.dumps(arg, indent=3, default=str)
                if arg_json.count('\n') > MAX_LINES:
                    arg_json = '\n'.join(arg_json.split('\n')[0:MAX_LINES] + ['...'])
                print(arg_json)
            except:
                print('(did not successfully dump as json)')
                print(arg, end=' ')
        else:
            print(arg, end=' ')

    print('##############################################################')
    for arg in args:
        if run:
            print('>> ' + arg)
            if run in ['cli']:
                completed_proc = subprocess.run(arg)
                try_json_print(completed_proc.stdout.decode('utf-8'))
                try_json_print(completed_proc.stderr.decode('utf-8'))
            elif isinstance(run, dict):
                try_json_print(eval(arg, run))
            else:
                assert False
        else:
            try_json_print(arg)
        print()
    print('--------------------------------------------------------------')


