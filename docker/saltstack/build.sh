#!/bin/bash

#
# build the docker images and start the test environment
# angelos@unix.gr
#

echo "Cleaning Up"
docker rm -f salt-master
for minion in 1 2 3
do
 docker rm -f salt-minion${minion}
done

echo "Building Master Image"
echo "Copying my ssh credentials to be used for git"
mkdir -p creds 2> /dev/null
cp $HOME/.ssh/id_rsa creds/
cp $HOME/.ssh/known_hosts creds/
cp $HOME/.gitconfig creds/gitconfig

docker build . 2>&1 | tee master.log
id=`grep 'Successfully built' master.log | cut -d" " -f 3`
if [ "X${id}" == "X" ]
then
 echo "Salt Master build failed"
 exit 1
fi
docker run -d \
 -h salt-master --name salt-master \
 -v $PWD/bath:/srv/salt \
 -v $PWD/pillar:/srv/pillar \
 --memory-swappiness=1 $id

docker tag -f ${id} salt-master

echo "Building Minion image"
docker build -f Dockerfile.minion . 2>&1 | tee minion.log
id=`grep 'Successfully built' minion.log | cut -d" " -f 3`

if [ "X${id}" == "X" ]
then
 echo "Salt Minion build failed"
 exit 1
fi
for minion in 1 2 3
do
 hash=`docker run -d \
 -h salt-minion${minion} --name=salt-minion${minion} \
 --link salt-master \
 --memory-swappiness=1 $id`
 docker tag -f ${id} salt-minion${minion}
done

docker ps
