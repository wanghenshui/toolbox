#!/usr/bin/env python
import sys
import re

f = sys.stdin
# use stdin if it's full
if not sys.stdin.isatty():
    f = sys.stdin
else:
    try:
        input_filename = sys.argv[1]
    except IndexError:
        message = 'need filename as first argument if stdin is not full'
        raise IndexError(message)
    else:
        f = open(input_filename, 'r')

lines = f.readlines() 
for line in lines:
    data = re.findall("\[(.*?)\]",line, re.I|re.M)
    if len(data) > 2:
        print("UnlockKey -lock_key {0} -lock_owner {1}".format(data[0], data[1]))
    else:
        print(data)
