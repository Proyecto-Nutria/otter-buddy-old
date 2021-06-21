import time

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
