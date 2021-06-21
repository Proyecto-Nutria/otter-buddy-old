from otter_buddy.utils.common import *

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