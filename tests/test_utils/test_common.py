import time

from PIL import Image, ImageDraw, ImageFont

import discord
import discord.ext.test as dpytest

from otter_buddy.utils.common import *

FONT_PATH = "tests/fonts/OpenSans-Regular.ttf"

def test_time_format_seconds():
    seconds = 1
    days, hours, minutes, seconds = time_format(seconds)
    assert days == 0
    assert hours == 0
    assert minutes == 0
    assert seconds == 1

def test_time_format_minutes():
    seconds = 60
    days, hours, minutes, seconds = time_format(seconds)
    assert days == 0
    assert hours == 0
    assert minutes == 1
    assert seconds == 0

def test_time_format_hour():
    seconds = 3600
    days, hours, minutes, seconds = time_format(seconds)
    assert days == 0
    assert hours == 1
    assert minutes == 0
    assert seconds == 0

def test_time_format_days():
    seconds = 86400
    days, hours, minutes, seconds = time_format(seconds)
    assert days == 1
    assert hours == 0
    assert minutes == 0
    assert seconds == 0

def test_time_format():
    seconds = 192625
    days, hours, minutes, seconds = time_format(seconds)
    assert days == 2
    assert hours == 5
    assert minutes == 30
    assert seconds == 25

def test_time_format_zero():
    seconds = 0
    days, hours, minutes, seconds = time_format(seconds)
    assert days == 0
    assert hours == 0
    assert minutes == 0
    assert seconds == 0

def test_pretty_time_format_seconds():
    seconds = 0
    time = pretty_time_format(seconds)
    expected = "0 seconds"
    assert time == expected
    time = pretty_time_format(seconds, shorten=True)
    expected = "0s"
    assert time == expected

    # Singular
    seconds = 1
    time = pretty_time_format(seconds)
    expected = "1 second"
    assert time == expected

    # Plural
    seconds = seconds * 2
    time = pretty_time_format(seconds)
    expected = "2 seconds"
    assert time == expected

def test_pretty_time_format_minutes():
    # Singular
    seconds = 60
    time = pretty_time_format(seconds)
    expected = "1 minute"
    assert time == expected

    # Plural
    seconds = seconds * 2
    time = pretty_time_format(seconds)
    expected = "2 minutes"
    assert time == expected

    time = pretty_time_format(seconds, shorten=True)
    expected = "2m"
    assert time == expected

    time = pretty_time_format(seconds, always_seconds=True)
    expected = "2 minutes 0 seconds"
    assert time == expected

    time = pretty_time_format(seconds, shorten=True, always_seconds=True)
    expected = "2m 0s"
    assert time == expected

def test_pretty_time_format_hours():
    # Singular
    seconds = 3600
    time = pretty_time_format(seconds)
    expected = "1 hour"
    assert time == expected

    # Plural
    seconds = seconds * 2
    time = pretty_time_format(seconds)
    expected = "2 hours"
    assert time == expected

    time = pretty_time_format(seconds, shorten=True)
    expected = "2h"
    assert time == expected

    time = pretty_time_format(seconds, always_seconds=True)
    expected = "2 hours 0 seconds"
    assert time == expected

    time = pretty_time_format(seconds, shorten=True, always_seconds=True)
    expected = "2h 0s"
    assert time == expected

def test_pretty_time_format_days():
    # Singular
    seconds = 86400
    time = pretty_time_format(seconds)
    expected = "1 day"
    assert time == expected

    # Plural
    seconds = seconds * 2
    time = pretty_time_format(seconds)
    expected = "2 days"
    assert time == expected

    time = pretty_time_format(seconds, shorten=True)
    expected = "2d"
    assert time == expected

    time = pretty_time_format(seconds, always_seconds=True)
    expected = "2 days 0 seconds"
    assert time == expected

    time = pretty_time_format(seconds, shorten=True, always_seconds=True)
    expected = "2d 0s"
    assert time == expected

def test_time_format():
    # Singular
    seconds = 90061
    time = pretty_time_format(seconds)
    expected = "1 day 1 hour 1 minute"
    assert time == expected
    time = pretty_time_format(seconds, always_seconds=True)
    expected = "1 day 1 hour 1 minute 1 second"
    assert time == expected

    # Plural
    seconds = seconds * 2
    time = pretty_time_format(seconds)
    expected = "2 days 2 hours 2 minutes"
    assert time == expected
    time = pretty_time_format(seconds, always_seconds=True)
    expected = "2 days 2 hours 2 minutes 2 seconds"
    assert time == expected

    time = pretty_time_format(seconds, shorten=True)
    expected = "2d 2h 2m"
    assert time == expected

    time = pretty_time_format(seconds, shorten=True, always_seconds=True)
    expected = "2d 2h 2m 2s"
    assert time == expected

    time = pretty_time_format(seconds, only_most_significant=True)
    expected = "2 days"
    assert time == expected

    time = pretty_time_format(seconds, shorten=True, only_most_significant=True)
    expected = "2d"
    assert time == expected

def test_valid_email():
    email = "Test00@test.com"
    assert is_valid_email(email)

def test_valid_email_underscore():
    email = "my_Test00_11@test.com"
    assert is_valid_email(email)

def test_valid_email_minus():
    email = "my-Test00-11@test.com"
    assert is_valid_email(email)

def test_valid_email_dot():
    email = "my.Test00.11@test.com"
    assert is_valid_email(email)

def test_valid_email_dot():
    email = "my.Test00.11@test.com"
    assert is_valid_email(email)

def test_valid_email_country():
    email = "my.Test00.11@test.com.mx"
    assert is_valid_email(email)

def test_valid_email_custom_domain():
    email = "my.Test00.11@custom-domain.com"
    assert is_valid_email(email)

def test_phrase_as_email():
    email = "This is a test"
    assert not is_valid_email(email)

def test_incomplete_email():
    email = "test"
    assert not is_valid_email(email)

    email = "test@"
    assert not is_valid_email(email)

    email = "test@test"
    assert not is_valid_email(email)

    email = "test@test."
    assert not is_valid_email(email)

    email = "test.com"
    assert not is_valid_email(email)

def test_invalid_email():
    email = "test!@test.com"
    assert not is_valid_email(email)

    email = "test@test!.com"
    assert not is_valid_email(email)

    email = "test@test.com!"
    assert not is_valid_email(email)

def test_get_size():
    text = "This is a test!"
    size = 16
    font = ImageFont.truetype(FONT_PATH, size)
    width, height = get_size(text, font)
    assert width == 96
    assert height == 18

    size = 10
    font = ImageFont.truetype(FONT_PATH, size)
    width, height = get_size(text, font)
    assert width == 60
    assert height == 11

    text = text + "\n" + text
    width, height = get_size(text, font)
    assert width == 60
    assert height == 26

def test_create_match_image():
    expected_partial_path = "otter_buddy/utils/image.png"
    expected_colors = sorted([
        (398, (128, 128, 128)),
        (412, (0, 0, 0)),
        (11768, (255, 255, 255))
    ])

    week_otter_pairs = [
        (dpytest.backend.make_user("test1", "0001"), dpytest.backend.make_user("test2", "0002")),
        (dpytest.backend.make_user("test3", "0003"), dpytest.backend.make_user("test4", "0004")),
        (dpytest.backend.make_user("test5", "0005"), dpytest.backend.make_user("test6", "0006"))
    ]

    img, path = create_match_image(week_otter_pairs)
    assert expected_partial_path in path

    img_colors = sorted(img.getcolors())
    assert img_colors[-3:] == expected_colors
