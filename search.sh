#!/bin/bash

echo "Search query?"
read string

find * -type f | xargs grep -i "$string"
