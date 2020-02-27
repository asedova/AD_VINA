import functools
import pprint, json
import subprocess
import sys
import os
import time

MAX_LINES = 70
print = functools.partial(print, flush=True)
subprocess.run = functools.partial(subprocess.run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

#TODO decouple dprint and drun?
#TODO time
def dprint(*args, run=False, subproc_run_kwargs={}, print_kwargs={}):
    print = functools.partial(globals()['print'], **print_kwargs)

    def print_format(arg):
        if isinstance(arg, (dict, list)):
            try:
                arg_json = json.dumps(arg, indent=3, default=str)
                if arg_json.count('\n') > MAX_LINES:
                    arg_json = '\n'.join(arg_json.split('\n')[0:MAX_LINES] + ['...'])
                print(arg_json)
            except:
                print('(dprint error: did not successfully dump as json)')
                print(arg)
        else:
            print(arg, end=' ')

    print('##############################################################')
    for arg in args:
        if run:
            print('>> ' + arg)
            if run in ['cli', 'shell']:
                completed_proc = subprocess.run(arg, **subproc_run_kwargs)
                retcode = completed_proc.returncode
                stdout = completed_proc.stdout.decode('utf-8')
                stderr = completed_proc.stderr.decode('utf-8')
                print_format(stdout)
                print_format(stderr)
            elif isinstance(run, dict):
                print_format(eval(arg, run))
            else:
                assert False
        else:
            print_format(arg)
        print()
    print('--------------------------------------------------------------')
    # return last run
    if run and run in ['cli', 'shell']:
        return (retcode, stdout, stderr)


def where_am_i(f):
    '''
    Decorator
    '''
    dprint("where am i? in module " + globals()['__name__'] + " method " + f.__qualname__)
    return f
