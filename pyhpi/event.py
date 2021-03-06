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

import datetime
import array

from sahpi import *
from utils import BaseHpiObject, TextBuffer, event_type_str
from errors import EncodingError

class Event(BaseHpiObject):
    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)
        self.source = s.Source
        self.event_type = s.EventType.value
        self.timestamp = \
            datetime.datetime.fromtimestamp(s.Timestamp/1000000000)
        self.severity = s.Severity.value

    @staticmethod
    def class_factory(s):
        event_type = s.EventType.value
        if event_type == SAHPI_ET_RESOURCE:
            return ResourceEvent
        elif event_type == SAHPI_ET_DOMAIN:
            return DomainEvent
        elif event_type == SAHPI_ET_USER:
            return UserEvent
        elif event_type == SAHPI_ET_DIMI:
            return DimiEvent
        elif event_type == SAHPI_ET_DIMI_UPDATE:
            return DimiUpdateEvent
        elif event_type == SAHPI_ET_FUMI:
            return FumiEvent
        else:
            raise AssertionError('unhandled event type %s (%d)' %
                    (event_type_str(event_type), event_type))

class ResourceEvent(Event):
    def from_ctype(self, s):
        Event.from_ctype(self, s)
        e = s.EventDataUnion.ResourceEvent
        self.action = e.ResourceEventType.value

        return self

class DomainEvent(Event):
    def from_ctype(self, s):
        Event.from_ctype(self, s)
        e = s.EventDataUnion.DomainEvent
        self.domain_type = e.Type
        self.domain_id = e.DomainId

        return self

class UserEvent(Event):
    def from_ctype(self, s):
        Event.from_ctype(self, s)
        e = s.EventDataUnion.UserEvent
        self.user_data = TextBuffer().from_ctype(e.UserEventData)

        return self

class DimiEvent(Event):
    def from_ctype(self, s):
        Event.from_ctype(self, s)
        e = s.EventDataUnion.DimiEvent
        self.dimi_num = e.DimiNum
        self.test_num = e.TestNum
        self.run_status = e.DimiTestRunStatus.value
        self.percent_completed = e.DimiTestPercentCompleted

        return self

class DimiUpdateEvent(Event):
    def from_ctype(self, s):
        Event.from_ctype(self, s)
        e = s.EventDataUnion.DimiUpdateEvent
        self.dimi_num = e.DimiNum

        return self

class FumiEvent(Event):
    def from_ctype(self, s):
        Event.from_ctype(self, s)
        e = s.EventDataUnion.FumiEvent
        self.fumi_num = e.FumiNum
        self.bank_num = e.BankNum
        self.status = e.UpgradeStatus.value

        return self

class EventListener(object):
    def __init__(self, session):
        self.session = session

    def subscribe(self):
        saHpiSubscribe(self.session)

    def unsubscribe(self):
        saHpiUnsubscribe(self.session)

    def get(self, timeout=0):
        if timeout == 0:
            timeout = SAHPI_TIMEOUT_IMMEDIATE
        elif timeout == -1:
            timeout = SAHPI_TIMEOUT_BLOCK
        else:
            timeout = int(timeout * 1000000000)

        timeout = SaHpiTimeoutT(timeout)
        event = SaHpiEventT()
        rdr = SaHpiRdrT()
        rpt_entry = SaHpiRptEntryT()
        queue_status = SaHpiEvtQueueStatusT()
        try:
            saHpiEventGet(self.session, timeout, byref(event), byref(rdr),
                    byref(rpt_entry), byref(queue_status))
        except SaHpiError, e:
            if (timeout.value == SAHPI_TIMEOUT_IMMEDIATE
                    and e.errno == SA_ERR_HPI_TIMEOUT):
                # no event in queue
                return None
            else:
                raise

        event_cls = Event.class_factory(event)
        return event_cls().from_ctype(event)
