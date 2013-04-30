#!/usr/bin/python

# ArcMesg, a program to archive e-mails and news, by Zoe Blade
# For Python 3
# See README.creole for more information

import csv, datetime, hashlib, nntplib, os, poplib, string

configFile = '~/.arcmesgrc'
messageDir = '~/message-archive'

if not os.path.exists(os.path.expanduser(configFile)):
	print('Please create configuration file', configFile)
	exit()

def writeMessage(lines):
	for line in lines:
		splitMessageLine = line.decode().split(' ')

		if (splitMessageLine[0] == 'Message-ID:'):
			messageID = splitMessageLine[1][1:-1]
			hashedMessageID = hashlib.sha1(messageID.encode()).hexdigest()

			if downloadLogFile:
				downloadLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' ' + messageID + '\n')

			hashDir = hashedMessageID[:2]
			hashSubdir = hashedMessageID[2:4]
			hashFile = hashedMessageID[4:]

			if not os.path.exists(os.path.expanduser(messageDir)):
				os.mkdir(os.path.expanduser(messageDir), 0o755)

			if not os.path.exists(os.path.expanduser(messageDir+'/'+hashDir)):
				os.mkdir(os.path.expanduser(messageDir+'/'+hashDir), 0o755)

			if not os.path.exists(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir)):
				os.mkdir(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir), 0o755)

			messageFile = open(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir+'/'+hashFile), 'w')

			for messageLineAgain in lines:
				try:
					messageFile.write(messageLineAgain.decode() + '\n')
				except: # If we can't cope with a message, don't save it
					messageFile.close()
					os.unlink(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashFile))

					if errorLogFile:
						errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding message ' + messageID + ' (Can\'t decode)\n')

					return

			messageFile.close()
	return

def getMessagesViaNntp(server, group):
	try:
		connection = nntplib.NNTP(server)
	except:
		if errorLogFile:
			errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding server ' + server + ' (Can\'t connect)\n')

	try:
		groupInfo = connection.group(group)[0].split(' ')
		firstMessageNumber = int(groupInfo[2])
		lastMessageNumber = int(groupInfo[3])
	except:
		if errorLogFile:
			errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding group ' + group + ' (Can\'t get list of messages)\n')

		return

	for messageNumber in range(firstMessageNumber, lastMessageNumber + 1):
		try:
			message = connection.article(messageNumber)[1]
			writeMessage(message.lines)
		except:
			if errorLogFile:
				errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding message ' + str(messageNumber) + ' in ' + group + ' (Can\'t get message of that number)\n')

	connection.quit()
	return

def getMessagesViaPop3(server, username, password, delete):
	try:
		connection = poplib.POP3(server)
		connection.user(username)
		connection.pass_(password)
		list = connection.list()
	except:
		if errorLogFile:
			errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding server ' + server + ' (Can\'t connect)\n')

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
			if len(line) != 4:
				continue

			server = line[2]
			group = line[3]
			getMessagesViaNntp(server, group)

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

			getMessagesViaPop3(server, username, password, delete)

if errorLogFile:
	errorLogFile.close()
