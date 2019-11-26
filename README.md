# ArcMesg

ArcMesg is a set of simple tools used to move and manipulate message files, originating from both e-mails and USENET news.  Each message must be stored in a separate file, and will be named after the SHA1 of its universally unique message ID.

## Getting and splitting up messages

Before you can use ArcMesg to collate message files, you should first download some.

### Getting message files via POP3

First, install ```fetchmail```.  Then create the file ```~/.fetchmailrc```, and ```chmod 600 ~/.fetchmailrc```.  Give it the following content:

```
poll pop3.example.com
	protocol pop3
	username "foo"
	password "bar"
	fetchall
	mda ~/incoming-messages/save.sh
```

Change ```pop3.example.com``` to your mail server, ```foo``` to your username, and ```bar``` to your password.  This will cause ```fetchmail```, when you next run it, to pipe each e-mail message, one at a time, to the script ```~/incoming-messages/save.sh``` before deleting it from the mail server.

Next, ```mkdir ~/incoming-messages``` and create the file ```~/incoming-messages/save.sh``` with the following content:

```
#!/bin/sh

number=1
filename="/home/foo/incoming-messages/${number}.txt"

while [ -f $filename ]; do
	number=$(( $number + 1 ))
	filename="/home/foo/incoming-messages/${number}.txt"
done

tee $filename
```

Replace ```foo``` with your username.  ```chmod 755 ~/incoming-messages/save.sh``` so you can execute it.  This script saves each piece of text passed to it in a sequentially numbered file.

Test the script with ```echo 'Test' | ~/incoming-messages/save.sh```.  You should now have a file called ```~/incoming-messages/1.txt``` with the content ```Test```.  If so, delete it, double check your ```~/.fetchmailrc``` file, and run ```fetchmail```.

You should now have several e-mails stored together, one file per e-mail.

<Explain how to get mailing list archives; how to get USENET newsgroup archives; how to split mbox files with git;>

## Usage

Now you're ready to collate and sort your message files.

To use ArcMesg, set up a file in your home directory called ```.arcmesgrc``` with the following information, in tab-separated format:

```
# The optional custom message repository directory
DocumentRoot	~/mesg
```

## To do

* As per RFC 3977 section 8.5, I don't need to get all headers at first, only the Message-ID header, *then* I can retrieve the whole message
* I believe I should read the message headers as ASCII, and only if a Content-Type header is present that specifies an alternative charset should the message then be closed and re-opened using the appropriate charset.  Currently, all messages are opened and processed as ISO-8859-1.  Of course, it would be ideal to ignore the charset entirely, and assume the headers are ASCII and everything else should be preserved as-is without understanding or interpreting it at all.
* Write all kinds of errors to the error log file
* Don't overwrite existing POP3 messages.  Preferably don't get them either.
* Support NNTP's NEWNEWS command
* Port to C
