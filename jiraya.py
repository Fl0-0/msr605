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
import time

    
def tokenize(string):
    """
    	to get a well formed command+args
    """
    return shlex.split(string)

def shell_loop():
    # auto-completion
    readline.set_completer(msr605_cmd.completer)
    readline.parse_and_bind('tab: complete')

    status = True
    device = '?'
    settings = 'hico'
    save = False # use to init the value at null because nothing to save
    while status:
    	# display a command prompt
    	cmd = raw_input(Back.WHITE+Fore.RED+' msr605 '+device+'('+settings+')> '+Back.RESET+Fore.CYAN+' ')
        os.system('clear')

    	# tokenize the command input
    	cmd_tokens = tokenize(cmd)
    
        try:
            if cmd_tokens[0] == 'use':
                device = cmd_tokens[1]
        except:
            continue

        try:
            if cmd_tokens[0] == 'settings':
                if cmd_tokens[1] == 'hico':
                    settings = 'hico'
                elif cmd_tokens[1] == 'loco':
                    settings = 'loco'
                else:
                    print(' [*] this settings does not exist')
                    print(' [*] try: hico or loco')
                    settings == settings
        except:
            continue

        print(Back.WHITE+Fore.RED+' msr605 '+device+'('+settings+')> '+Back.RESET+Fore.CYAN+' '+cmd)


    	# execute the command and retrieve new status
    	try:
            if cmd_tokens[0] != 'use':
        	status = msr605_cmd.execute(cmd_tokens, device, settings, save)
                save = status
    	except:
    	    continue


def closeProgram(signal, frame):
    sys.exit(1)

def main():
    signal.signal(signal.SIGINT, closeProgram) # close program with Ctrl+C
    os.system('clear')

    shell_loop()

if __name__ == '__main__':
    main()

