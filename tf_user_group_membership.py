#!/usr/bin/env python3
"""
import existing AWS IAM group memberships into terrafrom
"""
import sys

with open(sys.argv[1]) as rdx:
    while True:
        line=rdx.readline().rstrip()
        if line == '':
            break
        (user,groups)=line.split(":")
        if groups == '':
            continue
        groups=groups.split(" ")

        print("""
resource "aws_iam_user_group_membership" "%s" {
    user =  aws_iam_user.%s.name
    groups = [
  """ % (user, user), end="")
        for g in groups:
            print("\t\taws_iam_group.%s.name," % g)
        print("      ]\n}")
        print("#terraform import aws_iam_user_group_membership.%s %s/" %(user,user),end="")
        print("/".join(groups))

