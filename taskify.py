def taskify(function):
    """
    call the kuyryk decorator only when imported
    The true parameter hese is "function"
    fn is whatever gets passed to the function
    only possible with dynamic languages
    kuyruk uses the python module name to serialize the defs to enqueue
    so any include will use a different module name for the kuyruk worker
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
