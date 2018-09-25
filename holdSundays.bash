#!/usr/local/bin/bash

#Hold snapshots that were taken on Sundays
#date parameters are BSD specific
#

VERBOSE=0
param=$1
if [[ "$param" == "-v" ]]
then
	VERBOSE=1
fi

TAG=Weekly
LC_ALL=C zfs list -t snapshot -o name,creation -H | grep Sun | awk '{ print $1}'|\
while read snapname
do
	tag=$(zfs holds $snapname | grep $TAG)
	if [[ -z "$tag" ]]
	then
		if [[ $VERBOSE == 1 ]]
		then
			echo holding $snapname
		fi
		zfs hold $TAG $snapname
	else
		if [[ $VERBOSE == 1 ]]
		then
			echo Already Tagged:$snapname
		fi
	fi
done
