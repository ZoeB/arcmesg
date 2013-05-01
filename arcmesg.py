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

def getMessageID(message):
	for line in message:
		splitMessageLine = line.decode('latin-1').split(' ')

		if (splitMessageLine[0] == 'Message-ID:'):
			return splitMessageLine[1][1:-1]

	return None

def hashMessageID(messageID):
	if not messageID:
		return None

	return hashlib.sha1(messageID.encode()).hexdigest()

def messageAlreadyArchived(hashedMessageID):
	hashDir = hashedMessageID[:2]
	hashSubdir = hashedMessageID[2:4]
	hashFile = hashedMessageID[4:]
	messageFilename = os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir+'/'+hashFile)
	return os.path.exists(messageFilename)

def writeMessage(message, messageBody = None):
	messageID = getMessageID(message)

	if not messageID:
		return None

	hashedMessageID = hashMessageID(messageID)

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

	try:
		messageFile = open(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir+'/'+hashFile), 'w')
	except:
		if errorLogFile:
			errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding message ' + messageID + ' (Can\'t write file)\n')

		return None

	for line in message:
		try:
			messageFile.write(line.decode('latin-1') + '\n')
		except: # If we can't cope with a message, don't save it
			messageFile.close()
			os.unlink(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashFile))

			if errorLogFile:
				errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding message ' + messageID + ' (Can\'t decode)\n')

			return None

	if not messageBody:
		messageFile.close()
		return None

	messageFile.write('\n')

	for line in messageBody:
		try:
			messageFile.write(line.decode('latin-1') + '\n')
		except: # If we can't cope with a message, don't save it
			messageFile.close()
			os.unlink(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashFile))

			if errorLogFile:
				errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding message ' + messageID + ' (Can\'t decode)\n')

			return None

	messageFile.close()
	return None

def getMessagesViaNntp(server, username = None, password = None, group = None):
	if group == None: #TODO: implement automatic ripping of all groups on the server (and "groups" with wildcards for that matter, eg sci.*)
		return None

	try:
		connection = nntplib.NNTP(server, 119, username, password)
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
		message = None
		messageHead = None

		try:
			messageHead = connection.head(messageNumber)[1]
		except:
			if errorLogFile:
				errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding message ' + str(messageNumber) + ' in ' + group + ' (Can\'t get message of that number)\n')

			continue

		messageID = getMessageID(messageHead.lines)

		if not messageID:
			if errorLogFile:
				errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding message ' + str(messageNumber) + ' in ' + group + ' (Can\'t find message ID)\n')

			continue

		hashedMessageID = hashMessageID(messageID)

		if messageAlreadyArchived(hashedMessageID):
			if errorLogFile:
				errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding message ' + messageID + ' (Duplicate)\n')

			continue

		messageBody = connection.body(messageNumber)[1]
		writeMessage(messageHead.lines, messageBody.lines)

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
		emailNumberActual = emailNumber.decode('latin-1').split(' ')[0]
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
			if len(line) < 3 or len(line) > 6:
				continue

			server = line[2]
			username = None
			password = None
			group = None

			if len(line) == 6:
				username = line[3]
				password = line[4]
				group = line[5]
			elif len(line) == 5:
				username = line[3]
				password = line[4]
			elif len(line) == 4:
				group = line[3]

			getMessagesViaNntp(server, username, password, group)

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
