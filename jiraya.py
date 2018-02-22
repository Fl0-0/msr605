#!/usr/bin/python
# -*- coding: utf-8 -*-
import colorama
from colorama import Fore, Back
import shlex 
import signal
import readline
import os, sys
sys.path.insert(0,'./lib/')
import msr605_cmd
import test
import time
import optparse

def optionsManager():
    parser = optparse.OptionParser(sys.argv[0]+" --help")
    parser.add_option('-d','--dev',dest="DEV",type="string",help='/dev/ttyUSB0')
    parser.add_option('-t','--type',dest="TYPE",type="string",help='<iso,raw>')
    parser.add_option('-m','--mode',dest="MODE",type="string",help='<hico,loco>')

    (opt, args) = parser.parse_args()

    return opt

global Save, autoSave, bpc, bpi, mode, track_type, dev_ptr

options = optionsManager()

Save = ""
autoSave = False
bpc = ['8', '8', '8'] # bits per character for each tracks
bpi = ['210', '75', '210'] # bits per inch for each tracks
if options.MODE is not None:
    mode = options.MODE
else:
    mode = 'hico' 
if options.TYPE is not None:
    track_type = options.TYPE
else:
    track_type = 'iso'


def tokenize(string):
    """
    	to get a well formed command+args
    """
    return shlex.split(string)

def shell_loop(device):
    # auto-completion
    readline.set_completer(msr605_cmd.completer)
    readline.parse_and_bind('tab: complete')

    dev_ptr = test.msr_init(device)
    if dev_ptr == False:
        print " [-] Please check that the device is on /dev/ttyUSB0"
        sys.exit(1)

    # init 
    test.msr_reset(dev_ptr)
    test.set_coercivity(mode,dev_ptr)
    test.set_bpc(int(bpc[0]), int(bpc[1]), int(bpc[2]),dev_ptr)
    while True:
    	# display a command prompt
    	cmd = raw_input(Back.WHITE+Fore.RED+' msr605 ['+device+'](help/settings)> '+Back.RESET+Fore.CYAN+' ')

    	# tokenize the command input
    	cmd_tokens = tokenize(cmd)

    	# execute the command
        msr605_cmd.execute(cmd_tokens, dev_ptr)


def closeProgram(signal, frame):
    sys.exit(1)

def main():
    signal.signal(signal.SIGINT, closeProgram) # close program with Ctrl+C

    if options.DEV is not None:
        device = options.DEV
    else:
        device = "/dev/ttyUSB0"

    shell_loop(device)

if __name__ == '__main__':
    main()

