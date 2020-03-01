from PIL import Image
from PIL import GifImagePlugin

image = Image.open('bldng.gif')
outfile = 'bldng_bg.txt'

print(image.n_frames)

colormap = {
(64,64,64): '\u2591',
(128,128,128): '\u2592',
(192,192,192): '\u2588',
#(192,192,192): '█',
(0,0,255): '\u25a0',
(0,64,0): '\u2591',
(0,255,255): ',',
(0,0,0): ' ',
(255,0,0): 'X',
}

print(colormap)

text_frame = []
for frame_idx in range(image.n_frames):
    image.seek(frame_idx)
    frame = image.convert('RGB')
    for y in range(12):
        line = ''
        for x in range(58):
            color = frame.getpixel((2*x,3*y))
            line += colormap[color]

        text_frame.append(line)

print('\n'.join(text_frame))
open(outfile, 'w', encoding='utf-8').write('\n'.join(text_frame))

