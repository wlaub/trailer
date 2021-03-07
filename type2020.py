import sys
import time
import pygame
from pygame.locals import *

import colorama

import numpy as np

colorama.init()

#12 image lines
#9 text lines
#1 command lines


window = """┌──────────────────────────────────────────────────────────┐
│                                                          │
│                                                          │
│                                                          │
│                                                          │
│                                                          │
│                                                          │
│                                                          │
│                                                          │
│                                                          │
│                                                          │
│                                                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
                                                           │
                                                           │
                                                           │
                                                           │
                                                           │
                                                           │
                                                           │
                                                           │
                                                           ┴
>""".split('\n')

typerate = 0.25
linerate = 1.
flashrate = 1.
measrate = 7

class Cmd():
    """
    bg_idx - the image displayed while typing the command

    Sequence values:
    -2 = fade out
    -1 = linefeed 1
    >0 = change to this background
    if nothing left, feed the remaining lines
    """
    def __init__(self, bg_idx, sequence = []):
        self.bg_idx = bg_idx
        self.sequence = sequence
        pass

commands = {
#0x1: Cmd(0, []),
#0x2: Cmd(0, [-1, 2, -1, 3, -1, 4]),
#0x3: Cmd(0, []),
#0x4: Cmd(0, []),
#0x5: Cmd(0, [5]),
#0x6: Cmd(5, [-1, 7, -1, 8, -1, 9]),
#0x7: Cmd(5, [-1,-2,-1,10]),
#0x8: Cmd(10, []),
#0x9: Cmd(10, []),
#0x10: Cmd(10, []),
#0x11: Cmd(10, []),
#0x12: Cmd(10, [-1,-2,-1,11]),
#0x13: Cmd(11, [12]),
#0x14: Cmd(12, [13]),
#0x15: Cmd(13, [14]), #18, 16, 19,17
#0x18: Cmd(14, [15]), #drain rocks in correct sequence
#0x16: Cmd(15, [16]), #scramble this
#0x19: Cmd(16, [17]),
#0x17: Cmd(17, [18]), #end on canon
#0x20: Cmd(18, [-1,-2,-1,10]),
#0x21: Cmd(10, []),
#0x22: Cmd(10, []),
#0x23: Cmd(10, []),
#0x24: Cmd(10, [19]),
#0x25: Cmd(19, []),
#0x26: Cmd(19, [-1,-2,-1,18]),
#0x27: Cmd(18, [20]),
#0x28: Cmd(20, [-1,-2,-1,19]),
#0x29: Cmd(19, [21]),
#0x30: Cmd(21, [-1,-2,-1,22]),
#0x31: Cmd(22, []),
#0x32: Cmd(22, []),
#0x33: Cmd(22, []),
#0x34: Cmd(22, [-1,23,-2,-1,24]),
#0x35: Cmd(24, [-1,-2,-1,25]),
0xfe: Cmd(25, [-1]),
0xff: Cmd(-1, []), #TODO: Change this

0x01: Cmd(0, []),
0x02: Cmd(0, []),
0x03: Cmd(0, []),
0x04: Cmd(0, []),
0x13: Cmd(0, []),
0x14: Cmd(0, []),
0x2c: Cmd(0, []),
0x2d: Cmd(0, []),
0x2e: Cmd(0, []),
0x31: Cmd(0, []),
0x32: Cmd(0, []),
0x33: Cmd(0, []),
0x4a: Cmd(0, []),
0x4b: Cmd(0, []),
0x4c: Cmd(0, []),
0x4d: Cmd(0, []),
0x4e: Cmd(0, []),
0x4f: Cmd(0, []),
0x53: Cmd(0, []),
0x54: Cmd(0, []),
0x55: Cmd(0, []),
0x70: Cmd(0, []),
0x71: Cmd(0, []),
0x72: Cmd(0, []),

0x06: Cmd(0, []),
#0x4f: Cmd(0, []),
0x5b: Cmd(0, []),
#0x13: Cmd(0, []),
#0x71: Cmd(0, []),
}
#['flashcmd', 0xfe,0xfe,0xfe,0x71,0xfe,0xfe,0xfe],
#['flashcmd', 0xfe,0xfe,-1,0x13,0x5b,0x4f,0x06],


frames = []
    
def process_line(line):
    if len(line) == 0: return ''
    parts = line.split(' ')
    result = []
    for part in parts:
        if part.isupper():
            tpart = colorama.Fore.BLACK+colorama.Back.WHITE
            tpart += part
            fragment = ''
            if tpart[-1] in ['.',',',';',':']:
                fragment = tpart[-1]
                tpart = tpart[:-1]
            tpart += colorama.Fore.RESET+colorama.Back.RESET
            tpart += fragment
            result.append(tpart)

        else:
            result.append(part.upper())

    result = ' '.join(result)

    return result



