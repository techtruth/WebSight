#!/bin/bash

rm -f output.somoclu*
/usr/local/bin/somoclu -v 2 -k 1 -e $4 -x $2 -y $3 $1 output.somoclu

