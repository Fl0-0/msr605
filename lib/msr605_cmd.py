#!/usr/bin/python
import sys, os
import datetime
import serial
from os.path import isfile, join
from os import listdir
import colorama
from colorama import Fore, Back
import msr
sys.path.insert(0,'../')
import jiraya

# auto-completion
cmdList = [ 'autosave ',
            'clear', 
            'bulk_compare',
            'bulk_copy',
            'bulk_erase',
            'bulk_read',
            'bulk_write',
	    'compare', 
	    'copy', 
	    'erase', 
	    'exit', 
	    'help', 
            'iso',
            'mode ',
            'off'
            'on',
            'raw',
	    'read', 
            'save',
            'settings ',
            'status',
            'use ',
	    'write', 
	    'quit',
            'dev/',
            'ttyUSB0',
            'ttyUSB1',
            'ttyUSB2',
            'ttyUSB3']


############################################################
############################################################
############################################################

def completer(text, state):
	"""
		auto-completion
	"""
	options = [x for x in cmdList if x.startswith(text)]
	try:
		return options[state]
	except IndexError:
		return None

############################################################
############################################################
############################################################

def help_menu():
	i = 60
	print "="*i
	print " Play with MSR605 **\\(^.^)//**"
        print " Magnetic Swipe Card Reader/Writer"
	print "="*i
	print " ?/help\t\t\t display this help"
	print " quit/exit\t\t quit the program"
	print " clear\t\t\t clear the screen"
        print " settings\t\t hico/loco"
        print " autosave\t\t on/off/status"
	print "="*i
        print " compare/bulk_compare"
        print " copy/bulk_copy"
        print " erase"
        print " mode\t\t\t iso/raw"
        print " read/bulk_read"
        print " save"
        print " use /dev/ttyUSB0\t look at dmesg"
        print " write/bulk_write"
	print "="*i

def savedata(filename, folder, data):
    try:
        if not os.path.isdir(folder):
            os.makedirs(folder)
    
        timestamp = str(datetime.datetime.now())
        timestamp = timestamp.replace(' ', '_')
        try: 
            with open(folder+'/'+filename+'_'+timestamp,'w') as fp:
                fp.write(data)
        except Exception,e:
            print str(e)


        result =  True
    except:
        result = False

    if result:
        print "[+] Saved to "+folder+"/"+filename+"_"+timestamp
    else:
        print "[-] Error during saving"


