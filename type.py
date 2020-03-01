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
lines = open(infile, 'r').read().upper().split('\n')
lines = [' ' if len(x) == 0 else x for x in lines]

image = ['█'*58]*12
outbuf, lines = lines[:9], lines[9:]
command = ''
next_time = 0
meas_time = 0

meas_idx = 0

for line in lines:
    if len(line) > 2 and line[2] == '>':
        line = line[4:]

        tframe = render(command, outbuf, image)
        frames.append((meas_time, tframe))

        next_time = meas_time
        meas_time += measrate*beatrate

        meas_idx += 1
        if meas_idx % 7 == 0:
            beatrate = 60/bpms[int(meas_idx/7)]

        while len(line) > 0:
            command += line[0]
            line = line[1:]
            tframe = render(command, outbuf, image)
            frames.append((next_time, tframe))
            next_time += typerate*beatrate

        outbuf.append('> '+command)
        command = ''
    else:
        outbuf.append(line)
        tframe = render(command, outbuf, image)
        frames.append((next_time, tframe))
        next_time += linerate*beatrate

 

pygame.mixer.init(frequency=44100)
music = pygame.mixer.Sound('Title2.ogg')

start_time = time.time()
music.set_volume(.1)
music.play()

#exit()

for next_time, frame in frames:
    tdelta = next_time - (time.time()-start_time)
    print('')
    print(frame, end='')
    if tdelta > 0:
        time.sleep(tdelta)
    pass
