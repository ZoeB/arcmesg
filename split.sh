#!/bin/bash

for mbox in *.mbox
do
	mkdir ${mbox}.split
	git mailsplit -o${mbox}.split ${mbox}
done
