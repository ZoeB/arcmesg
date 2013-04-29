#!/usr/bin/python

import csv, os

configFile = '~/.arcmailrc'

if not os.path.exists(os.path.expanduser(configFile)):
	print('Please create configuration file', configFile);
	exit()

config = open(os.path.expanduser(configFile))

for line in csv.reader(config, delimiter='\t'):
	if line[0][0] == '#' or len(line) != 3:
		continue;

	for item in line:
		print(item)
