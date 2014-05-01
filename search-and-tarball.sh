#!/bin/bash

echo "Search query?"
read string

find * -type f | xargs grep -ls "$string" | xargs tar cf "$string.tar"
