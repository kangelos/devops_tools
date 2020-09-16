
#!/bin/bash

SSHPARAMS="-i /home/buildbot/.ssh/id_rsa.rsync -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
SSHDEST="python-packages@python.mydomain.com"
TMPDIR=/tmp/buildbot/$

branch=$1
giturl=$2

if [ "X$branch" == "X" ]
then
	echo "No branch passed"
	exit 1
fi

if [ "X$giturl" == "X" ]
then
	echo "No branch passed"
	exit 1
fi

function finish {
	cd /home/buildbot
	/bin/rm -rf $TMPDIR
	echo "*** cleanup done ***"
}


# sometimes gitlab sends https:// urls not git@
giturl=`echo $giturl | sed -e 's/https:\/\/gitlab.mydomain.com\//git@gitlab.mydomain.com:/g'`
echo "******************** giturl is:$giturl branch is:$branch ********************"

mkdir -p $TMPDIR
cd $TMPDIR

# Exit on error
set -e 
set -x
trap finish EXIT TERM HUP

echo "Setting up python virtualenv under $TMPDIR/venv"
virtualenv $TMPDIR/venv -p python3
source $TMPDIR/venv/bin/activate

#########################################################
#
# dependencies & requirements
#
##########################################################

if [ -f $TMPDIR/thisbuild/setup.py ]
then
	cd $TMPDIR/thisbuild
	echo "******************** Installing dependencies via pip ********************"
	pip install --process-dependency-links  $TMPDIR/thisbuild/
else
	echo "!!!!!!!!!!!!!!!!!!!! No setup.py found !!!!!!!!!!!!!!!!!!!!"
fi

if [ -f $TMPDIR/thisbuild/requirements.txt ]
then
	cd $TMPDIR/thisbuild
	echo "******************** Installing requirements via pip ********************"
	pip install -r  $TMPDIR/thisbuild/requirements.txt
else
	echo "!!!!!!!!!!!!!!!!!!!! No requirements.txt found !!!!!!!!!!!!!!!!!!!!"
fi

#########################################################
#
#  tests
#
##########################################################

if [ -d $TMPDIR/thisbuild/tests ]
then
	cd $TMPDIR/thisbuild
	echo "******************** Running unit tests ********************"
	python -m unittest
else 
	echo "!!!!!!!!!!!!!!!!!!!! No unit tests found !!!!!!!!!!!!!!!!!!!!"
fi

#########################################################
#
#  build & upload
#
##########################################################



if [ -f $TMPDIR/thisbuild/setup.py ]
then
	cd $TMPDIR/thisbuild
	echo "******************** Building the project ********************"
	python setup.py sdist bdist_egg
	if [ $? -ne 0 ]
	then
		echo "!!!!!!!!!!!!!!!!!!!! Build failed !!!!!!!!!!!!!!!!!!!!"
		exit 1
	fi
	# now upload the stuff :-)
	ls -alR dist
	dstdir=$(python3 setup.py --name 2> /dev/null | tail -n 1)
	echo "******************** uploading to $dstdir ********************"
	chmod 644 dist/*
	ssh $SSHPARAMS $SSHDEST mkdir -p files/${dstdir}
        scp $SSHPARAMS dist/* $SSHDEST:files/${dstdir}/
else
	echo "!!!!!!!!!!!!!!!!!!!! No setup.py found !!!!!!!!!!!!!!!!!!!!"
fi

echo "******************** build Job completed ********************"
