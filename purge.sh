#!/bin/sh

find ?? -type f | xargs grep -il 'X-No-Archive: Yes' | xargs rm
