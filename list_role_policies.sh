#!/bin/bash
Roles=$(aws iam list-roles | jq -r .Roles[].RoleName | grep -v Amazon )
for g in $Roles
do
  policies=$(aws iam  list-role-policies --role-name $g | jq -r .PolicyNames[])
  if [[ "$policies" == "" ]]
  then
    continue
  fi

  for p in $policies
  do
    pname=$(echo $p | sed -e 's/\./_/g')
    echo "resource \"aws_iam_role_policy\" \"$pname\" {
  name = \"$p\"
  role = aws_iam_role.$g.id
}
  #terraform import aws_iam_role_policy.${pname} $g:$p
  #terraform state show aws_iam_role_policy.${pname} 
  "
  done

done

echo "Remember to do a tf plan when done importing"

