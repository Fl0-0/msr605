#!/usr/bin/python
import time
import serial
import sys
sys.path.insert(0,'../')
import jiraya

map_5bits = {   "00001": ["00", "0"],
                "10000": ["01", "1"],
                "01000": ["02", "2"],
                "11001": ["03", "3"],
                "00100": ["04", "4"],
                "10101": ["05", "5"],
                "01101": ["06", "6"],
                "11100": ["07", "7"],
                "00010": ["08", "8"],
                "10011": ["09", "9"],
                "01011": ["0A", ":"],
                "11010": ["0B", ";"],
                "00111": ["0C", "<"],
                "10110": ["0D", "="],
                "01110": ["0E", ">"],
                "11111": ["0F", "?"]
            }

map_7bits = {   "0000001": ["00", " "],
                "1000000": ["01", "!"],
                "0100000": ["02", "\""],
                "1100001": ["03", "#"],
                "0010000": ["04", "$"],
                "1010001": ["05", "%"],
                "0110001": ["06", "&"],
                "1110000": ["07", "'"],
                "0001000": ["08", "("],
                "1001001": ["09", ")"],
                "0101001": ["0A", "*"],
                "1101000": ["0B", "+"],
                "0011001": ["0C", "`"],
                "1011000": ["0D", "-"],
                "0111000": ["0E", "."],
                "1111000": ["0F", "/"],
                "0000100": ["10", "0"],
                "1000101": ["11", "1"],
                "0100101": ["12", "2"],
                "1100100": ["13", "3"],
                "0010101": ["14", "4"],
                "1010100": ["15", "5"],
                "0110100": ["16", "6"],
                "1110101": ["17", "7"],
                "0001101": ["18", "8"],
                "1001100": ["19", "9"],
                "0101100": ["1A", ":"],
                "1101101": ["1B", ";"],
                "0011100": ["1C", "<"],
                "1011101": ["1D", "="],
                "0111101": ["1E", ">"],
                "1111100": ["1F", "?"],
                "0000010": ["20", "@"],
                "1000011": ["21", "A"],
                "0100011": ["22", "B"],
                "1100010": ["23", "C"],
                "0010011": ["24", "D"],
                "1010010": ["25", "E"],
                "0110010": ["26", "F"],
                "1110011": ["27", "G"],
                "0001011": ["28", "H"],
                "1001010": ["29", "I"],
                "0101010": ["2A", "J"],
                "1101011": ["2B", "K"],
                "0011000": ["2C", "L"],
                "1011011": ["2D", "M"],
                "0111011": ["2E", "N"],
                "1111010": ["2F", "O"],
                "0000111": ["30", "P"],
                "1000110": ["31", "Q"],
                "0100110": ["32", "R"],
                "1100111": ["33", "S"],
                "0010110": ["34", "T"],
                "1010111": ["35", "U"],
                "0110111": ["36", "V"],
                "1110110": ["37", "W"],
                "0001110": ["38", "X"],
                "1001111": ["39", "Y"],
                "0101111": ["3A", "Z"],
                "1101110": ["3B", "["],
                "0011111": ["3C", "\\"],
                "1011110": ["3D", "]"],
                "0111110": ["3E", "^"],
                "1111111": ["3F", "_"]
            }

def msr_init(dev_path):
    try:
        res = serial.Serial(dev_path,9600,8,serial.PARITY_NONE,timeout=0)
    except:
        res = None

    if res != None:
        print " [+] device initialisation: OK"
        return res
    else:
        print " [-] device initialisation: KO"
        return False

def msr_reset(dev_ptr):
    try:
        dev_ptr.write("\x1B"+"\x61") # escape_code = \x1B
        time.sleep(0.1)
        print " [+] device reset to initial state: OK"
        result = True
    except:
        print " [-] device reset to initial state: KO"
        result = False
    return result

