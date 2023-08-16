#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Set up Cross Region Replication for AWS S3 buckets
The program  creates ${bucket}-replica in the target_region
creates the necessary roles and polices and enables replication
Variable naming convention:
    bucket the source bucket
    target the target bucket
'''
import logging
import json
import sys
import pprint
import uuid
import time
import boto3
import botocore
from botocore.config import Config

# the manifests and reports buckets
CONTROL = "arn:aws:s3:::-s3crr-control"

# Array of buckets to replicate
# bucket: target region
bucket_to_replicate_to_region = {
    "test":   "eu-west-1",
}

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
pp = pprint.PrettyPrinter(indent=4)
iam = boto3.client('iam')
s3 = boto3.resource('s3')

def get_account_id():
    client = boto3.client("sts")
    return client.get_caller_identity()["Account"]


def get_policy_arn(policy_name):
    accountId = get_account_id()
    return(f'arn:aws:iam::{accountId}:policy/{policy_name}')
    ''' Slow but necessary '''
    logging.info(f'Locating ARN for policy {policy_name}')
    paginator = iam.get_paginator('list_policies')
    all_policies = [policy for page in paginator.paginate()
                    for policy in page['Policies']]
    [policy_1] = [p for p in all_policies if p['PolicyName'] == policy_name]
    return (policy_1["Arn"])


def create_replication_policy(bucket, target):
    '''
    creates a per bucket pair policy to allow for replication
    '''

    assume_role_policy_document = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "s3:ListBucket",
                    "s3:GetReplicationConfiguration",
                    "s3:GetObjectVersionForReplication",
                    "s3:GetObjectVersionAcl",
                    "s3:GetObjectVersionTagging",
                    "s3:GetObjectRetention",
                    "s3:GetObjectLegalHold",
                    "s3:PutInventoryConfiguration",
                    "s3:InitiateReplication",
                    "s3:PutInventoryConfiguration",
                    "s3:GetObject",
                    "s3:GetObjectAcl",
                    "s3:GetObjectTagging",
                    "s3:ListBucket",
                ],
                "Effect": "Allow",
                "Resource": [
                    f'arn:aws:s3:::{bucket}',
                    f'arn:aws:s3:::{bucket}/*',
                    f'arn:aws:s3:::{target}',
                    f'arn:aws:s3:::{target}/*',
                    CONTROL,
                    f'{CONTROL}/*',
                ]
            },

            {
                "Action": [
                    "s3:PutInventoryConfiguration",
                    "s3:PutBucketInventoryConfiguration",
                    "s3:GetObjectVersion",
                    "s3:GetObject",
                    "s3:PutObject",
                ],
                "Effect": "Allow",
                "Resource": [
                    CONTROL,
                    f'{CONTROL}/*',
                ]
            },

            {
                "Action": [
                    "s3:ReplicateObject",
                    "s3:ReplicateDelete",
                    "s3:ReplicateTags",
                    "s3:GetObjectVersionTagging",
                    "s3:ObjectOwnerOverrideToBucketOwner",
                    "s3:PutObject",
                    "s3:PutObjectAcl",
                    "s3:PutObjectTagging",
                ],
                "Effect": "Allow",
                "Resource": [
                    f'arn:aws:s3:::{bucket}/*',
                    f'arn:aws:s3:::{target}/*',
                ]
            },
        ]
    })

    # debug ?
    # print(assume_role_policy_document)

    policy_name = f's3crr-for-{target}'
    try:
        policyresponse = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=assume_role_policy_document % (
                bucket, bucket, target, target, bucket, target),
            Description=f'policy to allow replication from {bucket} to {target}'
         )
    except:
        logging.error("Could not Create IAM policy, maybe already there")
        pass

    return (policy_name)


def create_replication_role(target):
    '''
    Uses the above policy plus the trust relationship to create the necessary 
    replication role per bucket pair
    '''
    role_name = f's3crr-for-{target}'
    try:
        roleresponse = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "batchoperations.s3.amazonaws.com",
                                "s3.amazonaws.com"
                            ]
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }),
            Description='For replication purposes',
        )
    except:
        logging.error("Could not Create role, maybe already there")
        pass

    return (role_name)


def insert_replication(client, bucket, target, role_arn):
    '''
    finally insert the replication rules to the source bucket
    '''
    target_bucket_arn = f'arn:aws:s3:::{target}'
    logging.info(f'Inserting replication for the bucket "{bucket}" ')
    replconfig = {
        'Role': role_arn,
        'Rules': [
            {
                'ID': 'Replication',
                'Priority': 1,
                'Status': 'Enabled',
                "Filter": {},
                "Destination": {
                    'Bucket': target_bucket_arn,
                    "Metrics": {
                        "Status": "Enabled",
                        "EventThreshold": {
                            "Minutes": 15
                        }
                    },
                    "ReplicationTime": {
                        "Status": "Enabled",
                        "Time": {
                            "Minutes": 15
                        }
                    },
                },
                "DeleteMarkerReplication": {
                    "Status": "Enabled"
                },
            }
        ]
    }

    replresp = client.put_bucket_replication(
        Bucket=bucket,
        ReplicationConfiguration=replconfig,
    )
    logging.info(f'Replication setup for {bucket} ready')
    return (replresp)


def create_bucket(target, target_region):
    '''
    create target bucket
    '''
    # s3 client is very finnicky about regions and access points
    my_config = Config(
        region_name=target_region,
    )
    client = boto3.client('s3', config=my_config)
    client.create_bucket(
        Bucket=f'{target}',
        CreateBucketConfiguration={
            'LocationConstraint': target_region,
        },
    )
    # We do not care for public access for the replicated data
    logging.info(f'Blocking Public Access for the target bucket "{target}" ')
    client.put_public_access_block(
        Bucket=f'{target}',
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        },
    )
    logging.info(f'Creating versioning for the target bucket "{target}" ')
    client.put_bucket_versioning(
        Bucket=f'{target}',
        VersioningConfiguration={
            'Status': 'Enabled'
        },
    )


def setup_replication(bucket, target_region):
    '''
    steps:
        enable versioning on source bucket
        create target bucket
        setup the replication policy
        setup the replicatoin role
        attach the replication polixy to the role
        finally
        insert the replication itself
    Note: a bucket can have multiple replication entities
    '''
    client = boto3.client('s3')

    logging.info(f'Bucket "{bucket}" : enabling versioning')
    client.put_bucket_versioning(
        Bucket=bucket,
        VersioningConfiguration={
            'Status': 'Enabled'
        },
    )
    # CREATE TARGET BUCKET
    logging.info('Creating Target Bucket')
    try:
        s3.meta.client.head_bucket(Bucket=target)
    except botocore.exceptions.ClientError:
        # The bucket does not exist or you have no access.
        create_bucket(target, target_region)

    # Checking if config was created and skipping if not needed
    logging.info('Creating replication policy')
    replication_policy_name = create_replication_policy(bucket, target)
    policy_arn = get_policy_arn(replication_policy_name)
    logging.info(f'Policy arn:{policy_arn}')

    logging.info(f'Creating replication role')
    role_name = create_replication_role(target)
    logging.info(f'role name:{role_name}')

    response = iam.get_role(RoleName=role_name)
    role_arn = response['Role']['Arn']
    logging.info(f'Role arn is:{role_arn}')

    response = iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )
    logging.info(
        f'Attached replication policy {replication_policy_name} to role {role_name}')

    # Finally Insert the replication to the bucket
    replresp = insert_replication(client, bucket, target, role_arn)
    logging.info(f'Replication setup for {bucket} ready')
    return ((role_arn, replresp))


def create_batch_job(bucket, role_arn):
    """
    This is the final step in the process
    this batch job will replicate existing data 
    from the source bucket to the target bucket
    """
    s3ControlClient = boto3.client('s3control')
    accountId = get_account_id()
    RequestToken = str(uuid.uuid4())
    bucket_arn = f'arn:aws:s3:::{bucket}'

    response = s3ControlClient.create_job(
        AccountId=accountId,
        ConfirmationRequired=False,
        RoleArn=role_arn,
        Operation={
            "S3ReplicateObject": {}
        },
        Report={
            "Bucket": CONTROL,
            "Format": "Report_CSV_20180820",
            "Enabled": True,
            "ReportScope": "AllTasks",
        },
        ManifestGenerator={
            "S3JobManifestGenerator": {
                "SourceBucket": bucket_arn,
                "ExpectedBucketOwner": accountId,
                "EnableManifestOutput": True,
                "ManifestOutputLocation": {
                    "Bucket": CONTROL,
                    "ManifestFormat": "S3InventoryReport_CSV_20211130",
                },
                "Filter": {
                    "EligibleForReplication": True,
                    "ObjectReplicationStatuses": ["NONE", "FAILED"]
                },
            }
        },
        Description=time.strftime('%Y-%m-%d')+' - replication job',
        Priority=1,
        ClientRequestToken=RequestToken
    )
    return (response)


# Main
if __name__ == '__main__':
    client = boto3.client('s3')
    for bucket in bucket_to_replicate_to_region:
        target_region = bucket_to_replicate_to_region[bucket]
        target = "replica-%s" % bucket

        # GET REPLICATION
        logging.info('=' * 80)
        logging.info(f'Working for S3 Bucket:{bucket}')
        try:
            config = client.get_bucket_replication(Bucket=bucket)
            # repl_setup = pp.pformat(config['ReplicationConfiguration'])
            logging.info(f'bucket:{bucket} already has a replication config')
        except botocore.exceptions.ClientError:
            (role_arn, config) = setup_replication(bucket, target_region)
            RequestId=config['ResponseMetadata']['RequestId']
            logging.info(
                f'bucket {bucket} new replication config created: {RequestId} ')
            # Now create the batch job to replicate everything
            response = create_batch_job(bucket, role_arn)
            JobId=response['JobId']
            logging.info(f'Created batch replication job: {JobId} ')
