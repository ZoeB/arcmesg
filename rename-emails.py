#!/usr/bin/python

# Rename e-mail files to their message ID, by Zoe Blade
# For Python 3

import re, os

for filename in os.listdir('.'):
	if not os.path.isfile(filename):
		continue

	file = open(filename, 'r', 1, 'iso-8859-1')
	messageIDs = 0

	for line in file:
		result = re.search('Message-ID: <([^>]+)>', line, flags=re.IGNORECASE)

		if result and result.group(1) and '@' in result.group(1):
			messageIDs += 1
			messageID = result.group(1)

	if messageIDs == 1:
		os.rename(filename, messageID + '.eml')
