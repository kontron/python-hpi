# Copyright (c) 2014  Kontron Europe GmbH
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import logging

from sahpi import *
from resource import Resource
from domain import UNSPECIFIED_DOMAIN
from resource import RptEntry
from errors import SaHpiError
from event import EventListener

logger = logging.getLogger(__name__)

class Session(object):
    def __init__(self):
        self._as_parameter_ = SaHpiSessionIdT(0)
        self.event_listener = None

    def open(self, domain=UNSPECIFIED_DOMAIN, security=None):
        logger.info('Open session for domain %d' % (domain.id,))
        saHpiSessionOpen(domain, byref(self._as_parameter_), None)

    def close(self):
        logger.info('Close session')
        if self.event_listener is not None:
            self.event_listener.unsubscribe()
        saHpiSessionClose(self)

    def discover(self):
        saHpiDiscover(self)

    def domain_info(self):
        info = SaHpiDomainInfoT()
        saHpiDomainInfoGet(self, byref(info))
        return info

    def get_rpt_entry_by_resource(self, res):
        entry = SaHpiRptEntryT()
        saHpiRptEntryGetByResourceId(self, res, byref(entry))
        return RptEntry().from_ctype(entry)

    def resources(self):
        id = SaHpiEntryIdT(SAHPI_FIRST_ENTRY)
        nextid = SaHpiEntryIdT()
        while id.value != SAHPI_LAST_ENTRY:
            entry = SaHpiRptEntryT()
            try:
                saHpiRptEntryGet(self, id, byref(nextid), byref(entry))
                yield Resource(self).from_rpt(RptEntry().from_ctype(entry))
                id.value = nextid.value
            except SaHpiError, e:
                if (e.errno == SA_ERR_HPI_NOT_PRESENT
                        and id.value == SAHPI_FIRST_ENTRY):
                    # empty RPT
                    break
                else:
                    raise

    def attach_event_listener(self):
        self.event_listener = EventListener(self)
        self.event_listener.subscribe()

    def resources_list(self):
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
