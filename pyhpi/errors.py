class SaHpiError(Exception):
    def __init__(self, errno, error):
        self.errno = errno
        self.error = error

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self.error)

    def __repr__(self):
        return '%s(%d,"%s")' % (self.__class__.__name__, self.errno, self.error)
