import logging
import math
import time
import re
import os

from PIL import Image, ImageDraw, ImageFont

from otter_buddy.constants import FONT_PATH

logger = logging.getLogger(__name__)

# Based on RFC 5322 Official Standard
# Ref: https://www.ietf.org/rfc/rfc5322.txt
email_regex: str = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

def time_format(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return days, hours, minutes, seconds


def pretty_time_format(seconds, *, shorten=False, only_most_significant=False, always_seconds=False):
    days, hours, minutes, seconds = time_format(seconds)
    timespec = [
        (days, 'day', 'days'),
        (hours, 'hour', 'hours'),
        (minutes, 'minute', 'minutes'),
    ]
    timeprint = [(cnt, singular, plural) for cnt, singular, plural in timespec if cnt]
    if not timeprint or always_seconds:
        timeprint.append((seconds, 'second', 'seconds'))
    if only_most_significant:
        timeprint = [timeprint[0]]

    def format_(triple):
        cnt, singular, plural = triple
        return f'{cnt}{singular[0]}' if shorten else f'{cnt} {singular if cnt == 1 else plural}'

    return ' '.join(map(format_, timeprint))


def is_valid_email(email: str) -> bool:
    if(re.search(email_regex, email)):   
        return True  
    else:   
        return False


def get_size(txt: str, font) -> (int, int):
    testImg = Image.new('RGB', (1, 1))
    testDraw = ImageDraw.Draw(testImg)
    return testDraw.textsize(txt, font)

def create_match_image(week_otter_pairs: list) -> (Image, str):

    first_list, second_list = zip(*week_otter_pairs)
    first_column = "\n".join(list(map(lambda user: f"{user.name}#{user.discriminator}", first_list)))
    second_column = "\n".join(list(map(lambda user: f"{user.name}#{user.discriminator}", second_list)))
    
    colorText = "black"
    colorOutline = "gray"
    colorBackground = "white"

    fontsize = 16
    font = ImageFont.truetype(FONT_PATH, fontsize)

    width, height = get_size(first_column, font)
    width2, _height2 = get_size(second_column, font)
    img = Image.new('RGB', ((width + width2)+100, (height)+20), colorBackground)
    d = ImageDraw.Draw(img)
    d.text((5,5), first_column, fill=colorText, font=font)
    d.text((width+55,5), second_column, fill=colorText, font=font)
    d.rectangle((0, 0, width+50, height+20), outline=colorOutline)
    d.rectangle((width+50, 0, (width + width2)+100, height+20), outline=colorOutline)

    path = os.path.dirname(os.path.realpath(__file__)) + "/image.png"    
    img.save(path)

    return img, path
