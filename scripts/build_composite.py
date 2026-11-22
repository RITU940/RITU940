#!/usr/bin/env python3
"""Combine locally stored illustrated GIF frames into the GitHub profile art.

Edit labels, colors, text, timings here. No third-party badges or runtime services.
Requires Pillow only if you want to regenerate the artwork. Published GIFs work as-is.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT/'assets'
CHARACTERS = ASSETS/'characters'
INK = '#2e2b2a'
RUST = '#a96350'
SAGE = '#6c7762'
PAPER = '#f6ecdf'
LINE = '#c9b9a5'
FONT_BOLD = '/usr/share/fonts/truetype/lato/Lato-Heavy.ttf'
FONT_REG = '/usr/share/fonts/truetype/lato/Lato-Regular.ttf'
FONT_ITALIC = '/usr/share/fonts/truetype/lato/Lato-Italic.ttf'
FONT_MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'


def font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def read_frames(path: Path):
    im = Image.open(path)
    return [frame.convert('RGBA') for frame in __import__('PIL').ImageSequence.Iterator(im)]


def save_gif(frames, target: Path, duration=170):
    target.parent.mkdir(parents=True, exist_ok=True)
    # RGB frames avoid GIF transparency problems and have broad GitHub support.
    pal = [f.convert('RGB').quantize(colors=180, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE) for f in frames]
    pal[0].save(target, save_all=True, append_images=pal[1:], duration=duration,
                loop=0, disposal=2, optimize=True)
    print(f'Wrote {target.relative_to(ROOT)} ({target.stat().st_size // 1024} KiB)')


def make_hero(src):
    W,H=1100,550
    art=src
    cycle=list(range(len(art)))+list(range(len(art)-2,0,-1))
    out=[]
    steps=22
    for k in range(steps):
        canvas=Image.new('RGB',(W,H),PAPER)
        d=ImageDraw.Draw(canvas)
        # small imperfect journal lines / bookish style
        for yy in (40,518):
            d.line([(42,yy),(564,yy)],fill=LINE,width=2)
        d.text((56,55),'MY LITTLE CORNER OF GITHUB',font=font(FONT_MONO,15),fill=RUST)
        d.line((56,87,342,87),fill=RUST,width=2)
        d.arc((492,48,555,120),start=220,end=540,fill=SAGE,width=3)
        d.line([(515,110),(524,119),(539,103)],fill=SAGE,width=3)
        d.text((56,129),'hey,',font=font(FONT_BOLD,91),fill=INK)
        d.text((56,224),"i'm Ritu.",font=font(FONT_BOLD,86),fill=RUST)
        d.text((58,332),'an electronics student who',font=font(FONT_REG,27),fill=INK)
        d.text((58,369),'keeps ending up in other',font=font(FONT_REG,27),fill=INK)
        d.text((58,406),"people's codebases.",font=font(FONT_ITALIC,28),fill=INK)
        # notes written by a real developer, rather than flashy faux-dashboard badges
        for x,y,ww,txt,fg in ((58,470,89,'JU 2028',INK),(158,470,130,'ISI Kolkata',INK),(300,470,173,'open source <3',SAGE)):
            d.rounded_rectangle((x,y,x+ww,y+31),radius=8,fill='#ecdfcc',outline='#d6c6b3',width=1)
            d.text((x+10,y+7),txt,font=font(FONT_MONO,13),fill=fg)
        # right-hand illustrated scene, keeping original animated character consistency
        scene=art[cycle[k%len(cycle)]].resize((489,H),Image.Resampling.LANCZOS).convert('RGB')
        canvas.paste(scene,(611,0))
        d.line([(603,0),(603,H)],fill='#e3d1ba',width=7)
        # organic page fold divider
        for yy in range(18,H,36):
            d.ellipse((604,yy,609,yy+5),fill=RUST)
        out.append(canvas)
    save_gif(out,ASSETS/'hero-ritu.gif',duration=145)
    out[0].save(ROOT/'preview'/'Hero_First_Frame.png')


def make_character_stickers(src):
    # cropped directly from the same illustrated animation: no mismatch of character style
    items=[('cat', (224,208,380,396),'the supervisor'),
           ('robot',(255,69,409,230),'the assistant'),
           ('oscilloscope',(314,287,477,451),'the signal')]
    for name, crop, label in items:
        output=[]
        for i,im in enumerate(src):
            canvas=Image.new('RGB',(214,229),PAPER)
            d=ImageDraw.Draw(canvas)
            d.rounded_rectangle((7,7,207,220),radius=12,fill='#fbf6ee',outline=LINE,width=2)
            section=im.crop(crop)
            section=ImageOps.fit(section,(190,177),method=Image.Resampling.LANCZOS,centering=(.5,.45)).convert('RGB')
            canvas.paste(section,(12,12))
            d.line([(26,198),(49,198)],fill=RUST,width=2)
            d.text((60,191),label,font=font(FONT_ITALIC,16),fill=INK)
            # hand-drawn motion accent
            if i%3==1:
                d.line([(180,192),(184,187),(189,188)],fill=RUST,width=2)
            output.append(canvas)
        save_gif(output,CHARACTERS/f'{name}.gif',duration=230)


if __name__=='__main__':
    src=read_frames(ASSETS/'electronics-lab.gif')
    (ROOT/'preview').mkdir(exist_ok=True)
    make_hero(src)
    make_character_stickers(src)
