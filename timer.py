__author__ = 'sergeygolubev'

import time

def timer(f):
    def tmp(*args, **kwargs):
        t = time.time()
        res = f(*args, **kwargs)
        print "Run time: %f" % (time.time()-t)
        return res

    return tmp