def execute_waitresult(command, dev_ptr, timeout=10):
    # execute
    dev_ptr.flushInput()
    dev_ptr.write("\x1B"+command) # escape_code = \x1B
    time.sleep(0.1)
    
    # get result
    dev_ptr.timeout = timeout
    result = dev_ptr.read()
    time.sleep(0.5)
    if result == "": 
        print " [*] operation timed out"
        return "","",""
    dev_ptr.timeout = 0

    result += dev_ptr.read(1000)
    
    # parse result : status, result, data
    pos = result.rindex("\x1B")
    status = result[pos+1]
    res = result[pos+2:]
    data = result[0:pos]

    return status, res, data

def set_coercivity(coercivity,dev_ptr):
    if coercivity == 'hico':
        status, _, _ = execute_waitresult("\x78",dev_ptr) # x
    elif coercivity == 'loco':
        status, _, _ = execute_waitresult("\x79",dev_ptr) # y
    if status != "0":
        print(" [-] set_coercivity() error: %c" % status)
        #raise Exception(" [-] set_coercivity() error: %c" % status)
        return False
    print " [+] set coercivity: OK"

def set_bpc(bpc1, bpc2, bpc3,dev_ptr):
    status, result, _ = execute_waitresult("\x6F"+chr(bpc1)+chr(bpc2)+chr(bpc3),dev_ptr) # \x6F: o
    if status != "0":
        print(" [-] set_bpc() error: %c" % status)
        #raise Exception(" [-] set_bpc() error: %c" % status)
        return False
    print " [+] set bpc: OK"

def read_raw_tracks(dev_ptr):
    status, _, data = execute_waitresult("\x6D",dev_ptr) # m : read raw data
    #data = map_7bits[0]
    if status != "0":
        print " [*] maybe it is an empty card, or not in the good type: set type iso/raw"
        #raise Exception(" [-] read_raw_tracks() error: %c" % status)
        return "","",""
    #return data
    return decode_rawdatablock(data)

def read_iso_tracks(dev_ptr):
    status, _, data = execute_waitresult("\x72",dev_ptr) # r
    if status != "0":
        print " [*] Maybe it is an empty one card"
        return "","",""
        #raise Exception(" [-] read_iso_tracks() error: %c" % status)
    return decode_isodatablock(data)

def decode_rawdatablock(data):

    # header
    if data[0:4] != "\x1B\x73\x1B\x01":
        print(" [-] bad datablock : don't start with 1B 73 1B 01", data)
        #raise Exception("bad datablock : don't start with 1B 73 1B 01", data)
        return "","",""
    
    # first strip
    strip1_start = 4
    strip1_end = strip1_start + 1 + ord(data[strip1_start]) # first byte is length
    strip1 = data[strip1_start+1:strip1_end]

    # second strip
    strip2_start = strip1_end+2
    if data[strip1_end:strip2_start] != "\x1B\x02":
        print(" [-] bad datablock : missing 1B 02 at position %d" % strip1_end, data)
        #raise Exception("bad datablock : missing 1B 02 at position %d" % strip1_end, data)
        return "","",""

    strip2_end = strip2_start + 1 + ord(data[strip2_start])
    strip2 = data[strip2_start+1:strip2_end]
        
    
    # third strip
    strip3_start = strip2_end+2
    if data[strip2_end:strip3_start] != "\x1B\x03":
        print(" [-] bad datablock : missing 1B 03 at position %d" % strip2_end, data)
        #raise Exception("bad datablock : missing 1B 03 at position %d" % strip2_end, data)
        return "","",""

    strip3_end = strip3_start + 1 + ord(data[strip3_start])
    strip3 = data[strip3_start+1:strip3_end]

    # trailer
    if data[strip3_end:] != "\x3F"+"\x1C":
        print(" [-] bad datablock : missing 3F 1C at position %d", strip3_end, data)
        #raise Exception("bad datablock : missing 3F 1C at position %d", strip3_end, data)
        return "","",""
            
    return strip1, strip2, strip3

