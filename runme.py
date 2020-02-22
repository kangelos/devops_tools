def runme(args, chwd="/tmp", debug=False):
    """
    A generic subprocess runner with a capture of all output and stderr
    in their proper order. If debug flag is set , it also logs the output
    Retuns all output stdout+stderr in proper order
    """
    cmdOutput = []
    cmdOutputLock = Lock()
    STDOUT = 1
    STDERR = 2

    def _outputLoop(fd, identifier):
        """
        lock the output array and grab as many lines as you can 
        from the relevant file descriptor
        """
        line = fd.readline()
        while line:
            cmdOutputLock.acquire()
            cmdOutput.append((line, identifier))
            cmdOutputLock.release()
            line = fd.readline()
    # back to runme
    try:
        p = subprocess.Popen(args, cwd=chwd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True)
    except subprocess.CalledProcessError as err:
        logger.err("subprocess.Popen error:%d", err.returncode)

    Thread(target=_outputLoop, args=(p.stdout, STDOUT)).start()
    Thread(target=_outputLoop, args=(p.stderr, STDERR)).start()

    lines = ""
    while p.poll() is None or cmdOutput:
        output = None
        cmdOutputLock.acquire()
        if cmdOutput:
            output = cmdOutput[0]
            lines += output[0]
            del cmdOutput[0]
            if debug:
                if output[1] == STDOUT:
                    logger.info("STDOUT:%s", output[0].rstrip())
                elif output[1] == STDERR:
                    logger.info("STDERR:%s", output[0].rstrip())
        cmdOutputLock.release()

    return lines
