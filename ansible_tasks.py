#!/usr/bin/env python3
"""
A batch task system for triggering full ansible runs for a single host
the queueing system is rabbitmq

dependencies:
  pip3 install kuyruk
  and a rabbitmq cluster ;-)

The worker executes the task it dequeues
run the worker it with:
    kuyruk --app ansible_tasks.kuyruk worker --queue ha-ansible

The sender enqueues/sends the task
send the task so that a full playbook can be run on limit
    python3 ansible_tasks.py rfidgw-..... collectd

you will need an /srv/ansible/run script like so
  !/bin/bash
  ansible-playbook -i INVENTORY PLAYBOOK.yml  $*

"""
import configparser
import subprocess
import shlex
import sys
import os
import logging
import time
from threading import Thread
from kuyruk import Kuyruk, Config

logging.basicConfig(level=logging.INFO)
Logger = logging.getLogger()
os.environ['PYTHONUNBUFFERED'] = '1'


def readconfig(inifile='/etc/kuyruk.ini', section='ansible_tasks'):
    """
    Read an inifile with all the settings for kuyruk
    """
    conf = Config()
    cfg_parser = configparser.ConfigParser()
    if not os.path.isfile(inifile):
        Logger.err("File not found {}".format(inifile))
        return None

    cfg_parser.read([section, inifile])
    conf.RABBIT_HOST = cfg_parser[section]['RABBIT_HOST']
    conf.RABBIT_PORT = int(cfg_parser[section]['RABBIT_PORT'])
    conf.RABBIT_USER = cfg_parser[section]['RABBIT_USER']
    conf.RABBIT_PASSWORD = cfg_parser[section]['RABBIT_PASSWORD']
    conf.RABBIT_VIRTUAL_HOST = cfg_parser[section]['RABBIT_VIRTUAL_HOST']
    conf.WORKER_MAX_RUN_TIME = int(cfg_parser[section]['WORKER_MAX_RUN_TIME'])
    conf.WORKER_LOGGING_LEVEL = cfg_parser[section]['WORKER_LOGGING_LEVEL']
    conf.RABBIT_SSL = cfg_parser[section].getboolean('RABBIT_SSL')

    return conf


# don't let these lines fool you, they do a lot of work
try:
    kuyruk = Kuyruk(readconfig("/etc/assimilate/kuyruk.ini", "ansible_tasks"))
except:
    Logger.err("cannot initialize kuyruk")
    exit(1)

#taskify 'playbook' and bind it to queue ha-ansible
@kuyruk.task("ha-ansible")
def playbook(hostname, tag=""):
    """
    The actual task to send over rabbitmq and execute when received.
    We are using a multithreaded IO reader because the output is quite long
    and we would rather wathc it go by rather than wait for the end
    of the task.
    """
    def _outputLoop(fd, dummy=0):
        """
        read lines from  a file descriptor, the second param is there
        so that python does not expand the first param from an fd to its contents
        """
        line = fd.readline()
        while line:
            Logger.info("%s", line.decode('utf-8').rstrip())
            line = fd.readline()

    command_line = "/srv/ansible/run -v "
    if hostname:
        command_line += " --limit " + hostname
    
    if tag:
        command_line += " --tags " + tag

    Logger.info("Trying to execute '%s'", command_line)
    args = shlex.split(command_line)
    try:
        p = subprocess.Popen(args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as err:
        Logger.err("Ansible run came back with error %d", err.returncode)
        return None

    Thread(target=_outputLoop, args=(p.stdout, 1)).start()
    Thread(target=_outputLoop, args=(p.stderr, 2)).start()

    # wait until the process is done
    while p.poll() is None:
        time.sleep(0.5)
    # playbook is done

#  If run from the command line then SEND the task
if __name__ == "__main__":
    host = ""
    tag = ""
    if len(sys.argv) <= 1:
        print("Usage: ansible_tasks <limit_hostname> [tag]")
        exit(1)

    if len(sys.argv) > 1:
        host = sys.argv[1]
        if len(sys.argv) > 2:
            tag = sys.argv[2]

        print("Queueing an ansible task on target:{} with tag='{}'".format(host, tag))
        playbook(host, tag)