def decode_isodatablock(data):
    # header and end
    if data[0:4] != "\x1B\x73\x1B\x01":
        print(" [-] bad datablock : don't start with 1B 73 1B 01", data)
        #raise Exception("bad datablock : don't start with 1B 73 1B 01", data)
        return "","",""
    if data[-2:] != "\x3F\x1C":
        print(" [-] bad datablock : don't end with 3F 1C", data)
        #raise Exception("bad datablock : don't end with 3F 1C", data)
        return "","",""
    
    # first strip
    strip1_start = 4
    strip1_end = data.index("\x1B", strip1_start)
    if strip1_end == strip1_start:
        strip1_end += 2
        strip1 = None
    else:
        strip1 = data[strip1_start:strip1_end]

    # second strip
    strip2_start = strip1_end+2
    if data[strip1_end:strip2_start] != "\x1B\x02":
        print(" [-] bad datablock : missing 1B 02 at position %d" % strip1_end, data)
        #raise Exception("bad datablock : missing 1B 02 at position %d" % strip1_end, data)
        return "","",""
    strip2_end = data.index("\x1B", strip2_start)
    if strip2_end == strip2_start:
        strip2_end += 2
        strip2 = None
    else:
        strip2 = data[strip2_start:strip2_end]
    
    # third strip
    strip3_start = strip2_end+2
    if data[strip2_end:strip3_start] != "\x1B\x03":
        print(" [-] bad datablock : missing 1B 03 at position %d" % strip2_end, data)
        #raise Exception("bad datablock : missing 1B 03 at position %d" % strip2_end, data)
        return "","",""
    if data[strip3_start] == "\x1B":
        strip3 = None
    else:
        strip3 = data[strip3_start:-2]
    
    return strip1, strip2, strip3


def write_raw_tracks(t1, t2, t3,dev_ptr):
    data = encode_rawdatablock(t1,t2,t3)
    status, _, _ = execute_waitresult("\x6E"+data,dev_ptr)
    if status != "0":
        print(" [-] write_raw_tracks() error: %c" % status)
        #raise Exception(" [-] write_raw_tracks() error: %c" % status)
        return False

def write_iso_tracks(t1, t2, t3,dev_ptr):
    if t1 == None:
        t1 = ""
    if t2 == None:
        t2 = ""
    if t3 == None:
        t3 = ""
    data = encode_isodatablock(t1,t2,t3)
    status, _, _ = execute_waitresult("\x77"+data,dev_ptr)
    if status != "0":
        print ' [*] probably too fast, take your time to swipe the card'
        #raise Exception(" [-] write_iso_tracks() error: %c" % status)
        return False
    return True

def encode_rawdatablock(strip1, strip2, strip3):
    # use empty string if you don't want to set a given strip : FIXME doesn't work
    datablock = "\x1bs"
    if strip1 != "":
        datablock += "\x1b\x01"+chr(len(strip1))+strip1
    if strip2 != "":
        datablock += "\x1b\x02"+chr(len(strip2))+strip2
    if strip3 != "":
        datablock += "\x1b\x03"+chr(len(strip3))+strip3
    datablock += "?\x1C"
    #return datablock
    return "\x1b\x73\x1b\x01"+chr(len(strip1))+strip1+"\x1b\x02"+chr(len(strip2))+strip2+"\x1b\x03"+chr(len(strip3))+strip3+"\x3F\x1C"

def encode_isodatablock(strip1, strip2, strip3):
    # use empty string if you don't want to set a given strip
    return "\x1b\x73\x1b\x01"+strip1+"\x1b\x02"+strip2+"\x1b\x03"+strip3+"\x3F\x1C"

