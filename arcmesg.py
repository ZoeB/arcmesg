#!/usr/bin/python

# ArcMesg, a program to archive e-mails and news, by Zoe Blade
# For Python 3
# See README.creole for more information

import csv, datetime, hashlib, mesg, nntplib, os, poplib, string

configFile = '~/.arcmesgrc'
messageDir = '~/message-archive'

if not os.path.exists(os.path.expanduser(configFile)):
	print('Please create configuration file', configFile)
	exit()

# Let's begin!
downloadLogFile = None
errorLogFile = None

config = open(os.path.expanduser(configFile))

for line in csv.reader(config, delimiter='\t'):
	if len(line) == 0 or line[0][0] == '#':
		continue

	command = line[0]

	if command == 'DocumentRoot':
		if len(line) != 2:
			continue

		messageDir = line[1]

	elif command == 'DownloadLog':
		if len(line) != 2:
			continue

		downloadLogFile = open(os.path.expanduser(line[1]), 'a')

	elif command == 'ErrorLog':
		if len(line) != 2:
			continue

		errorLogFile = open(os.path.expanduser(line[1]), 'a')

	elif command == 'Pull':
		if len(line) < 4:
			continue

		protocol = line[1]

		if protocol == 'nntp':
			if len(line) == 4:
				mesg.getMessagesViaNntp(messageDir, downloadLogFile, errorLogFile, line[2], line[3])
			elif len(line) == 6:
				mesg.getMessagesViaNntp(messageDir, downloadLogFile, errorLogFile, line[2], line[5], line[3], line[4])
			else:
				pass

		elif protocol == 'pop3':
			if len(line) < 5 or len(line) > 6:
				continue

			server = line[2]
			username = line[3]
			password = line[4]

			if len(line) > 5 and line[5] == 'delete':
				delete = True
			else:
				delete = False

			mesg.getMessagesViaPop3(messageDir, downloadLogFile, errorLogFile, server, username, password, delete)

if downloadLogFile:
	downloadLogFile.close()

if errorLogFile:
	errorLogFile.close()
