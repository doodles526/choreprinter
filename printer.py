#!/bin/python

from escpos.printer import Usb
import textwrap
import math
from PIL import Image, ImageDraw, ImageFont

p = Usb(0x4b8, 0x0202, profile="TM-T88V")

"""
"title": Title
"note": note (optional)
"assigned_to" Person who should do it
"date_assigned" Date
"finish_by": Finish by date/time
"""

def do_line_wrap(text, font, width):
    scrapImg = Image.new('RGB', (1,1), "white")
    scrapDraw = ImageDraw.Draw(scrapImg)

    bbox = scrapDraw.multiline_textbbox((0,0), text, font=font, align="center")

    bbox_w = bbox[2]

    if bbox_w <= width:
        return text

    num_lines = math.ceil(bbox_w/float(width))

    char_wrapping_bottom = math.floor(len(text)/num_lines)
    char_wrapping_top = math.ceil(len(text)/(num_lines-1))

    # TODO: Binary search for efficiency
    while char_wrapping_top > char_wrapping_bottom:
        lines = "\n".join(textwrap.wrap(text, width=char_wrapping_top))
        bbox = scrapDraw.multiline_textbbox((0,0), lines, font=font, align="center")
        if bbox[2] <= width:
            return lines
        char_wrapping_top-=1
    
def assignee_text(assigned_to):
    return ''.join(("Hi ", assigned_to, ". Here's something for you to do :)"))

def total_heights(text_data, spacing):
    img = Image.new('RGB', (1, 1), "white")
    draw = ImageDraw.Draw(img)

    h = spacing*(len(text_data)-1)

    for d in text_data:
        local_height = draw.multiline_textbbox((0,0), d[0], font=d[1], align="center", spacing=d[2])[3]
        h += local_height
        d.append(local_height)

    print(h)

    return h


def create_todo_image(todo):
    """
    Creates a PIL Image object from a todo dictionary.
    """
    title_font = ImageFont.truetype("/usr/share/fonts/TTF/RobotoMonoNerdFont-Medium.ttf", 40)
    other_font = ImageFont.truetype("/usr/share/fonts/TTF/RobotoMonoNerdFont-Medium.ttf", 30)
    note_font = ImageFont.truetype("/usr/share/fonts/TTF/RobotoMonoNerdFont-Medium.ttf", 20)

    title_lines = do_line_wrap(todo["title"], title_font, 512)
    note_lines = do_line_wrap(todo["note"], note_font, 512)
    assigned_lines = do_line_wrap(assignee_text(todo["assigned_to"]), other_font, 512)

    all_data = [[assigned_lines, other_font, 5], [title_lines, title_font, 10], [note_lines, note_font, 5]]

    prodImg = Image.new('RGB', (512, total_heights(all_data, 20)), "white")
    prodDraw = ImageDraw.Draw(prodImg)

    curH = 0

    for data in all_data:
        print(data)
        prodDraw.multiline_text((0, curH), data[0], font=data[1], align="center", spacing=data[2], fill="black")
        curH += data[3] + 20
    
    return prodImg

def print_image(img):
    """
    Sends a PIL image to the printer and performs a cut.
    """
    p.image(img)
    p.cut()

def image_from_todo(todo):
    """
    Convenience method to create and print a todo image.
    """
    img = create_todo_image(todo)
    print_image(img)