def erase_tracks(dev_ptr,t1, t2, t3):
    mask = 0
    if t1: 
        mask |= 1
    if t2: 
        mask |= 2
    if t3: 
        mask |= 4

    status, _, _ = execute_waitresult("\x63"+chr(mask),dev_ptr)
    if status != "0":
        print(" [-] erase_tracks() error: %c" % status)
        #raise Exception(" [-] erase_tracks() error: %c" % status)

def set_leadingzero(self, track13, track2):
    status, result, _ = execute_waitresult("\x7A"+track13+track2)
    if status != "0":
        print(" [-] set_leadingzero() error: %c" % status)
        #raise Exception(" [-] set_leadingzero() error: %c" % status)

def set_bpi(bpi1, bpi2, bpi3,dev_ptr):
    modes = []
    if bpi1=="210": 
        modes.append("\xA1")    # 210bpi
    elif bpi1=="75": 
        modes.append("\xA0")    # 75bpi

    if bpi2=="210": 
        modes.append("\xD2")    # 210bpi
    elif bpi2=="75": 
        modes.append("\x4B")    # 75bpi

    if bpi3=="210": 
        modes.append("\xC1")    # 210bpi
    elif bpi3=="75": 
        modes.append("\xC0")    # 75bpi

    for m in modes:
        status, result, _ = execute_waitresult("\x62"+m,dev_ptr)
        if status != "0":
            print(" [-] set_bpi() error: %c for %s" % (status,hex(m)))
            #raise Exception(" [-] set_bpi() error: %c for %s" % (status,hex(m)))

def get_device_model(dev_ptr):
    result = dev_ptr.write("\x1B"+"\x74") # escape_code = \x1B
    status = dev_ptr.read().decode()
    time.sleep(0.1)
    #status, result, blop = execute_waitresult("\x1B\x74", dev_ptr)
    if status != "0":
        return str(status)
    else:
        return ''

def get_firmware_version(dev_ptr):
    dev_ptr.write("\x1B\x76") # escape_code = \x1B
    result = dev_ptr.read()
    print map(hex,bytearray(result))
    #pos = result.rindex("\x1B")
    #status = result[pos+1]
    #res = result[pos+2:]
    #data = result[0:pos]
    if result != "0":
        return "oups"#str(result)
    else:
        return ''

def get_hico_loco_status(dev_ptr):
    result = dev_ptr.write("\x1B"+"\x64") # escape_code = \x1B
    time.sleep(0.1)
    if result == 'H':
        return 'hico'
    elif result == 'L':
        return 'loco'
    else:
        return ''
        
def do_ram_test(dev_ptr):
    result = dev_ptr.write("\x1B"+"\x86") # escape_code = \x1B
    time.sleep(0.1)
    if result != "0":
       return 'KO'
    elif result == "0":   
        return 'OK'
    else:
        return ''

def do_communication_test(dev_ptr):
    result = dev_ptr.write("\x1B"+"\x65") # escape_code = \x1B
    time.sleep(0.1)
    if result == "y":
        return 'OK'
    elif result != "y":
        return 'KO'
    else:
        return ''

def do_sensor_test():
    status, _, _ = execute_waitresult("\x86")
    if status != "0":
        print(" [-] do_sensor_test() error: %c" % status)
        #raise Exception(" [-] do_sensor_test() error: %c" % status)
        return False
    print " [+] the card sensing circuit works properly"


def play_all_led_off(dev_ptr):
    dev_ptr.write("\x1B"+"\x81")
    print " [+] all led off"

def play_all_led_on(dev_ptr):
    dev_ptr.write("\x1B"+"\x82")
    print " [+] all led on"

def play_green_led_on(dev_ptr):
    dev_ptr.write("\x1B"+"\x83")
    print " [+] green led on"

def play_yellow_led_on(dev_ptr):
    dev_ptr.write("\x1B"+"\x84")
    print " [+] yellow led on"
    
def play_red_led_on(dev_ptr):
    dev_ptr.write("\x1B"+"\x85")
    print " [+] red led on"