def render(command, outbuf, image_lines):

    nlines = outbuf.count('\n') + 1
    out_lines = outbuf[-9:]

    out_frame = list(window)
    for idx, line in enumerate(out_lines):
        linelen = len(line)
        winlen = len(window[idx+14])
        line = process_line(line)
        out_frame[idx+14] = line + window[idx+14][linelen:]
#        if linelen >= winlen: 
#            out_frame[winlen-1] = window[idx+14][-1]

    for idx, line in enumerate(image_lines):
        out_frame[idx+1] = window[idx+1][0] + line + window[idx+1][len(line)+1:]

    out_frame[-1] = '> '+ command.upper()
    return '\n'.join(out_frame)

infile = sys.argv[1]
lines = open(infile, 'r', encoding='utf-8').read().split('\n')
#lines = list(map(process_line, lines))

#map command numbers to line numbers
command_index = {}
for idx, line in enumerate(lines):
    if '>' in line:
        try:
            command_index[int(line[:2], 16)] = idx
        except: pass

#strip command numbers
lines = list(map(lambda x: x if not '>' in x or x[2] != '>' in x else x[2:], lines))

lines_base = lines

#load backgrounds
bgraw = open('bldng_bg.txt','r', encoding='utf-8').read().split('\n')
backgrounds = []
while len(bgraw) > 0:
    backgrounds.append(bgraw[:12])
    bgraw = bgraw[12:]

#backgrounds = backgrounds[1:]

#load titlecard characters
charsraw = open('chars.txt', 'r', encoding='utf-8').read().split('\n')
charsmap = {}
for char_idx in range(26):
    charsmap[chr(0x41+char_idx)]=charsraw[6*char_idx+1:6*char_idx+1+5]

charsmap["'"]=[' \u2588 ',' \u2588 ','   ','   ','   ']
charsmap[' ']=['   ']*5

def render_title(top, bot, green = False):
    """
    render the title card with the top and bottom text
    """
    lines = []
    if green:
        lines.extend([colorama.Fore.GREEN+'    ']*12)
    else:
        lines.extend(['    ']*12)

    lines.extend(['    ']*12)

    for ypos, text in [[3, top],[16, bot]]:
        for char in text.upper():
            for y_idx, cline in enumerate(charsmap[char]):
                lines[ypos+y_idx] += cline + ' '

    lines = map(lambda x: x+colorama.Fore.RESET, lines)

    return '\n'.join(lines)

def fade_img(image):
    #fade out the image
    result = []
    charmap = {
        '\u2588':'\u2592',
        '\u2592':'\u2591',
        '\u2591':'.', 
        'G': colorama.Fore.GREEN,
        'R': colorama.Fore.RESET,
    }
    for line in image:
        line = line.replace(colorama.Fore.GREEN, 'G')
        line = line.replace(colorama.Fore.RESET, 'R')       
        nline = ''.join([charmap.get(x, ' ')for x in line])
        result.append(nline)

    return result

def flash_command(meas_idx, cmd_idx, seq_idx):
    #
    meas_time = meas_idx*measrate+seq_idx*flashrate
    next_time = meas_time

    start_idx = command_index[cmd_idx]

    image = backgrounds[commands[cmd_idx].bg_idx+1]
    outbuf, lines = lines_base[start_idx-9:start_idx], lines_base[start_idx:]
    command = ''

    line = lines[0]

    #first type out the command
    line = line[2:]
    tframe = render(command, outbuf, image)
    frames.append((meas_time, tframe))


def execute_command(meas_idx, cmd_idx):
    #
    meas_time = meas_idx*measrate
    next_time = meas_time

    start_idx = command_index[cmd_idx]

    image = backgrounds[commands[cmd_idx].bg_idx+1]
    outbuf, lines = lines_base[start_idx-9:start_idx], lines_base[start_idx:]
    command = ''

    line = lines[0]

    #first type out the command
    line = line[2:]
    tframe = render(command, outbuf, image)
    frames.append((meas_time, tframe))

    while len(line) > 0:
        command += line[0]
        line = line[1:]
        tframe = render(command, outbuf, image)
        frames.append((next_time, tframe))
        next_time += typerate#*beatrate

    outbuf.append('> '+command)
    command = ''

    #then run the command sequence
    line_idx = 1
    for step in commands[cmd_idx].sequence:
        if step == -1: #feed line
            outbuf.append(lines[line_idx])
            line_idx += 1
            tframe = render(command, outbuf, image)
            frames.append((next_time, tframe))
            next_time += linerate
        elif step >= 0: #update background
            image = backgrounds[step+1]
            tframe = render(command, outbuf, image)
            frames.append((next_time, tframe))
