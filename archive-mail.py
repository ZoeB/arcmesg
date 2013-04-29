#!/usr/bin/python

import csv, os

configFile = '~/.archive-mail'

if not os.path.exists(os.path.expanduser(configFile)):
	print('Please create configuration file', configFile);
	exit()

config = open(os.path.expanduser(configFile))

for line in csv.reader(config, delimiter='\t'):
	comment = False

	for item in line:
		if item[0] == '#':
			comment = True
			break

	if comment == True:
		comment = False
		continue

	print(line)
