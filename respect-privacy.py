#!/usr/bin/python

# Tally, a program to tally archived e-mails and news, by Zoe Blade
# For Python 3
# See README.md for more information

import csv, os, string, sys

configFile = '~/.arcmesgrc'
messageDir = '~/message-archive'

if len(sys.argv) == 2:
	field = sys.argv[1]

if not os.path.exists(os.path.expanduser(configFile)):
	print('Please create configuration file', configFile)
	exit()

# Let's begin!
config = open(os.path.expanduser(configFile))

for line in csv.reader(config, delimiter='\t'):
	if len(line) == 0 or line[0][0] == '#':
		continue

	command = line[0]

	if command == 'DocumentRoot':
		if len(line) != 2:
			continue

		messageDir = line[1]

deletedMessageCount = 0;

for hashDir in os.listdir(os.path.expanduser(messageDir)):
	for hashSubdir in os.listdir(os.path.expanduser(messageDir+'/'+hashDir)):
		for hashFile in os.listdir(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir)):
			messageFile = open(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir+'/'+hashFile), 'r')

			for line in messageFile:
				splitLine = line.split(' ')

				if (splitLine[0][:-1].lower() == 'x-no-archive' and splitLine[1][:-1].lower() == 'yes'):
					os.unlink(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir+'/'+hashFile))
					deletedMessageCount = deletedMessageCount + 1;
					continue

if (deletedMessageCount == 1):
	print('Deleted', deletedMessageCount, 'message')
else:
	print('Deleted', deletedMessageCount, 'messages')
