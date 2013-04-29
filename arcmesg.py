#!/usr/bin/python

# ArcMesg, a program to archive e-mails and news, by Zoe Blade
# For Python 3
# See README.creole for more information

import csv, datetime, hashlib, nntplib, os, poplib, string

configFile = '~/.arcmesgrc'
outputDir = '~/message-archive'

if not os.path.exists(os.path.expanduser(configFile)):
	print('Please create configuration file', configFile)
	exit()

if not os.path.exists(os.path.expanduser(outputDir)):
	os.mkdir(os.path.expanduser(outputDir), 0o755)

def writeMessage(lines):
	for line in lines:
		splitMessageLine = line.decode().split(' ')

		if (splitMessageLine[0] == 'Message-ID:'):
			messageID = splitMessageLine[1][1:-1]
			hashedMessageID = hashlib.sha1(messageID.encode()).hexdigest()

			if downloadLogFile:
				downloadLogFile.write('Downloading message ' + hashedMessageID + ' ' + messageID + '\n')

			hashDir = hashedMessageID[:2]
			hashFile = hashedMessageID[2:]

			if not os.path.exists(os.path.expanduser(outputDir+'/'+hashDir)):
				os.mkdir(os.path.expanduser(outputDir+'/'+hashDir), 0o755)

			messageFile = open(os.path.expanduser(outputDir+'/'+hashDir+'/'+hashFile), 'w')

			for messageLineAgain in lines:
				try:
					messageFile.write(messageLineAgain.decode() + '\n')
				except: # If we can't cope with a message, don't save it
					messageFile.close()
					os.unlink(os.path.expanduser(outputDir+'/'+hashDir+'/'+hashFile))

					if errorLogFile:
						errorLogFile.write('Discarding message ' + messageID + ' (Can\'t decode)\n')

					return

			messageFile.close()
	return

def getMessagesViaNntp(server, group):
	connection = nntplib.NNTP(server)

	try:
		groupInfo = connection.group(group)[0].split(' ')
		firstMessageNumber = int(groupInfo[2])
		lastMessageNumber = int(groupInfo[3])
	except:
		if errorLogFile:
			errorLogFile.write('Discarding group ' + group + ' (Can\'t get list of messages)\n')

		return

	for messageNumber in range(firstMessageNumber, lastMessageNumber + 1):
		try:
			message = connection.article(messageNumber)[1]
			writeMessage(message.lines)
		except:
			if errorLogFile:
				errorLogFile.write('Discarding message ' + str(messageNumber) + ' (Can\'t get message of that number)\n')

	connection.quit()
	return

def getMessagesViaPop3(server, username, password, delete):
	connection = poplib.POP3(server)
	connection.user(username)
	connection.pass_(password)
	list = connection.list()

	for emailNumber in list[1]:
		emailNumberActual = emailNumber.decode().split(' ')[0]
		email = connection.retr(emailNumberActual)
		writeMessage(email[1])

		if (delete == True):
			connection.dele(emailNumberActual)

	connection.quit()
	return

# Let's begin!
downloadLogFile = None
errorLogFile = None

config = open(os.path.expanduser(configFile))

for line in csv.reader(config, delimiter='\t'):
	if len(line) == 0 or line[0][0] == '#':
		continue

	command = line[0]

	if command == 'DownloadLog':
		if len(line) != 2:
			continue

		downloadLogFile = open(os.path.expanduser(line[1]), 'a')

	elif command == 'ErrorLog':
		if len(line) != 2:
			continue

		errorLogFile = open(os.path.expanduser(line[1]), 'a')

	elif command == 'nntp':
		if len(line) != 3:
			continue

		server = line[1]
		group = line[2]
		getMessagesViaNntp(server, group)

	elif command == 'pop3':
		if len(line) < 4 or len(line) > 5:
			continue

		server = line[1]
		username = line[2]
		password = line[3]

		if len(line) > 4 and line[4] == 'delete':
			delete = True
		else:
			delete = False

		getMessagesViaPop3(server, username, password, delete)

if errorLogFile:
	errorLogFile.close()
