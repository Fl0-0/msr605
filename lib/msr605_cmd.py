#!/usr/bin/python
import sys, os
import datetime
import serial
from os.path import isfile, join
from os import listdir
import colorama
from colorama import Fore, Back
#import msr605_drv
sys.path.insert(0,'../')
import jiraya

# auto-completion
cmdList = [ 'autosave ',
            'bpc ',
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
            'hico',
            'iso',
            'led',
            'loco',
            'mode ',
            'off',
            'on',
            'play',
            'raw',
	    'read', 
            'reset',
            'save',
            'set ',
            'settings',
            'type ',
	    'write', 
	    'quit']


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

def get_hex_value(strip):
    res = ""
    for i in strip:
        val =  i[2:]
        if len(val) == 1:
            val = '0'+val
        res += val
    return res

############################################################
############################################################
############################################################

def help_menu():
	print "="*60
	print " Play with MSR605 **\\(^.^)//**"
        print " Magnetic Swipe Card Reader/Writer"
        print "="*23+"COMMAND LINE"+"=25"
        print ' -d /dev/ttyUSB0\t device'
        print ' -t <iso/raw>\t\t type'
        print ' -m <hico/loco>\t\t mode'
	print "="*23+"GENERAL"+"="*30
	print " ?/help\t\t\t display this help"
	print " quit/exit\t\t quit the program"
	print " clear\t\t\t clear the screen"
        print " settings\t\t display current settings"
        print " reset\t\t\t reset to default config"
	print "="*23+"ACTIONS"+"="*30
        print " compare/bulk_compare"
        print " copy/bulk_copy"
        print " erase"
        print " read/bulk_read"
        print " save"
        print " write/bulk_write"
        print " play <g,y,r,all> led <on,off>"
	print "="*23+"SETTINGS"+"="*29
        print " set mode <hico,loco>"
        print " set type <iso,raw>"
        print " set autosave <on,off>"
        print " set bpc <777,456,...>\t not working properly (default: 888)"
        print " set bpi <1,2,3,all> <210,75>"
	print "="*60

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
        print " [+] Saved to "+folder+"/"+filename+"_"+timestamp
    else:
        print " [-] Error during saving"

def verifyEmptyTrack(t1,t2,t3):
    if t1 == None:
        t1 = ''
    if t2 == None:
        t2 = ''
    if t3 == None:
        t3 = ''
    return t1,t2,t3

def printTracks(track1, track2, track3):
    if jiraya.track_type == 'raw':
        print(Fore.GREEN+" [1-binary]: "+Fore.RESET+get_hex_value(map(bin,bytearray(track1))))
        print(Fore.GREEN+" [2-binary]: "+Fore.RESET+get_hex_value(map(bin,bytearray(track2))))
        print(Fore.GREEN+" [3-binary]: "+Fore.RESET+get_hex_value(map(bin,bytearray(track3))))
        print("")
        print(Fore.GREEN+" [1-hexa]: "+Fore.RESET+get_hex_value(map(hex,bytearray(track1))))
        print(Fore.GREEN+" [2-hexa]: "+Fore.RESET+get_hex_value(map(hex,bytearray(track2))))
        print(Fore.GREEN+" [3-hexa]: "+Fore.RESET+get_hex_value(map(hex,bytearray(track3))))
        print("")
        print(Fore.GREEN+" [1-ascii]: "+Fore.RESET+track1)
        print(Fore.GREEN+" [2-ascii]: "+Fore.RESET+track2)
        print(Fore.GREEN+" [3-ascii]: "+Fore.RESET+track3)
    if jiraya.track_type == 'iso':
        print(Fore.GREEN+" [1-ascii]: "+Fore.RESET+track1)
        print(Fore.GREEN+" [2-ascii]: "+Fore.RESET+track2)
        print(Fore.GREEN+" [3-ascii]: "+Fore.RESET+track3)

