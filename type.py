import sys
import time
import pygame
from pygame.locals import *

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
36: Cmd(25, []),
37: Cmd(25, []),
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

bgraw = open('bldng_bg.txt','r', encoding='utf-8').read().split('\n')
backgrounds = []
while len(bgraw) > 0:
    backgrounds.append(bgraw[:12])
    bgraw = bgraw[12:]

backgrounds = backgrounds[1:]

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
            next_time += linerate#*beatrate
        elif step > 0: #update background
            image = backgrounds[step]
#            print(f'bg: {step}')
            tframe = render(command, outbuf, image)
            frames.append((next_time, tframe))
#            next_time += linerate#*beatrate
        elif step == -2: #fade out
            pass

    #feed the remaining lines
    while not '>' in lines[line_idx]:
        outbuf.append(lines[line_idx])
        line_idx += 1
        tframe = render(command, outbuf, image)
        frames.append((next_time, tframe))
        next_time += linerate#*beatrate

for j, i in enumerate(range(2,38)):
    execute_command(j, i)
#execute_command(0, 2)

pygame.mixer.init(frequency=44100)
music = pygame.mixer.Sound('Title2.ogg')

start_time = time.time()
music.set_volume(.1)
music.play()

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

for beat, frame in frames:
    
    next_time = map_beat(beat)


    if True:
        tdelta = next_time - (time.time()-start_time)
        print('')
        print(frame, end='')
        if tdelta > 0:
            time.sleep(tdelta)
