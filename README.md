# devops_tools and various little tools



You got the code , read it

 
* [ansible_tasks](ansible_tasks.py): Batch ansible tasks remotely using rabbitmq as a queueing system.
* [taskify](taskify.py): Conditional decorator for [kuyruk](https://kuyruk.readthedocs.io/en/latest/) to allow imports INTO other modules.
* [sendfile](sendfile.py): Use Rabbitmq to send small files to remote hosts behind firewalls.
* [holdSundays](holdSundays.bash):	Place a hold to ZFS snapshots on Sundays.
* [PowerDNS SOA autoupdate](powerdns_SOA_Autoupdate.psql): Increase a zone's serial number on update for powerDNS.
* [swiss_dormant](swiss_dormant.pl):	Scrape the Swiss federal database for dormant accounts.
* [runME](runme.py): A Generic python popen with proper ordering of stdout and stderr.
* [revvy](revvy/): A universal reverse ssh tunnel in 46 lines of scripts/configs.
* [impinjfirm.py](impinjfirm.py): retrieve the firmware version of an impinj rfid reader.
* [joiner](joiner.py): convert multiline logs into digestible RS docs, ingest 500 at a time.
* [λ-alerts](lambda_function.py): Post aws SNS alerts and events to SLACK.
* [QR](read_qr.py) , a QR scanner for the Greek govnmt vaccination cert. Not a proper place for it , but I had to put it some place.
* [kafkalag](kafkalag.sh): Drill down and Identify kafka lag issues.
* [λ-cloudtrail2elastic](lambda_cloudtrail2elastic):  poh sre's serverless cloudtrail ingestion to elasticsearch .
* [waf2elastic](waf2elastic.py): Read AWS WAF logs from an S3 bucket and feed them in batches to an ELK cluster.
* [mqtt-panel](mqtt-panel/): A fork of  Fabian Affolter' mqtt-panel, severely abused to make it work for Dingtian devices.
* [bridger](bridger.sh): Po'boys kuberbnetes VPN. Access pod IPs, service IPs and kube-dns entries from your laptop.
* [chaosmonkey](chaosmonkey/): A 1 1/2 bash script kubernetes chaosmonkey helm chart. No dependencies, not even for an image!
* [onlyaws](onlyaws.sh): Is your openvpn GW forcing all of your traffic through it but you only need it for AWS work ?
* [s3replicate](s3replicate.py): AWS S3 CRR complete python code
  

# Importing user group membership into terraform


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
  If you have any errors like usernames with periods, please hand edit the manifest

Look for more complicated tools @ https://managenot.wordpress.com/
