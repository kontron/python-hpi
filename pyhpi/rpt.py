from sahpi import *
from utils import BaseHpiObject, TextBuffer
from entity import EntityPath

class RptEntry(BaseHpiObject):
    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)
        self.entry_id = s.EntryId
        self.resource_id = s.ResourceId
        #self.resource_info = ResourceInfo(s.ResourceInfo)
        self.resource_info = None # XXX
        self.entity_path = EntityPath().from_ctype(s.ResourceEntity)
        self.resource_capabilities = s.ResourceCapabilities
        self.hotswap_capabilities = s.HotSwapCapabilities
        self.resource_severity = s.ResourceSeverity.value
        self.resource_failed = s.ResourceFailed
        self.resource_tag = TextBuffer().from_ctype(s.ResourceTag)

        return self
