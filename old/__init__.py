import sys
import os

#TODO: set up logger
'''
def replace(stream, path):
    pathname = os.path.dirname(sys.argv[0])
    logfile = pathname + "\\eventlog.txt"
    new_stream = file(logfile, 'w')
    os.dup2(new_stream.fileno(), stream.fileno())
    return new_stream

for stream, path in (('stdout', 'out'), ('stderr', 'err')):
    setattr(sys, stream, replace(getattr(sys, stream), path))
'''

import control

def main():
    
    print("Program started!")
    
    ctrl = control.MainController()
    sys.exit(ctrl.execute())
    
    
if __name__ == '__main__':
    main()