def execute(cmd_tokens, dev_ptr):
    import msr605_drv
    """
    	execute the command+args
    	command: cmd_tokens[0]
    	args: cmd_tokens[i]
    """
    if len(cmd_tokens)==0:
        return False

    ############# SETTINGS
    if cmd_tokens[0] == 'settings':
        #status = msr605_drv.get_hico_loco_status(dev_ptr)
        model = msr605_drv.get_device_model(dev_ptr)
        firmware = msr605_drv.get_firmware_version(dev_ptr)
        #comm = msr605_drv.do_communication_msr605_drv(dev_ptr)
        #ram = msr605_drv.do_ram_msr605_drv(dev_ptr)
        i = 60
        print "="*i
        print ' write mode: '+jiraya.mode
        print ' track type: '+jiraya.track_type
        print ' bpc1: '+jiraya.bpc[0]+"\t bpc2: "+jiraya.bpc[1]+"\t bpc3: "+jiraya.bpc[2]
        print ' bpi1: '+jiraya.bpi[0]+"\t bpi2: "+jiraya.bpi[1]+"\t bpi3: "+jiraya.bpi[2]
        print ' autosave: '+ str(jiraya.autoSave)
        print "="*i
        print ' device model: '+model
        print ' firmare version: '+firmware
        #print ' RAM: '+ram
        #print ' communication: '+comm
        print "="*i

        return True
    
    if ((cmd_tokens[0] == 'set') and (len(cmd_tokens)>2)):
        if cmd_tokens[1] == 'mode':
            if cmd_tokens[2] == 'hico':
                jiraya.mode = 'hico'
                msr605_drv.set_coercivity('hico',dev_ptr)
            elif cmd_tokens[2] == 'loco':
                jiraya.mode = 'loco'
                msr605_drv.set_coercivity('loco',dev_ptr)
            else:
                print(' [*] this mode does not exist')
                print(' [*] try: hico or loco')
                jiraya.mode == jiraya.mode
    
        elif cmd_tokens[1] == 'type':
            if cmd_tokens[2] == 'iso':
                jiraya.track_type = 'iso'
                print ' [+] type iso: OK'
            elif cmd_tokens[2] == 'raw':
                jiraya.track_type = 'raw'
                print ' [+] type raw: OK'
            else:    
                print(' [*] this track type does not exist')
                print(' [*] try: raw or iso')
                jiraya.track_type = jiraya.track_type
    
        elif cmd_tokens[1] == 'bpc':
            bpc_value = cmd_tokens[2]
            jiraya.bpc[0] = bpc_value[0]
            jiraya.bpc[1] = bpc_value[1]
            jiraya.bpc[2] = bpc_value[2]
            msr605_drv.set_bpc(int(jiraya.bpc[0]), int(jiraya.bpc[1]), int(jiraya.bpc[2]))
            print ' [+] bpc '+cmd_tokens[2]+": OK"
    
        elif cmd_tokens[1] == "bpi":
            if cmd_tokens[2] == "1":
                jiraya.bpi[0] = cmd_tokens[3]
            elif cmd_tokens[2] == "2":
                jiraya.bpi[1] = cmd_tokens[3]
            elif cmd_tokens[2] == "3":
                jiraya.bpi[2] = cmd_tokens[3]
            elif cmd_tokens[2] == "all":
                jiraya.bpi[0] = cmd_tokens[3]
                jiraya.bpi[1] = cmd_tokens[3]
                jiraya.bpi[2] = cmd_tokens[3]
            else:
                print " [*] usage: set bpi <1,2,3,all> <210,75>"
            msr605_drv.set_bpi(jiraya.bpi[0], jiraya.bpi[1], jiraya.bpi[2], dev_ptr)
            print " [+] bpi to track "+cmd_tokens[2]+" set to "+cmd_tokens[3]+": OK"



        elif cmd_tokens[1] == 'autosave':
                if cmd_tokens[2] == "on":
                    jiraya.autoSave = True
                    print ' [+] autosave: on'
                elif cmd_tokens[2] == "off":
                    jiraya.autoSave = False
                    print ' [+] autosave: off'
        else:
            print " [-] use the help menu, please"
    
        return True
    
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
        print " [*] swipe card to read"
        if jiraya.track_type == 'iso':
            t1, t2, t3 = msr605_drv.read_iso_tracks(dev_ptr)
        if jiraya.track_type == 'raw':
            t1, t2, t3 = msr605_drv.read_raw_tracks(dev_ptr)

        t1,t2,t3 = verifyEmptyTrack(t1,t2,t3) 
        printTracks(t1,t2,t3)

        print " [*] swipe card to compare"
        if jiraya.track_type == 'iso':
            b1, b2, b3 = msr605_drv.read_iso_tracks(dev_ptr)
        if jiraya.track_type == 'raw':
            b1, b2, b3 = msr605_drv.read_raw_tracks(dev_ptr)
        if b1 == t1 and b2 == t2 and t3 == t3:
            print " [+] Compare OK"
        else:
            b1,b2,b3 = verifyEmptyTrack(b1,b2,b3) 
            printTracks(b1,b2,b3)
            print " [-] Compare FAILED"
    
        return True
    
    ############ BULK COMPARE
    if cmd_tokens[0] == 'bulk_compare':
        print " [*] swipe card to read"
        if jiraya.track_type == 'iso':
            t1, t2, t3 = msr605_drv.read_iso_tracks(dev_ptr)
        if jiraya.track_type == 'raw':
            t1, t2, t3 = msr605_drv.read_raw_tracks(dev_ptr)

        t1,t2,t3 = verifyEmptyTrack(t1,t2,t3) 
        printTracks(t1,t2,t3)
        while True:
            print " [*] swipe card to compare"
            try:
                if jiraya.track_type == 'iso':
                    b1, b2, b3 = msr605_drv.read_iso_tracks(dev_ptr)
                if jiraya.track_type == 'raw':
                    b1, b2, b3 = msr605_drv.read_raw_tracks(dev_ptr)
            except KeyboardInterrupt:
                break
            if b1 == t1 and b2 == t2 and t3 == t3:
                print " [+] Compare OK"
            else:
                b1,b2,b3 = verifyEmptyTrack(b1,b2,b3) 
                printTracks(b1,b2,b3)
                print " [-] Compare FAILED"
        return True 
    
    
    ############# READ
    if cmd_tokens[0] == 'read':
        print " [*] swipe card to read"
    
        if jiraya.track_type == 'iso':
            t1, t2, t3 = msr605_drv.read_iso_tracks(dev_ptr)
        if jiraya.track_type == 'raw':
            t1, t2, t3 = msr605_drv.read_raw_tracks(dev_ptr)

        t1,t2,t3 = verifyEmptyTrack(t1,t2,t3) 
        printTracks(t1,t2,t3)

        saveItToFile = 'track1:'+t1+'\n'+'track2:'+t2+'\n'+'track3:'+t3+'\n'
    
        if jiraya.autoSave:
            filename = 'autosave'
            savedata(filename, os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + '/../autosave'), saveItToFile)
    
        jiraya.Save = saveItToFile
    
        return True
    
    ############# BULK READ
    if cmd_tokens[0] == 'bulk_read':
        var_msr605_drv = True
        while var_msr605_drv:
            print " [*] swipe card to read"
            if jiraya.track_type == 'iso':
                t1, t2, t3 = msr605_drv.read_iso_tracks(dev_ptr)
            if jiraya.track_type == 'raw':
                t1, t2, t3 = msr605_drv.read_raw_tracks(dev_ptr)

            t1,t2,t3 = verifyEmptyTrack(t1,t2,t3) 
            printTracks(t1,t2,t3)

            saveItToFile = 'track1:'+t1+'\n'+'track2:'+t2+'\n'+'track3:'+t3+'\n'
    
            if jiraya.autoSave:
                filename = 'autosave'
                savedata(filename, './autosave', saveItToFile)
    
    
            next = raw_input(" continue? [Yes/no] ")
    
            if ((next.lower()=="y") or (next.lower()=="yes")):
                var_msr605_drv = True
            else:
                var_msr605_drv = False
    
        return True
        
    
    ############# ERASE
    if cmd_tokens[0] == 'erase':
        print " [*] swipe card to erase all tracks"
        msr605_drv.erase_tracks(dev_ptr,t1=True, t2=True, t3=True)
        print " [+] Erased."
        return True
    
    ############# COPY
    if cmd_tokens[0] == 'copy':
        print " [*] swipe card to read"
        if jiraya.track_type == 'iso':
            t1, t2, t3 = msr605_drv.read_iso_tracks(dev_ptr)
        if jiraya.track_type == 'raw':
            print(' [-] cannot copy in raw mode yet, please use: set type iso')
            return True

        t1,t2,t3 = verifyEmptyTrack(t1,t2,t3) 
        printTracks(t1,t2,t3)
        print " [*] swipe card to write, ^C to cancel"
        
        # to remove the start sentinel and the end sentinel
        if t1!=None:
            t1 = t1[1:-1]
        if t2!=None:
            t2 = t2[1:-1]
        if t3!=None:
            t3 = t3[1:-1]

        if jiraya.track_type == 'iso':
            res=msr605_drv.write_iso_tracks(t1,t2,t3,dev_ptr)
        if jiraya.track_type == 'raw':
            #msr605_drv.write_raw_tracks(**kwargs)
            print(' [-] cannot copy in raw mode yet, please use: set type iso')
            return True
        if res:
            print " [+] Written."
        else:
            print " [-] Not written"
        return True
    
    ############## BULK COPY
    if cmd_tokens[0] == 'bulk_copy':
        print " [*] swipe card to read, ^C to cancel"
        if jiraya.track_type == 'iso':
            t1, t2, t3 = msr605_drv.read_iso_tracks(dev_ptr)
        if jiraya.track_type == 'raw':
            print(' [-] cannot copy in raw mode yet, please use: set type iso')
            return True

        t1,t2,t3 = verifyEmptyTrack(t1,t2,t3) 
        printTracks(t1,t2,t3)
    
        # to remove the start sentinel and the end sentinel
        if t1!=None:
            t1 = t1[1:-1]
        if t2!=None:
            t2 = t2[1:-1]
        if t3!=None:
            t3 = t3[1:-1]

        var_msr605_drv = True
        while var_msr605_drv:
            try:
                print " [*] swipe card to write"
                res = msr605_drv.write_iso_tracks(t1,t2,t3,dev_ptr)
                if res:
                    print " [+] Written."
                else:
                    print " [-] Not written"
            except Exception as e:
                print " [-] Failed. Error:", e
    
            next = raw_input(" [*] continue? [Yes/no] ")
    
            if ((next.lower()=="y") or (next.lower()=="yes")):
                var_msr605_drv = True
            else:
                var_msr605_drv = False
        return True
    
    ############## WRITE
    if cmd_tokens[0] == 'write':
        print " [*] Input your data. Enter for not writing to a track."
        print " Track 1:",
        t1 = raw_input().strip()
        print " Track 2:",
        t2 = raw_input().strip()
        print " Track 3:",
        t3 = raw_input().strip()
        print " [*] swipe card to write"
        if jiraya.track_type == 'iso':
            res = msr605_drv.write_iso_tracks(t1,t2,t3,dev_ptr)
        if jiraya.track_type == 'raw':
            #msr605_drv.write_raw_tracks(1,t2,t3,dev_ptr)
            print(' [-] cannot write in raw mode yet, please: set type iso')
            return True
        if res:
            print " [+] Written."
        else:
            print " [-] Not written"
        return True
    
    ############## BULK WRITE
    if cmd_tokens[0] == 'bulk_write':
        print " [*] Input your data. Enter for not writing to a track."
        print " Track 1:",
        t1 = raw_input().strip()
        print " Track 2:",
        t2 = raw_input().strip()
        print " Track 3:",
        t3 = raw_input().strip()
    
        var_msr605_drv = True
        while var_msr605_drv:
            print " [*] swipe card to write"
            if jiraya.track_type == 'iso':
                res = msr605_drv.write_iso_tracks(t1,t2,t3,dev_ptr)
            if jiraya.track_type == 'raw':
                #msr605_drv.write_raw_tracks(t1,t2,t3,dev_ptr)
                print(' [-] cannot write in raw mode yet, please: set type iso')
                return True
    
            if res:
                print " [+] Written."
            else:
                print " [-] Not written"
    
            next = raw_input(" [*] continue? [Yes/no] ")
    
            if ((next.lower()=="y") or (next.lower()=="yes")):
                var_msr605_drv = True
            else:
                var_msr605_drv = False
        return True
    
    ############## SAVE
    if cmd_tokens[0] == 'save':
        if jiraya.Save != "":
            filename = raw_input(" Filename: ")
    
            savedata(filename, os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + '/../archives'), jiraya.Save)
    
            jiraya.Save = ""
        else:
            print " [*] You should read a card first"
    
        return True
    
    ############## PLAY
    if ((cmd_tokens[0] == 'play') and (cmd_tokens[2] == 'led')):
        if cmd_tokens[3] == 'on':
            if cmd_tokens[1] == 'all':
                msr605_drv.play_all_led_on(dev_ptr)
            elif cmd_tokens[1] == "g":
                msr605_drv.play_green_led_on(dev_ptr)
            elif cmd_tokens[1] == "y":
                msr605_drv.play_yellow_led_on(dev_ptr)
            elif cmd_tokens[1] == "r":
                msr605_drv.play_red_led_on(dev_ptr)
            else:
                print ' [-] that led color does not exist (g,y,r,all)'

        elif cmd_tokens[3] == 'off':
            msr605_drv.play_all_led_off(dev_ptr)

        else:
            print ' [-] that status does not exist (on,off)'
        return True

    ############# RESET
    if cmd_tokens[0] == "reset":
        msr605_drv.msr_reset(dev_ptr)
        msr605_drv.set_coercivity("hico",dev_ptr)
        msr605_drv.set_bpc(int(jiraya.bpc[0]), int(jiraya.bpc[1]), int(jiraya.bpc[2]),dev_ptr)
        jiraya.track_type = "iso"
        return True

    ############## IF COMMAND DOES NOT EXIST
    print " [*] that command does not exist"
    return False
                
