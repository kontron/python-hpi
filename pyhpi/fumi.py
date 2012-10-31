import time
import logging

from sahpi import *
from utils import TextBuffer, BaseHpiObject

logger = logging.getLogger(__name__)


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


class TargetInfo(BaseHpiObject):
    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)

        self.id = s.BankId
        self.size = s.BankSize
        self.position = s.Position
        self.state = s.BankState.value
        self.identifier = TextBuffer().from_ctype(s.Identifier)
        self.description = TextBuffer().from_ctype(s.Description)
        self.date_time = TextBuffer().from_ctype(s.DateTime)
        self.major_version = s.MajorVersion
        self.minor_version = s.MinorVersion
        self.aux_version = s.AuxVersion

        return self


class FirmwareInstance(BaseHpiObject):
    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)

        self.is_present = bool(s.InstancePresent)
        self.identifier = TextBuffer().from_ctype(s.Identifier)
        self.description = TextBuffer().from_ctype(s.Description)
        self.date_time = TextBuffer().from_ctype(s.DateTime)
        self.major_version = s.MajorVersion
        self.minor_version = s.MinorVersion
        self.aux_version = s.AuxVersion

        return self


class LogicalTargetInfo(BaseHpiObject):
    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)

        self.fw_persistent_location_count = s.FirmwarePersistentLocationCount
        self.state = s.BankStateFlags
        self.pending_instance = \
                FirmwareInstance().from_ctype(s.PendingFwInstance)
        self.rollback_instance = \
                FirmwareInstance().from_ctype(s.RollbackFwInstance)

        # remove instances which are not present
        if not self.pending_instance.is_present:
            self.pending_instance = None
        if not self.rollback_instance.is_present:
            self.rollback_instance = None

        return self


class FumiBank(object):
    def __init__(self, session, resource, fumi, bank_num):
        self.session = session
        self.resource = resource
        self.fumi = fumi
        self._as_parameter_ = SaHpiBankNumT(bank_num)

    def set_source(self, uri):
        uri = TextBuffer().from_string(uri)
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

    def cancel(self):
        saHpiFumiUpgradeCancel(self.session, self.resource, self.fumi,
                self)

    def source_info(self):
        info = SaHpiFumiSourceInfoT()
        saHpiFumiSourceInfoGet(self.session, self.resource, self.fumi,
                self, byref(info))

        return  SourceInfo().from_ctype(info)

    def bank_info(self):
        _info = SaHpiFumiBankInfoT()
        saHpiFumiTargetInfoGet(self.session, self.resource, self.fumi,
                self, byref(_info))

        info = TargetInfo().from_ctype(_info)
        logger.debug('Fetched target info for (%d/%d): %s',
            self.fumi._as_parameter_.value, self._as_parameter_.value, info)

        return info

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

    def logical_bank_info(self):
        _info = SaHpiFumiLogicalBankInfoT()
        saHpiFumiLogicalTargetInfoGet(self.session, self.resource, self,
                byref(_info))

        info = LogicalTargetInfo().from_ctype(_info)
        logger.debug('Fetched logical target info for (%d): %s',
            self._as_parameter_.value, info)

        return info

    def start_activation(self, logical=True):
        saHpiFumiActivateStart(self.session, self.resource, self, logical)

    def start_rollback(self):
        saHpiFumiRollbackStart(self.session, self.resource, self)
