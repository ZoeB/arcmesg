#!/bin/bash

echo "Search query?"
read string
filename=$(echo $string | tr -c '[:alnum:]\n' '-')

find ?? -type f | xargs grep -ils "$string" | xargs tar cf "$filename.tar"
