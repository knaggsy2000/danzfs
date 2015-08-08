#!/bin/sh

SNAPSHOT_DATE="`date +%Y%m%d-%H%M`"
SNAPSHOT_PREFIX="AS"
SNAPSHOTS_TO_TAKE="mypool"


for POOL_SNAPSHOT in $SNAPSHOTS_TO_TAKE
do
	echo "Taking snapshot for filesystem $POOL_SNAPSHOT as @$SNAPSHOT_DATE..."
	zfs snapshot $POOL_SNAPSHOT@$SNAPSHOT_PREFIX-$SNAPSHOT_DATE
done
