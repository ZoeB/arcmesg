#!/usr/bin/python

import csv, hashlib, os, poplib, string

configFile = '~/.arcmailrc'
outputDir = '~/email-archive'

if not os.path.exists(os.path.expanduser(configFile)):
	print('Please create configuration file', configFile)
	exit()

if not os.path.exists(os.path.expanduser(outputDir)):
	os.mkdir(os.path.expanduser(outputDir), 0o755)

config = open(os.path.expanduser(configFile))

for line in csv.reader(config, delimiter='\t'):
	if line[0][0] == '#' or len(line) != 3:
		continue

	server = line[0]
	username = line[1]
	password = line[2]

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
				# connection.dele(emailNumber[0])
				break
