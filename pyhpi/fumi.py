import time

from sahpi import *
from utils import TextBuffer, BaseHpiObject

class SourceInfo(BaseHpiObject):
    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)
        self.source_uri = TextBuffer().from_ctype(s.SourceUri)
        self.source_status = SaHpiFumiSourceStatusT(s.SourceStatus.value)
        self.identifier = TextBuffer().from_ctype(s.Identifier)
        self.description = TextBuffer().from_ctype(s.Description)
        self.date_time = TextBuffer().from_ctype(s.DateTime)
        self.major_version = s.MajorVersion
        self.minor_version = s.MinorVersion
        self.aux_version = s.AuxVersion

        return self

class FumiBank(object):
    def __init__(self, session, resource, fumi, bank_num):
        self.session = session
        self.resource = resource
        self.fumi = fumi
        self._as_parameter_ = SaHpiBankNumT(bank_num)

    def set_source(self, uri):
        uri = TextBuffer(uri)
        saHpiFumiSourceSet(self.session, self.resource, self.fumi, self,
                byref(uri.to_ctype()))

    def start_validation(self):
        saHpiFumiSourceInfoValidateStart(self.session, self.resource,
                self.fumi, self)

    def status(self):
        status = SaHpiFumiUpgradeStatusT(0)
        saHpiFumiUpgradeStatusGet(self.session, self.resource, self.fumi,
                self, byref(status))

        return status.value

    def source_info(self):
        info = SaHpiFumiSourceInfoT()
        saHpiFumiSourceInfoGet(self.session, self.resource, self.fumi,
                self, byref(info))

        return  SourceInfo().from_ctype(info)

    def start_installation(self):
        saHpiFumiInstallStart(self.session, self.resource, self.fumi, self)

    def cleanup(self):
        saHpiFumiCleanup(self.session, self.resource, self.fumi, self)


class Fumi(object):
    def __init__(self, session, resource, fumi_num):
        self.session = session
        self.resource = resource
        self._as_parameter_ = SaHpiFumiNumT(fumi_num)

    def logical_bank(self):
        return FumiBank(self.session, self.resource, self, 0)

    def bank_number(self, num):
        return FumiBank(self.session, self.resource, self, num)

    def start_activation(self, logical=True):
        saHpiFumiActivateStart(self.session, self.resource, self, logical)
