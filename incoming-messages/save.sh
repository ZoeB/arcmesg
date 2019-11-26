#!/bin/sh

number=1
filename="~/incoming-messages/${number}.txt"

while [ -f $filename ]; do
	number=$(( $number + 1 ))
	filename="~/incoming-messages/${number}.txt"
done

tee $filename
