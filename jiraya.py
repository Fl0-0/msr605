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

global Save, autoSave, bpc, bpi, mode, track_type, dev_ptr

Save = ""
autoSave = False
bpc = ['8', '8', '8'] # bits per character for each tracks
bpi = ['210', '75', '210'] # bits per inch for each tracks
mode = 'hico' 
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
    	cmd = raw_input(Back.WHITE+Fore.RED+' msr605 (help/settings)> '+Back.RESET+Fore.CYAN+' ')

    	# tokenize the command input
    	cmd_tokens = tokenize(cmd)

    	# execute the command
        msr605_cmd.execute(cmd_tokens, dev_ptr)


def closeProgram(signal, frame):
    sys.exit(1)

def main():
    signal.signal(signal.SIGINT, closeProgram) # close program with Ctrl+C

    device = "/dev/ttyUSB0"

    shell_loop(device)

if __name__ == '__main__':
    main()

