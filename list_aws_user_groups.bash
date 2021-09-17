#!/bin/bash
users=$(aws iam list-users | jq -r .Users[].UserName)
for user in $users
do
  groups=$(aws iam list-groups-for-user --user-name $user | jq -r .Groups[].GroupName)
  echo -n $user":"
  echo $groups
done