def execute(cmd_tokens, dev, settings, mode):
	"""
		execute the command+args
		command: cmd_tokens[0]
		args: cmd_tokens[i]
	"""


        ############## DEVICE EMPTY
        if dev == "?":
	    ############## HELP
    	    if (cmd_tokens[0] == '?' or cmd_tokens[0]=='help'):
		help_menu()
                return True

	    ############## CLEAR
	    if cmd_tokens[0] == 'clear':
		os.system("clear")
                return True

    	    ############## QUIT
            if (cmd_tokens[0]=="quit" or cmd_tokens[0]=="exit"):
                sys.exit(1)

            ##############
            print "[*] you should use the command 'use' before doing anything else"
            return True # to stay in the while loop in tha apt.py

        ############## DEVICE NOT EMPTY
        else:

            if settings == 'hico':
                dev.set_coercivity(dev.hico)

            if settings == 'loco':
                dev.set_coercivity(dev.loco)

	    ############## HELP
    	    if (cmd_tokens[0] == '?' or cmd_tokens[0]=='help'):
		help_menu()
                return True

	    ############## CLEAR
	    if cmd_tokens[0] == 'clear':
		os.system("clear")
                return True

    	    ############## QUIT
            if (cmd_tokens[0]=="quit" or cmd_tokens[0]=="exit"):
                sys.exit(1)

            ############ COMPARE
            if cmd_tokens[0] == 'compare':
                print "[*] swipe card to read, ^C to cancel"
                if mode == 'iso':
                    t1, t2, t3 = dev.read_tracks()
                if mode == 'raw':
                    t1, t2, t3 = dev.read_raw_tracks()
                print "Track 1:", t1
                print "Track 2:", t2
                print "Track 3:", t3
                print "[*] swipe card to compare, ^C to cancel"
                if mode == 'iso':
                    b1, b2, b3 = dev.read_tracks()
                if mode == 'raw':
                    b1, b2, b3 = dev.read_raw_tracks()
                if b1 == t1 and b2 == t2 and t3 == t3:
                    print "[+] Compare OK"
                else:
                    print "Track 1:", b1
                    print "Track 2:", b2
                    print "Track 3:", b3
                    print "[-] Compare FAILED"

                return True

            ############ BULK COMPARE
            if cmd_tokens[0] == 'bulk_compare':
                print "[*] swipe card to read, ^C to cancel"
                if mode == 'iso':
                    t1, t2, t3 = dev.read_tracks()
                if mode == 'raw':
                    t1, t2, t3 = dev.read_raw_tracks()
                print "Track 1:", t1
                print "Track 2:", t2
                print "Track 3:", t3
                while True:
                    print "[*] swipe card to compare, ^C to cancel"
                    try:
                        if mode == 'iso':
                            b1, b2, b3 = dev.read_tracks()
                        if mode == 'raw':
                            b1, b2, b3 = dev.read_raw_tracks()
                    except KeyboardInterrupt:
                        break
                    if b1 == t1 and b2 == t2 and t3 == t3:
                        print "[+] Compare OK"
                    else:
                        print "Track 1:", b1
                        print "Track 2:", b2
                        print "Track 3:", b3
                        print "[-] Compare FAILED"
                return True 


            ############# READ
            if cmd_tokens[0] == 'read':
                print "[*] swipe card to read, ^C to cancel"

                if mode == 'iso':
                    t1, t2, t3 = dev.read_tracks()
                if mode == 'raw':
                    t1, t2, t3 = dev.read_raw_tracks()

                print "Track 1:", t1
                print "Track 2:", t2
                print "Track 3:", t3

                if t1 == None:
                    t1 = ''
                if t2 == None:
                    t2 = ''
                if t3 == None:
                    t3 = ''

                saveItToFile = 'track1:'+t1+'\n'+'track2:'+t2+'\n'+'track3:'+t3+'\n'

                if jiraya.autoSave:
                    filename = 'autosave'
                    savedata(filename, './autosave', saveItToFile)

                jiraya.Save = saveItToFile

                return True

            ############# BULK READ
            if cmd_tokens[0] == 'bulk_read':
                var_test = True
                while var_test:
                    print "[*] swipe card to read"
                    if mode == 'iso':
                        t1, t2, t3 = dev.read_tracks()
                    if mode == 'raw':
                        t1, t2, t3 = dev.read_raw_tracks()

                    print "Track 1:", t1
                    print "Track 2:", t2
                    print "Track 3:", t3

                    if t1 == None:
                        t1 = ''
                    if t2 == None:
                        t2 = ''
                    if t3 == None:
                        t3 = ''

                    saveItToFile = 'track1:'+t1+'\n'+'track2:'+t2+'\n'+'track3:'+t3+'\n'

                    if jiraya.autoSave:
                        filename = 'autosave'
                        savedata(filename, './autosave', saveItToFile)


                    next = raw_input("continue? [Yes/no] ")

                    if ((next.lower()=="y") or (next.lower()=="yes")):
                        var_test = True
                    else:
                        var_test = False

                return True
                

            ############# ERASE
            if cmd_tokens[0] == 'erase':
                print "[*] swipe card to erase all tracks"
                dev.erase_tracks(t1=True, t2=True, t3=True)
                print "[+] Erased."
                return True

            ############# COPY
            if cmd_tokens[0] == 'copy':
                print "[*] swipe card to read"
                if mode == 'iso':
                    t1, t2, t3 = dev.read_tracks()
                if mode == 'raw':
                    print('[-] cannot copy in raw mode yet, please use: mode iso')
                    return True
                print "Track 1:", t1
                print "Track 2:", t2
                print "Track 3:", t3
                kwargs = {}
                if t1 is not None:
                    kwargs['t1'] = t1[1:-1]
                if t2 is not None:
                    kwargs['t2'] = t2[1:-1]
                if t3 is not None:
                    kwargs['t3'] = t3[1:-1]
                print "[*] swipe card to write, ^C to cancel"
                dev.write_tracks(**kwargs)
                print "[+] Written."
                return True

            ############## BULK COPY
            if cmd_tokens[0] == 'bulk_copy':
                print "[*] swipe card to read, ^C to cancel"
                if mode == 'iso':
                    t1, t2, t3 = dev.read_tracks()
                if mode == 'raw':
                    print('[-] cannot copy in raw mode yet, please use: mode iso')
                    return True
                print "Track 1:", t1
                print "Track 2:", t2
                print "Track 3:", t3
                kwargs = {}
                if t1 is not None:
                    kwargs['t1'] = t1[1:-1]
                if t2 is not None:
                    kwargs['t2'] = t2[1:-1]
                if t3 is not None:
                    kwargs['t3'] = t3[1:-1]

                var_test = True
                while var_test:
                    try:
                        print "[*] swipe card to write"
                        dev.write_tracks(**kwargs)
                        print "[+] Written."
                    except Exception as e:
                        print "[-] Failed. Error:", e

                    next = raw_input("continue? [Yes/no] ")

                    if ((next.lower()=="y") or (next.lower()=="yes")):
                        var_test = True
                    else:
                        var_test = False
                return True
            
            ############## WRITE
            if cmd_tokens[0] == 'write':
                print "[*] Input your data. Enter for not writing to a track."
                kwargs = {}
                print "Track 1:",
                t1 = raw_input().strip()
                print "Track 2:",
                t2 = raw_input().strip()
                print "Track 3:",
                t3 = raw_input().strip()
                if t1 != "":
                    kwargs['t1'] = t1
                if t2 != "":
                    kwargs['t2'] = t2
                if t3 != "":
                    kwargs['t3'] = t3
                print "[*] swipe card to write"
                if mode == 'iso':
                    dev.write_tracks(**kwargs)
                if mode == 'raw':
                    print('[-] cannot write in raw mode yet, please use: mode iso')
                    return True
                print "[+] Written."
                return True
            
            ############## BULK WRITE
            if cmd_tokens[0] == 'bulk_write':
                print "[*] Input your data. Enter for not writing to a track."
                kwargs = {}
                print "Track 1:",
                t1 = raw_input().strip()
                print "Track 2:",
                t2 = raw_input().strip()
                print "Track 3:",
                t3 = raw_input().strip()
                if t1 != "":
                    kwargs['t1'] = t1
                if t2 != "":
                    kwargs['t2'] = t2
                if t3 != "":
                    kwargs['t3'] = t3

                var_test = True
                while var_test:
                    print "[*] swipe card to write"
                    if mode == 'iso':
                        dev.write_tracks(**kwargs)
                    if mode == 'raw':
                        print('[-] cannot write in raw mode yet, please use: mode iso')
                        return True

                    print "[+] Written."

                    next = raw_input("continue? [Yes/no] ")

                    if ((next.lower()=="y") or (next.lower()=="yes")):
                        var_test = True
                    else:
                        var_test = False
                return True

            ############## SAVE
            if cmd_tokens[0] == 'save':
                if jiraya.Save != "":
                    filename = raw_input("Filename: ")

                    savedata(filename, './archives', jiraya.Save)

                    jiraya.Save = ""
                else:
                    print "[*] You should read a card first"

                return True

            ############## AUTOSAVE
            if ((cmd_tokens[0] == 'autosave') and (len(cmd_tokens)==2)):
                if cmd_tokens[1] == "on":
                    jiraya.autoSave = True
                elif cmd_tokens[1] == "off":
                    jiraya.autoSave = False
                elif cmd_tokens[1] == "status":
                    print '[+] autosave = '+str(jiraya.autoSave)
                else:
                    print '[*] autosave '+cmd_tokens[1]+' does not exist'
            elif ((cmd_tokens[0] == 'autosave') and (len(cmd_tokens)!=2)):
                print '[*] autosave need an argument: on/off/status'

                return True

            ############## IF COMMAND DOES NOT EXIST
            print "[*] that command does not exist"
            return True
            
