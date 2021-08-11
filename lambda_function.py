"""
python lambda function to post SNS events _and_ alerts to a slack channel
angelos Jul 21
"""
import json
import urllib3

SLACK_URL = "https://hooks.slack.com/services/.../../..."
DEBUG = 0
UNWANTED_EVENTS = [
        'has the parameter innodb_file_per_table set to 1',
        ]


def lambda_handler(event, context):
    """
    Receive an event and post to slack channel
    do not send if in unwanted messages
    """
    http = urllib3.PoolManager()
    jstext = json.loads(event['Records'][0]['Sns']['Message'])
    stext = json.dumps(jstext, indent=4)   # give it some nice new lines
    for unwmsg in UNWANTED_EVENTS:
        if unwmsg in stext:
            print("Unwanted message will not post to slack: '%s'" % stext)
            return

    msg = {
        "channel": "#aws_alerts",
        "username": "AWS cloudwatch",
        "icon_emoji": ":warning:",
        "text": stext
    }

    encoded_msg = json.dumps(msg).encode('utf-8')
    resp = http.request('POST', SLACK_URL, body=encoded_msg)
    # just in case we need to trace an error
    print({
        "message": stext,
        "status_code": resp.status,
        "response": resp.data
    })


if __name__ == '__main__':
    """
    If you run this code from the CLI it will just test the lambda_function.
    Please setup your lambda to call lambda_handler
    """
    context = "some value"
    # test for a unwanted message
    UNWANTED_EVENT = """ {
       "Event Source": "db_instance",
       "Event Time": "2021-08-03 08:30:30.333",
       "Identifier Link": "https://console.aws.amazon.com/rds/home?region=us-west-2#dbinstance:id=demo8",
       "Source ID": "demo8",
       "Source ARN": "arn:aws:rds:us-west-2:0XXXXXXXXXXX:db:demo8",
       "Event ID": "http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Events.html#RDS-EVENT-0055",
       "Event Message": "DB Instance demo8 has a large number of tables and has the parameter innodb_file_per_table set to 1, which can increase database recovery time significantly. Consider setting this parameter to 0 in the parameter group associated with this DB instance to minimize database downtime during reboots and failovers. This DB Instance also contains MyISAM tables that have not been migrated to InnoDB. These tables can impact your ability to perform point-in-time restores. Consider converting these tables to InnoDB. Please refer to http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.BackingUpAndRestoringAmazonRDSInstances.html#Overview.BackupDeviceRestrictions"
    } """
    ev = {'Records': {0: {'Sns': {'Message': UNWANTED_EVENT}}}}
    if DEBUG:
        jtext = json.loads(ev['Records'][0]['Sns']['Message'])
        text = json.dumps(jtext, indent=4)
        print(text)
    lambda_handler(ev, context)

    # now test for a wanted message
    WANTED_EVENT = """
    {
        "ElastiCache:SnapshotComplete": "this-or-that-elasticache"
    }
    """
    ev['Records'][0]['Sns']['Message'] = WANTED_EVENT
    if DEBUG:
        jtext = json.loads(ev['Records'][0]['Sns']['Message'])
        text = json.dumps(jtext, indent=4)
        print(text)
    lambda_handler(ev, context)
