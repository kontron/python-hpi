from sahpi import *

class Domain(object):
    def __init__(self, id=0):
        self.id = id
        self._as_parameter_ = SaHpiDomainIdT(id) 

UNSPECIFIED_DOMAIN = Domain(SAHPI_UNSPECIFIED_DOMAIN_ID)
