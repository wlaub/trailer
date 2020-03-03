import sys
import time
import pygame
from pygame.locals import *

import colorama

colorama.init()

#12 image lines
#9 text lines
#1 command lines


window = """┌──────────────────────────────────────────────────────────┐
│█                                                        █│
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
│█                                                        █│
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
linerate = 0.5
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
1: Cmd(0, []),
2: Cmd(0, [-1, 2, -1, 3, -1, 4]),
3: Cmd(0, []),
4: Cmd(0, []),
5: Cmd(0, [5]),
6: Cmd(5, [-1, 7, -1, 8, -1, 9]),
7: Cmd(5, [-1,-2,-1,10]),
8: Cmd(10, []),
9: Cmd(10, []),
10: Cmd(10, []),
11: Cmd(10, []),
12: Cmd(10, [-1,-2,-1,11]),
13: Cmd(11, [12]),
14: Cmd(12, [13]),
15: Cmd(13, [14]),
16: Cmd(14, [15]), #scramble this
17: Cmd(15, [16]),
18: Cmd(16, [17]),
19: Cmd(17, [18]),
20: Cmd(18, [-1,-2,-1,10]),
21: Cmd(10, []),
22: Cmd(10, []),
23: Cmd(10, []),
24: Cmd(10, [19]),
25: Cmd(19, []),
26: Cmd(19, [-1,-2,-1,18]),
27: Cmd(18, [20]),
28: Cmd(20, [-1,-2,-1,19]),
29: Cmd(19, [21]),
30: Cmd(21, [-1,-2,-1,22]),
31: Cmd(22, []),
32: Cmd(22, []),
33: Cmd(22, []),
34: Cmd(22, [-1,23,-2,-1,24]),
35: Cmd(24, [-1,-2,-1,25]),
36: Cmd(25, [-1,-2]),
37: Cmd(25, []), #TODO: Change this
}

frames = []

def render(command, outbuf, image_lines):

    nlines = outbuf.count('\n') + 1
    out_lines = outbuf[-9:]

    out_frame = list(window)
    for idx, line in enumerate(out_lines):
        out_frame[idx+14] = line + window[idx+14][len(line):]

    for idx, line in enumerate(image_lines):
        out_frame[idx+1] = window[idx+1][0] + line + window[idx+1][len(line)+1:]

    out_frame[-1] = '> '+ command
    return '\n'.join(out_frame)

infile = sys.argv[1]
lines = open(infile, 'r', encoding='utf-8').read().upper().split('\n')
lines = [' ' if len(x) == 0 else x for x in lines]

#map command numbers to line numbers
command_index = {}
for idx, line in enumerate(lines):
    if '>' in line:
        command_index[int(line[:2])] = idx

#strip command numbers
lines = list(map(lambda x: x if not '>' in x else x[2:], lines))

lines_base = lines

#load backgrounds
bgraw = open('bldng_bg.txt','r', encoding='utf-8').read().split('\n')
backgrounds = []
while len(bgraw) > 0:
    backgrounds.append(bgraw[:12])
    bgraw = bgraw[12:]

backgrounds = backgrounds[1:]

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

def execute_command(meas_idx, cmd_idx):
    #
    meas_time = meas_idx*measrate
    next_time = meas_time

    start_idx = command_index[cmd_idx]

    image = backgrounds[commands[cmd_idx].bg_idx]
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
        elif step > 0: #update background
            image = backgrounds[step]
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
['title', "wrn'ng", ' '], #todo: trailer intro
['title', 'this', "trl'r"], #this trailer
['title', 'is', 'not'], #is not
['title', 'canon', ' ', True], #canon todo: green
['cmd', 6],
['cmd', 7],
['title', 'this', "sum'r"],
#1
['cmd', 9],
['cmd', 10],
['cmd', 11],
['cmd', 12],
['cmd', 13],
['cmd', 14],
['title', 'defy', "norm'l"],
#2
['cmd', 16],
['cmd', 17],
['cmd', 18],
['cmd', 19],
['cmd', 20],
['cmd', 21],
['title', 'b', 'tough'],
#3
['cmd', 23],
['cmd', 24],
['cmd', 25],
['cmd', 26],
['cmd', 27],
['cmd', 28],
['title', 'b', 'sexy'],
#4
['cmd', 30],
['cmd', 31],
['cmd', 32],
['cmd', 33],
['cmd', 34],
['cmd', 35],
['cmd', 36],
#end
['cmd', 37],
]

for meas_idx, step in enumerate(script):
    if step[0] == 'cmd':
        execute_command(meas_idx, step[1])
    elif step[0] == 'title':
        green = False
        if len(step) > 3: green = step[3]
        frames.append((meas_idx*measrate, render_title(step[1], '', green)))
        image = render_title(step[1], step[2], green)
        frames.append((meas_idx*measrate+2, image))
        for i in range(4):
            frames.append((meas_idx*measrate+5+i/2, image))
            image = '\n'.join(fade_img(image.split('\n')))


#for j, i in enumerate(range(2,38)):
#    execute_command(j, i)
#execute_command(0, 2)

pygame.mixer.init(frequency=44100)
music = pygame.mixer.Sound('Title2.ogg')

#exit()
import numpy as np

bpms = [100, 100, 120, 140, 160, 180]
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
            
