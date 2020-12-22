#!/usr/bin/env python3

#
# Raw monthly AWS cost by service per account angelos@unix.gr
# run with -s to skip refunds
#

import argparse
import boto3
import datetime
import sys

def byprice(x):
    return(x[1])


def period():
    """
    report period we have to calculate which dates are last months start and end
    """
    days=[31,28,31,30,31,30,31,31,30,31,30,31]
    # ok ok leap years are a problem!
    year = int(datetime.datetime.utcnow().strftime("%Y"))
    month = int(datetime.datetime.utcnow().strftime("%m"))
    if month == 1:
        year -= 1
        month = 12
    else:
        month -= 1
    start = "%d-%d-01" % (year, month)
    end = "%d-%d-%02d" % (year, month, days[month-1])
    return(start,end)



def accounting(start, end):
    # to use a specific profile e.g. 'default'
    session = boto3.session.Session(profile_name='default')
    cd = session.client('ce', 'us-west-2')

    results = []
    token = None
    while True:
        if token:
            kwargs = {'NextPageToken': token}
        else:
            kwargs = {}

        data = cd.get_cost_and_usage(
                TimePeriod={'Start': start, 'End':  end}, \
                Granularity='DAILY', \
                Metrics=['UnblendedCost'], \
                GroupBy=[ \
                        {'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'},
                        {'Type': 'DIMENSION', 'Key': 'SERVICE'}],
                **kwargs)
        results += data['ResultsByTime']
        token = data.get('NextPageToken')
        if not token:
            break
    return results



def subtotals(results, skipRefunds):
    total=0
    byacc={}
    byacc_and_service={}
    byservice={}
    byservice_and_account={}
    for result_by_time in results:
        for group in result_by_time['Groups']:
            unit = group['Metrics']['UnblendedCost']['Unit'].replace('USD','$')
            amount = float(group['Metrics']['UnblendedCost']['Amount'])
            account = group['Keys'][0]
            service = group['Keys'][1]

            if skipRefunds == True:
                if amount < 0.00:
                    print("->",amount,skipRefunds)
                    continue

            # initialize then 2nd dimensions
            if not account in byacc_and_service.keys():
                byacc_and_service[account]={}

            if not service in byservice_and_account.keys():
                byservice_and_account[service]={}

            if account == "":
                account = "None"

            total += amount

            # By linked account
            try:
                byacc[account] += amount
            except KeyError:
                byacc[account] = amount
            
            if not service in byacc_and_service[account].keys():
                byacc_and_service[account][service] = amount
            else:
                byacc_and_service[account][service] += amount

            #by service
            try:
                byservice[service] += amount
            except KeyError:
                byservice[service] = amount
            
            if not account in byservice_and_account[service].keys():
                byservice_and_account[service][account] = amount
            else:
                byservice_and_account[service][account] += amount


    return(byacc, byacc_and_service, byservice, byservice_and_account, total)




def report_byservice(byservice,byservice_and_account, total):
    """
    print a report by AWS service per Account  trying for CSV
    """
    print("AWS Monthly Cost report by Service per account from %s to %s" % (start,end));
    # assume everything is in dollars
    accounts=[]
    # Find all account in the report
    for service in byservice:
        for account in byservice_and_account[service]:
            if not account in accounts:
                accounts += [account]

    #print a header
    print("%40s ;" % ("'Service/Account'"), sep=";", end="")
    for account in accounts:
        print("'%13s' ;" % (account) ,end="")
    print("SubTotal")

    # print the cost matrix
    for service,total in sorted(byservice.items(), key=byprice, reverse=True):
        print("%40s " % (service), sep=";", end="")
        for account in accounts:
            try:
                print("; %15.2f" % (byservice_and_account[service][account]) ,end="")
            except KeyError:
                print("; %15.2f" % (0.00) ,end="")
        print("; %8.2f" % total )



if __name__ == "__main__":
    skipRefunds = False
    if len(sys.argv) == 2:
        if sys.argv[1] == "-s":
            skipRefunds = True
    (start,end) = period()
    results = accounting(start, end)
    (byacc, byacc_and_service, byservice, byservice_and_account, total) = subtotals(results, skipRefunds)
    print("\n\n\n")
    report_byservice(byservice,byservice_and_account, total)

