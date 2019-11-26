#!/bin/sh

fetchmail
python3 ~/Programs/arcmesg/import.py *.txt
