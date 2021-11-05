# devops_tools and various little tools



You got the code , read it

 
*	ansible_tasks.py 	Batch ansible tasks remotely using rabbitmq as a queueing system
* taskify.py. Conditaional decorator for kuyruk lib to allow imports INTO other modules
*	sendfile.py 	Another batch send of small files to remote hosts behind forewalls using rabbitmq as a queueing system
*	holdSundays.bash 	bash script to place a hold on ZFS snapshots on Sundays
*	powerdns_SOA_Autoupdate.psql 	Increase a zone's serial number on update for powerDNS
*	swiss_dormant.pl 	Scrape the Swiss federal database for dormant accounts
* runme.py. A Generic python popen with proper ordering of stdout and stderr
* revvy: A reverse ssh tunnel in 46 lines of scripts/configs
* impinjfirm.py: retrieve the firmware version of an impinj rfid reader
* joiner.py: convert multiline logs into digestible RS docs, ingest 500 at a time 
* lambda_function.py Post aws SNS alerts and events to SLACK
* read_qr.py , a QR scanner for the Greek govnmt vaccination cert. Not a proper place for it , but I had to put it some place
* kafkalag.sh Identify kafka lag issues
* lambda_cloudtrail2elastic:  poh sre's cloudtrail ingestion to elasticsearch


# Importing user group membership into terraform

It is an incredible pain to import manually crufted groups, users and memberships into terraform
The basic idea is that you create the terraform manifest and then you import every entry as per the documentation

basic assumptions
* You have existing manisfests for users
* You have existing manisfests for groups

now the way to do the import is 
  bash list_aws_user_groups.bash > groups.txt
  python3 tf_user_group_membership.py > user_group_membership.tf

  terraform plan 
should now attempt to re-create all the group memberships for you. But fear not, the marvelous script creates your import command for you.
  grep import user_group_membership.tf > toexecute
  edit and remove the hashes
  bash toexecute

Wait and see



Note:
  If you have any errors like usersnames with periods, please hand edit the manifest

Look for more complicated tools @ https://managenot.wordpress.com/
