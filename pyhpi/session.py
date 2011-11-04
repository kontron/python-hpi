import logging

from sahpi import *
from resource import Resource
from domain import UNSPECIFIED_DOMAIN
from resource import RptEntry

logger = logging.getLogger(__name__)

class Session(object):
    def __init__(self):
        self._as_parameter_ = SaHpiSessionIdT(0)

    def open(self, domain=UNSPECIFIED_DOMAIN, security=None):
        logger.info('Open session for domain %d' % (domain.id,))
        saHpiSessionOpen(domain, byref(self._as_parameter_), None)

    def close(self):
        logger.info('Close session')
        saHpiSessionClose(self)

    def discover(self):
        saHpiDiscover(self)

    def domain_info(self):
        info = SaHpiDomainInfoT()
        saHpiDomainInfoGet(self, byref(info))
        return info

    def get_rpt_entry_by_resource(self, res):
        entry = SaHpiRptEntryT()
        saHpiEntryGetByResourceId(self, res, byref(entry))
        return RptEntry().from_ctype(entry)

    def resources(self):
        id = SaHpiEntryIdT(SAHPI_FIRST_ENTRY)
        nextid = SaHpiEntryIdT()
        while id.value != SAHPI_LAST_ENTRY:
            entry = SaHpiRptEntryT()
            saHpiRptEntryGet(self, id, byref(nextid), byref(entry))
            yield Resource(self).from_rpt(RptEntry().from_ctype(entry))
            id.value = nextid.value

    def get_resources(self):
        return list(self.resources())

    def get_resources_by_entity_path(self, path, instrument=None):
        resources = list()
        instrument_type = SaHpiRdrTypeT(SAHPI_NO_RECORD)
        instance_id = SaHpiUint32T(SAHPI_FIRST_ENTRY)
        resource_id = SaHpiResourceIdT()
        upd_cnt = SaHpiUint32T()
        last_upd_cnt = None

        while instance_id.value != SAHPI_LAST_ENTRY:
            try:
                t = path.to_ctype()
                saHpiGetIdByEntityPath(self, path.to_ctype(),
                        instrument_type, byref(instance_id), byref(resource_id),
                        None, byref(upd_cnt))
            except SaHpiError, e:
                if e.errno == SA_ERR_HPI_NOT_PRESENT and \
                        instance_id.value != SAHPI_FIRST_ENTRY:
                    # may be due to rpt update, start over
                    del resources[:]
                    instance_id.value = SAHPI_FIRST_ENTRY
                else:
                    raise

            # check if rpt was updated between two calls
            if last_upd_cnt is not None and last_upd_cnt != upd_cnt:
                # start over
                del resources[:]
                instance_id.value = SAHPI_FIRST_ENTRY

            resources.append(Resource(self).from_id(resource_id.value))
            last_upd_cnt = upd_cnt

        return resources
