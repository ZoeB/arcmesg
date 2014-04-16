#!/bin/bash

echo "Search query?"
read string

for outerDir in ??
do
	for innerDir in $outerDir/??
	do
		for file in $innerDir/*
		do
			result=$(grep "$string" $file)

			if [ ${#result} -ne 0 ]; then
				echo $file $result
			fi
		done
	done
done