#            next_time += linerate
        elif step == -3: #update background
            image = backgrounds[0]
            tframe = render(command, outbuf, image)
            frames.append((next_time, tframe))
#            next_time += linerate
 
        elif step == -2: #fade out
            for i in range(4):
                image = fade_img(image)
                tframe = render(command, outbuf, image)
                frames.append((next_time, tframe))
                next_time += typerate


    #feed the remaining lines
    while line_idx < len(lines) and not '>' in lines[line_idx]:
        outbuf.append(lines[line_idx])
        line_idx += 1
        tframe = render(command, outbuf, image)
        frames.append((next_time, tframe))
        next_time += linerate#*beatrate

script = [
#0
['cmd', 1],
['cmd', 2],
['cmd', 3],
['cmd', 4],

#['cmd', 12],
['cmd', 0x13],
['cmd', 0x14], #this one is double length
['blank'],
#1
['cmd', 0x2c],
['cmd', 0x2d],
['cmd', 0x2e], #double length
['blank'],
['cmd', 0x31],
['cmd', 0x32],
['cmd', 0x33],
#2
['cmd', 0x4a],
['cmd', 0x4b],
['cmd', 0x4c],
['cmd', 0x4d],
['cmd', 0x53],
['cmd', 0x54],
['cmd', 0x55],
#3
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0x70],
['cmd', 0x71],#double length
['blank'],
['cmd', 0x72],
#4
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0xfe],
#5
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0xfe],
#6
['cmd', 0xfe],
['cmd', 0xfe],
['cmd', 0xfe],
['flashcmd', 0xfe,0xfe,-1,0xfe,0xfe,-1,0xfe],
['flashcmd', 0xfe,0xfe,0xfe,0x71,0xfe,0xfe,0xfe],
['flashcmd', 0xfe,0xfe,-1,0x13,0x5b,0x4f,0x06],

['cmd', 0xfe],
#
#end
#['flashcmd', #,#,-1,#,#,-1,#],
#['flashcmd', #,#,#,#,#,#,#],
#['flashcmd', #,#,-1,#,#,#,#],
#['cmd', 36],
]

#render frames

for meas_idx, step in enumerate(script[:]):
    if step[0] == 'cmd':
        execute_command(meas_idx, step[1])
    elif step[0] == 'flashcmd':
        for seq_idx, fcmd in enumerate(step[1:]):
            if fcmd >= 0:
                flash_command(meas_idx, fcmd, seq_idx)
        #step[1:] will be commands to flash or 1 to hold
    elif step[0] == 'title':
        green = False
        if len(step) > 3: green = step[3]
        frames.append((meas_idx*measrate, render_title(step[1], '', green)))
        image = render_title(step[1], step[2], green)
        frames.append((meas_idx*measrate+2, image))
        for i in range(4):
            frames.append((meas_idx*measrate+5+i/2, image))
            image = '\n'.join(fade_img(image.split('\n')))

#ending frames

nframe = str(frames[-1][1]).split('\n')
base_time = frames[-1][0]+2+5
for i in range(4): 
    frames.append((base_time+i/4-1, '\n'.join(nframe)))

nframe[-2] = colorama.Fore.GREEN + nframe[-2] + colorama.Fore.RESET
frames.append((base_time-.125, '\n'.join(nframe)))

for i in range(4):
    nframe = fade_img(nframe)
    frames.append((base_time+i/2, '\n'.join(nframe)))

#start playback

pygame.mixer.init(frequency=44100)
music = pygame.mixer.Sound('Title7.ogg')

bpms = [240]*8
beatrate = 60/bpms[0]

epochs = list(np.cumsum([ 7*7*60/x for x in bpms]))
epochs.insert(0,0)

meas_idx = 0

next_time = 0

def map_beat(beat):
    """
    Return the time that the beat happens given the time changes
    """
    epoch = int(beat/49)
    beatoff = beat - epoch*49
    result = epochs[epoch]+beatoff*60/(bpms[epoch])
    return result

start_time = time.time()
music.set_volume(.1)
music.play()


for beat, frame in frames:
    
    next_time = map_beat(beat)

    if True:
        tdelta = next_time - (time.time()-start_time)
        if tdelta > 0:
            time.sleep(tdelta)
        print('')
        print(frame, end='')
            
