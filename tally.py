#!/usr/bin/python

# Tally, a program to tally archived e-mails and news, by Zoe Blade
# For Python 3
# See README.creole for more information

import csv, os, string, sys

configFile = '~/.arcmesgrc'
messageDir = '~/message-archive'
field = 'Newsgroups'

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

newsgroups = {}

for hashDir in os.listdir(os.path.expanduser(messageDir)):
	for hashSubdir in os.listdir(os.path.expanduser(messageDir+'/'+hashDir)):
		for hashFile in os.listdir(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir)):
			messageFile = open(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir+'/'+hashFile), 'r')

			for line in messageFile:
				splitLine = line.split(' ')

				if (splitLine[0][:-1] == field):
					for messageNewsgroup in splitLine[1][:-1].split(','):
						if messageNewsgroup in newsgroups:
							newsgroups[messageNewsgroup] = newsgroups[messageNewsgroup] + 1
						else:
							newsgroups[messageNewsgroup] = 1

for newsgroup, tally in newsgroups.items():
	print(newsgroup, tally)
