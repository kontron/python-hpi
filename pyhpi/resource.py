import logging
from array import array

from sahpi import *
from fumi import Fumi
from dimi import Dimi
from utils import BaseHpiObject, TextBuffer
from entity import EntityPath
from errors import RetriesExceededError

logger = logging.getLogger(__name__)

class Guid(BaseHpiObject):
    def from_ctype(self, s):
        self.guid = array('B', s).tostring()
        return self

    def __str__(self):
        return self.guid.encode('hex')

    def __int__(self):
        guid = 0
        for i in len(self.guid):
            guid |= self.guid[i] << (i*8)
        return guid


class ResourceInfo(BaseHpiObject):
    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)
        self.resource_revision = s.ResourceRev
        self.specific_version = s.SpecificVer
        self.device_support = s.DeviceSupport
        self.manufacturer_id = s.ManufacturerId
        self.product_id = s.ProductId
        self.firmware_major_revision = s.FirmwareMajorRev
        self.firmware_minor_revision = s.FirmwareMinorRev
        self.aux_firmware_revision = s.AuxFirmwareRev
        self.guid = Guid().from_ctype(s.Guid)

        return self


class ResourceCapabilities(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        all_capabilities = [
            'SAHPI_CAPABILITY_SENSOR',
            'SAHPI_CAPABILITY_RDR',
            'SAHPI_CAPABILITY_EVENT_LOG',
            'SAHPI_CAPABILITY_INVENTORY_DATA',
            'SAHPI_CAPABILITY_RESET',
            'SAHPI_CAPABILITY_POWER',
            'SAHPI_CAPABILITY_ANNUNCIATOR',
            'SAHPI_CAPABILITY_LOAD_ID',
            'SAHPI_CAPABILITY_FRU',
            'SAHPI_CAPABILITY_CONTROL',
            'SAHPI_CAPABILITY_WATCHDOG',
            'SAHPI_CAPABILITY_MANAGED_HOTSWAP',
            'SAHPI_CAPABILITY_CONFIGURATION',
            'SAHPI_CAPABILITY_AGGREGATE_STATUS',
            'SAHPI_CAPABILITY_DIMI',
            'SAHPI_CAPABILITY_EVT_DEASSERTS',
            'SAHPI_CAPABILITY_FUMI',
            'SAHPI_CAPABILITY_RESOURCE',
        ]

        capabilities = list()
        for c in all_capabilities:
            if globals()[c] & self.value:
                capabilities.append(c[len('SAHPI_CAPABILITY_'):])

        return ' '.join(capabilities)

    def __int__(self):
        return self.value


class RptEntry(BaseHpiObject):
    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)
        self.entry_id = s.EntryId
        self.resource_id = s.ResourceId
        self.resource_info = ResourceInfo().from_ctype(s.ResourceInfo)
        self.entity_path = EntityPath().from_ctype(s.ResourceEntity)
        self.resource_capabilities = \
                ResourceCapabilities(s.ResourceCapabilities)
        self.hotswap_capabilities = s.HotSwapCapabilities
        self.resource_severity = s.ResourceSeverity.value
        self.resource_failed = s.ResourceFailed
        self.resource_tag = TextBuffer().from_ctype(s.ResourceTag)

        return self


class CommonRdr(BaseHpiObject):
    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)
        self.record_id = s.RecordId
        self.rdr_type = s.RdrType.value
        self.entity = EntityPath().from_ctype(s.Entity)
        self.is_fru = bool(s.IsFru)
        self.id_string = TextBuffer().from_ctype(s.IdString)


class DimiRdr(CommonRdr):
    __type__ = SAHPI_DIMI_RDR
    def from_ctype(self, s):
        CommonRdr.from_ctype(self, s)
        if self.rdr_type != self.__type__:
            raise DecodingError("RDR is no DIMI RDR")

        rec = s.RdrTypeUnion.DimiRec
        self.dimi_num = rec.DimiNum
        self.oem = rec.Oem

        return self


class FumiRdr(CommonRdr):
    __type__ = SAHPI_FUMI_RDR
    def from_ctype(self, s):
        CommonRdr.from_ctype(self, s)
        if self.rdr_type != SAHPI_FUMI_RDR:
            raise DecodingError("RDR is no FUMI RDR")

        rec = s.RdrTypeUnion.FumiRec
        self.fumi_num = rec.Num
        self.access_protocol = rec.AccessProt
        self.capability = rec.Capability
        self.num_banks = rec.NumBanks
        self.oem = rec.Oem

        return self


class Rdr:
    __types__ = [DimiRdr, FumiRdr]

    def from_ctype(self, s):
        """Creates an RDR class according the type field."""
        cls = None
        for cls in self.__types__:
            if cls.__type__ == s.RdrType.value:
                obj = cls()
                obj.from_ctype(s)
                return obj
        raise DecodingError("No RDR for type %d found" % s.RdrType.value)


class Resource(object):
    def __init__(self, session):
        self.session = session
        self._rpt = None
        self._rdrs = None
        self._last_rdr_update_count = 0

    def __repr__(self):
        return 'Resource(id=%d)' % (self._as_parameter_.value,)

    def fumi_handler_by_num(self, fumi_num):
        return Fumi(self.session, self, fumi_num)

    def fumi_handler_by_rdr(self, rdr):
        return Fumi(self.session, self, rdr.fumi_num)

    def dimi_handler_by_num(self, dimi_num):
        return Dimi(self.session, self, dimi_num)

    def dimi_handler_by_rdr(self, rdr):
        return Dimi(self.session, self, rdr.dimi_num)

    def from_id(self, id):
        self._as_parameter_ = SaHpiResourceIdT(id)
        return self

    def from_rpt(self, rpt):
        self._as_parameter_ = SaHpiResourceIdT(rpt.resource_id)
        self._rpt = rpt
        return self

    def rdr_update_count(self):
        count = SaHpiUint32T()
        saHpiRdrUpdateCountGet(self.session, self, byref(count))
        return count.value

    def rdrs(self):
        if (self._rdrs is None
                or self._last_rdr_update_count < self.rdr_update_count()):
            self._update_rdr_repository()

        return self._rdrs

    def _update_rdr_repository(self, max_retries=3):
        logger.debug('updating rdr repository (retries=%d)', max_retries)
        update_count = self.rdr_update_count()
        retries = 0
        if self._rdrs is None:
            self._rdrs = list()
        while retries < max_retries:
            logger.debug('retry #%d', retries)
            del self._rdrs[:]
            id = SaHpiEntryIdT(SAHPI_FIRST_ENTRY)
            nextid = SaHpiEntryIdT()
            while id.value != SAHPI_LAST_ENTRY:
                _rdr = SaHpiRdrT()
                saHpiRdrGet(self.session, self, id, byref(nextid), byref(_rdr))
                rdr = Rdr().from_ctype(_rdr)
                logger.debug('Fetched RDR %s', rdr)
                self._rdrs.append(rdr)
                id.value = nextid.value
            # see if rdr update count is still the same
            if update_count == self.rdr_update_count():
                break
            # otherwise try again
            retries += 1
        else:
            raise RetriesExceededError()

    @property
    def rpt(self):
        if self._rpt is None:
            self._rpt = self.session.get_rpt_entry_by_resource(self)
        return self._rpt

UNSPECIFIED_RESOURCE = Resource(None).from_id(SAHPI_UNSPECIFIED_RESOURCE_ID)
