#!/usr/bin/python

import csv, os, poplib

configFile = '~/.arcmailrc'

if not os.path.exists(os.path.expanduser(configFile)):
	print('Please create configuration file', configFile);
	exit()

config = open(os.path.expanduser(configFile))

for line in csv.reader(config, delimiter='\t'):
	if line[0][0] == '#' or len(line) != 3:
		continue;

	server = line[0]
	username = line[1]
	password = line[2]

	connection = poplib.POP3(server)
	connection.user(username)
	connection.pass_(password)
	list = connection.list()

	for emailNumber in list[1]:
		print(connection.retr(emailNumber[0]))
