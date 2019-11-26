#!/usr/bin/python

# Import, a program to archive single message files, by Zoe Blade
# For Python 3
# See README.md for more information

import csv, glob, hashlib, mesg, os, string, sys

configFile = '~/.arcmesgrc'
messageDir = '~/message-archive'
deleteDuplicates = False
verbosity = 'Normal'

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
	if argument[-3:] == '.py':
		continue

	if argument == '--delete-duplicates':
		deleteDuplicates = True
		continue

	if argument == '--terse':
		verbosity = 'Terse'
		continue

	filenames = glob.glob(argument)

	for filename in filenames:
		inputFilenames.append(filename)

# Try to import each file in turn
for inputFilename in inputFilenames:
	file = open(inputFilename, 'r', 1, 'iso-8859-1')
	message = file.readlines()
	messageID = mesg.getMessageID(message)

	if verbosity == 'Terse':
		sys.stdout.flush() # Really, this should be at the end of the loop, but I don't want to duplicate it before each continue

	if mesg.getArchivable(message) == False:
		if verbosity == 'Terse':
			sys.stdout.write('X')
		else:
			print('Deleting ' + inputFilename + '; not archivable (x-no-archive: yes)')

		os.remove(inputFilename)
		continue

	if messageID:
		hash = mesg.hashMessageID(messageID)
	else:
		hash = mesg.hashMessage(message)

	if mesg.messageAlreadyArchived(messageDir, hash):
		if verbosity == 'Terse':
			sys.stdout.write('D') # Duplicate
		else:
			if deleteDuplicates == True:
				print('Deleting ' + inputFilename + '; already in collection')
			else:
				print('Skipping ' + inputFilename + '; already in collection')

		if deleteDuplicates == True:
			os.remove(inputFilename)

		continue

	# This duplicates some of mesg.py, which is bad practice
	hashDir = hash[:2]
	hashSubdir = hash[2:4]
	hashFile = hash[4:]
	messageFilename = os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir+'/'+hashFile)

	if not os.path.exists(os.path.expanduser(messageDir)):
		os.mkdir(os.path.expanduser(messageDir), 0o755)

	if not os.path.exists(os.path.expanduser(messageDir+'/'+hashDir)):
		os.mkdir(os.path.expanduser(messageDir+'/'+hashDir), 0o755)

	if not os.path.exists(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir)):
		os.mkdir(os.path.expanduser(messageDir+'/'+hashDir+'/'+hashSubdir), 0o755)

	os.rename(inputFilename, messageFilename)

	if verbosity == 'Terse':
		sys.stdout.write('.')
	else:
		print('Imported ' + inputFilename)

if verbosity == 'Terse':
	print()
