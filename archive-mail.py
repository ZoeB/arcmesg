#!/usr/bin/python

import os

configFile = '~/.archive-mail'

if not os.path.exists(os.path.expanduser(configFile)):
	print('Please create configuration file', configFile);
	exit()

config = open(os.path.expanduser(configFile))

for line in config:
	if line[0] == '#':
		continue

	print(line)
