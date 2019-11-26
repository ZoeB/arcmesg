# ArcMesg

ArcMesg is a set of simple tools used to move and manipulate message files, originating from both e-mails and USENET news.  Each message must be stored in a separate file, and will be named after the SHA1 of its universally unique message ID.

## Getting and splitting up messages

Before you can use ArcMesg to collate message files, you should first download some.

<Explain how to get mailing list archives; how to get USENET newsgroup archives; how to split mbox files with git; how to fetch POP3 e-mails to different files with fetchmail>

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
