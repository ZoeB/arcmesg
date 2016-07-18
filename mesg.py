# Message module, to manipulate e-mails and USENET messages, by Zoe Blade
# For Python 3
# See README.creole for more information

import csv, datetime, hashlib, nntplib, os, poplib, string, sys

if sys.version_info[0] != 3:
	print('Please use Python 3')
	exit()

def getMessageID(message):
	for line in message:
		# Stop looking for a message ID after reaching the end of the headers and start of the body, to avoid a false positive from a quoted message ID
		if len(line.strip()) == 0:
			return None

		try:
			splitLine = line.decode('latin-1').split(' ')
		except:
			splitLine = line.split(' ')

		if splitLine[0].lower() == 'message-id:':
			if (splitLine[1][-1:] == '\n'): # DOS format messages have CRLF at the end, not just LF.  It looks like the Python line splitter lobs off just the CR or LF, not the whole CRLF.  Compensate for that.
				splitLine[1] = splitLine[1][0:-1]

			return splitLine[1][1:-1]

	return None

def getArchivable(message):
	for line in message:
		try:
			splitLine = line.decode('latin-1').split(' ')
		except:
			splitLine = line.split(' ')

		if splitLine[0].lower() == 'x-no-archive:' and splitLine[1].lower() == 'yes':
			return False

	return True

def hashMessageID(messageID):
	if not messageID:
		return None

	return hashlib.sha1(messageID.encode()).hexdigest()

def messageAlreadyArchived(messageDir, hashedMessageID):
	hashDir = hashedMessageID[:2]
	hashSubdir = hashedMessageID[2:4]
	hashFile = hashedMessageID[4:]
	messageFilename = os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir+'/'+hashFile)
	return os.path.exists(messageFilename)

def writeMessage(messageDir, downloadLogFile, errorLogFile, message, messageBody = None):
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
			os.unlink(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir+'/'+hashFile))

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

def getMessagesViaNntp(messageDir, downloadLogFile, errorLogFile, server, group, username = None, password = None):
	try:
		connection = nntplib.NNTP(server, 119, username, password)
		nntplib._MAXLINE = 65536 # Because some e-mail clients break the spec
	except:
		if errorLogFile:
			errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding server ' + server + ' (Can\'t connect)\n')

	if group[-1] == '*':
		groups = list(connection.descriptions(group)[1].keys())
	else:
		groups = [group]

	for group in groups:
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

			if messageAlreadyArchived(messageDir, hashedMessageID):
				if errorLogFile:
					errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding message ' + messageID + ' (Duplicate)\n')

				continue

			if getArchivable(messageHead.lines) == False:
				if errorLogFile:
					errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding message ' + messageID + ' (X-No-Archive: Yes)\n')

				continue

			try:
				messageBody = connection.body(messageNumber)[1]
			except:
				if errorLogFile:
					errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding message ' + messageID + ' (Can\'t retrieve body)\n')

				continue

			writeMessage(messageDir, downloadLogFile, errorLogFile, messageHead.lines, messageBody.lines)

	connection.quit()
	return

def getMessagesViaPop3(messageDir, downloadLogFile, errorLogFile, server, username, password, delete, limit):
	try:
		connection = poplib.POP3(server)
		poplib._MAXLINE = 65536 # Because some e-mail clients break the spec
		connection.user(username)
		connection.pass_(password)
		list = connection.list()
	except poplib.error_proto as detail:
		if errorLogFile:
			errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding server ' + server + ' (Can\'t connect): ' + detail.args[0].decode('latin-1') + '\n')

		return

	messagesRetrieved = 0

	for emailNumber in list[1]:
		emailNumberActual = emailNumber.decode('latin-1').split(' ')[0]

		try:
			email = connection.retr(emailNumberActual)
		except:
			if errorLogFile:
				errorLogFile.write(str(datetime.datetime.utcnow())[:-7] + ' Discarding e-mail ' + emailNumberActual + ' (Can\'t retrieve)\n')

			continue

		writeMessage(messageDir, downloadLogFile, errorLogFile, email[1])

		if delete == True:
			connection.dele(emailNumberActual)

		messagesRetrieved = messagesRetrieved + 1

		if messagesRetrieved == limit:
			break

	connection.quit()
	return
