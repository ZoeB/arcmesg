#!/usr/bin/python

# Import, a program to archive single message files, by Zoe Blade
# For Python 3
# See README.creole for more information

import csv, glob, hashlib, mesg, os, string, sys

configFile = '~/.arcmesgrc'
messageDir = '~/message-archive'

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

# Pop all the input filenames into one easy-to-manage list (array)
inputFilenames = []

for argument in sys.argv:
	filenames = glob.glob(argument)

	for filename in filenames:
		inputFilenames.append(filename)

# Try to import each file in turn
for inputFilename in inputFilenames:
	file = open(inputFilename, 'r')
	message = file.readlines()
	messageID = mesg.getMessageID(message)

	if mesg.getArchivable(message) == False:
		print('Skipping ' + inputFilename + '; not archivable (x-no-archive: yes)')
		continue

	if not messageID:
		print('Skipping ' + inputFilename + '; no message ID')
		continue

	hashedMessageID = mesg.hashMessageID(messageID)

	if mesg.messageAlreadyArchived(messageDir, hashedMessageID):
		print('Skipping ' + inputFilename + '; already in collection')
		continue

	# This duplicates some of mesg.py, which is bad practice
	hashDir = hashedMessageID[:2]
	hashSubdir = hashedMessageID[2:4]
	hashFile = hashedMessageID[4:]
	messageFilename = os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir+'/'+hashFile)

	if not os.path.exists(os.path.expanduser(messageDir)):
		os.mkdir(os.path.expanduser(messageDir), 0o755)

	if not os.path.exists(os.path.expanduser(messageDir+'/'+hashDir)):
		os.mkdir(os.path.expanduser(messageDir+'/'+hashDir), 0o755)

	if not os.path.exists(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir)):
		os.mkdir(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir), 0o755)

	os.rename(inputFilename, messageFilename)
	print('Imported ' + inputFilename)
