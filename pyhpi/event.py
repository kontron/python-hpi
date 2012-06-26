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

    def get(self, timeout=SAHPI_TIMEOUT_BLOCK):
        timeout = SaHpiTimeoutT(timeout)
        event = SaHpiEventT()
        rdr = SaHpiRdrT()
        rpt_entry = SaHpiRptEntryT()
        queue_status = SaHpiEvtQueueStatusT()
        saHpiEventGet(self.session, timeout, byref(event), None, None, None)
        #saHpiEventGet(self.session, timeout, byref(event), byref(rdr),
        #        byref(rpt_entry), byref(queue_status))

        event_cls = Event.class_factory(event)
        return event_cls().from_ctype(event)
