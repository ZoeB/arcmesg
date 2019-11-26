# Message module, to manipulate e-mails and USENET messages, by Zoe Blade
# For Python 3
# See README.md for more information

import csv, datetime, hashlib, os, string, sys

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

def hashMessage(message):
	if not message:
		return None

	return 'xx'+hashlib.sha1(''.join(message).encode()).hexdigest()[2:]

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
