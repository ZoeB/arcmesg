#!/usr/bin/python

# Convert a message ID to its corresponding hash, by Zoe Blade
# For Python 3
# See README.creole for more information

import mesg, sys

messageIDs = []

for argument in sys.argv:
	if argument[-3:] == '.py':
		continue

	messageIDs.append(argument)

for messageID in messageIDs:
	print(mesg.hashMessageID(messageID))
