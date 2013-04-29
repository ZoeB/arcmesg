#!/usr/bin/python

# ArcMail, a program to archive e-mails, by Zoe Blade
# Instructions:
# Make a file ~/.arcmesgrc
# Give it a list of POP3 accounts in the format:
# protocol\tservername\tusername\tpassword
# You can add comments by beginning a line with a # symbol
# Run this script periodically with a cron job
# The e-mails will be downloaded, stored in a Git-like hierarchy of files,
# and deleted from the POP3 server.
# Use the -d argument for debug mode, to avoid deleting e-mails.
# This program is intended to be used with its own e-mail accounts,
# which aren't shared with real e-mail clients.  It comes without warranty.
# Please don't blame me if your e-mails go missing!

import csv, datetime, hashlib, nntplib, os, poplib, string, sys

debug = False

for argument in sys.argv:
	if (argument == '-d'):
		debug = True
		break

configFile = '~/.arcmesgrc'
outputDir = '~/message-archive'

if not os.path.exists(os.path.expanduser(configFile)):
	print('Please create configuration file', configFile)
	exit()

if not os.path.exists(os.path.expanduser(outputDir)):
	os.mkdir(os.path.expanduser(outputDir), 0o755)

def getMessagesViaNntp(server, group, debug):
	connection = nntplib.NNTP(server)
	groupInfo = connection.group(group)[0].split(' ')
	firstMessageNumber = int(groupInfo[2])
	lastMessageNumber = int(groupInfo[3])

	for messageNumber in range(firstMessageNumber, lastMessageNumber + 1):
		message = connection.article(messageNumber)[1]

		for messageLine in message.lines:
			messageLine = messageLine.decode()
			print(messageLine)

	connection.quit()
	return

def getMessagesViaPop3(server, username, password, debug):
	connection = poplib.POP3(server)
	connection.user(username)
	connection.pass_(password)
	list = connection.list()

	for emailNumber in list[1]:
		emailNumberActual = emailNumber.decode().split(' ')[0]
		email = connection.retr(emailNumberActual)

		for emailLine in email[1]:
			splitEmailLine = emailLine.decode().split(' ')

			if (splitEmailLine[0] == 'Message-ID:'):
				messageID = splitEmailLine[1][1:-1]
				hashedMessageID = hashlib.sha1(messageID.encode()).hexdigest()
				print('Downloading message', hashedMessageID)
				hashDir = hashedMessageID[:2]
				hashFile = hashedMessageID[2:]

				if not os.path.exists(os.path.expanduser(outputDir+'/'+hashDir)):
					os.mkdir(os.path.expanduser(outputDir+'/'+hashDir), 0o755)

				emailFile = open(os.path.expanduser(outputDir+'/'+hashDir+'/'+hashFile), 'w')

				for emailLineAgain in email[1]:
					emailFile.write(emailLineAgain.decode()+'\n')

				emailFile.close()

				if (debug == False):
					connection.dele(emailNumberActual)

				break

	connection.quit()
	return

config = open(os.path.expanduser(configFile))

for line in csv.reader(config, delimiter='\t'):
	if line[0][0] == '#':
		continue

	protocol = line[0]
	if protocol == 'nntp':
		if len(line) != 3:
			continue

		server = line[1]
		group = line[2]
		getMessagesViaNntp(server, group, debug)

	if protocol == 'pop3':
		if len(line) != 4:
			continue

		server = line[1]
		username = line[2]
		password = line[3]
		getMessagesViaPop3(server, username, password, debug)
