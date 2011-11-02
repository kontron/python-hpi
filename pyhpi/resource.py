from sahpi import *
from fumi import Fumi

class Resource(object):
    def __init__(self, id=0, session=None):
        self._as_parameter_ = SaHpiResourceIdT(id)
        self.session = session

    def get_fumi_handler(self, fumi_num):
        return Fumi(self.session, self, fumi_num)

    def __repr__(self):
        return 'Resource(id=%d)' % (self._as_parameter_.value,)

UNSPECIFIED_RESOURCE = Resource(SAHPI_UNSPECIFIED_RESOURCE_ID)
