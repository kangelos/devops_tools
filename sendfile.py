#!/usr/bin/env python3
"""
An abuse of the kuyruk lib (a job queue system that uses rabbitmq to serialize tasks)
to send a small file over rabbitmq to a target device. This program uses a conditional 
decorator to define arbitrary queues for the sender and worker 

dependencies: pip3 install kuyruk 

The same program is used to send command to an arbitrary remote system and 
also perform the task on the remote system itself!


run the sender - you need the KUYRUK ENV var - with:
KUYRUK=SEND ./sendfile.py <filename>

-------------

run the worker on the remote device with:
/usr/local/bin/kuyruk --app sendfile.kuyruk worker --queue $(hostname)
"""
import socket
import sys
import os
import logging
from kuyruk import Kuyruk
# read the docs for the format of the config.py file
# https://kuyruk.readthedocs.io/en/latest/api.html
import config

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger("filesender")


def taskify(function):
    """
    call the kuyryk decorator only when imported
    The true parameter hese is "function"
    fn is whatever gets passed to the function
    only possible with dynamic languages
    kuyruk uses the python module name to serialize the commands/defs to send to the queue
    so any include will use a different module name and the kuyruk worker runner
    works via includes ....
    One way to deal with this cruft is an environment variable ...
    """
    def decorate(fn):
        """
        Return the kuryuk decorator or the function itself ?
        """
        mytype = os.getenv('KUYRUK')
        if mytype is None:
            logger.debug("ENV variable KUYRUK is not set, assuming a worker setup")
            return function(fn)
        elif mytype.upper() == 'SEND':
            logger.debug("ENV variable KUYRUK='%s', assuming you will be sending commands", mytype)
            return fn
        else:
            logger.debug("ENV variable KUYRUK='%s', assuming a worker setup", mytype)
            return function(fn)

    return decorate
    

kuyruk = Kuyruk(config)
# taskify is our own conditional decorator
@taskify(kuyruk.task(socket.gethostname()))
def sendfile(filename, contents):
    """
    copy a file
    """
    f = open(filename, "w")
    result = f.write(contents)
    f.close()
    logger.info("> SENDILE: '%s' received", filename)
    return result


#  If run from the command line then SEND the task
if __name__ == "__main__":
       
    filename = sys.argv[1]
    fi = open(filename, "r")
    contents = fi.read()
    fi.close()

    wait = 5
    host = "arbitrary hostname"
    mytask = kuyruk.task(queue=host)(sendfile)
    result = mytask.send_to_queue(args=[filename, contents], wait_result=wait)
    logger.info("Task:%s returned:%s", task, result)
    print(result)
