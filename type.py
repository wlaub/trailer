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

bpms = [100, 100, 120, 140, 160, 180]
beatrate = 60/bpms[0]

typerate = 0.25
linerate = 0.5
measrate = 7



def render(command, outbuf, image_lines):

    nlines = outbuf.count('\n') + 1
    out_lines = outbuf[-9:]

    out_frame = list(window)
    for idx, line in enumerate(out_lines):
        out_frame[idx+14] = line + window[idx+14][len(line):]

    for idx, line in enumerate(image_lines):
        out_frame[idx+1] = window[idx+1][0] + line + window[idx+1][len(line)+1:]

    out_frame[-1] = '> '+ command
    print('')
    print('\n'.join(out_frame), end='')

infile = sys.argv[1]
lines = open(infile, 'r').read().upper().split('\n')
lines = [' ' if len(x) == 0 else x for x in lines]

image = ['█'*58]*12
outbuf, lines = lines[:9], lines[9:]
command = ''
next_time = time.time()

pygame.mixer.init(frequency=44100)
music = pygame.mixer.Sound('Title2.ogg')

meas_idx = 0

start_time = time.time()
music.set_volume(.1)
music.play()
for line in lines:
    if line[0] == '>':
        line = line[2:]
        render(command, outbuf, image)

        tdelta = start_time+(meas_idx%7)*measrate*beatrate - time.time()
        if tdelta > 0:
            time.sleep(tdelta)
        meas_idx += 1
        if meas_idx % 7 == 0:
            start_time += 7*measrate*beatrate
            beatrate = 60/bpms[int(meas_idx/7)]

        while len(line) > 0:
            command += line[0]
            line = line[1:]
            render(command, outbuf, image)
            time.sleep(typerate*beatrate)
        outbuf.append('> '+command)
        command = ''
#        outbuf += '\n'
    else:
        outbuf.append(line)
        render(command, outbuf, image)
        time.sleep(linerate*beatrate)
 


