from functools import partial

from sahpi import *
from parser import tok_entity, tok_entity_path
from array import array

class BaseHpiObject(object):
    __ignored_methods__ = ['from_ctype', 'from_string', 'to_ctype']
    def __init__(self):
        pass

    def from_ctype(self, s):
        self._obj = s

    def __repr__(self):
        args = list()
        for k in dir(self):
            if k.startswith('_') or k in self.__ignored_methods__:
                continue
            attr = getattr(self, k)
            if isinstance(attr, basestring) \
                    or getattr(self, '_is_string_', False):
                args.append('%s="%s"' % (k, attr))
            else:
                args.append('%s=%s' % (k, attr))

        return '%s(%s)' % (self.__class__.__name__, ', '.join(args))

class TextBuffer(BaseHpiObject):
    def __init__(self, data=None):
        if data is not None:
            self.type = SAHPI_TL_TYPE_TEXT
            self.language = SAHPI_LANG_UNDEF
            self.data = data

    def from_string(self, s):
        self.type = SAHPI_TL_TYPE_TEXT
        self.language = SAHPI_LANG_UNDEF
        self.data = str(s)

        return self

    def from_ctype(self, s):
        """Fills this TextBuffer from a SaHpiTextBufferT C-structure."""
        BaseHpiObject.from_ctype(self, s)

        if s.DataType.value not in (SAHPI_TL_TYPE_TEXT, SAHPI_TL_TYPE_UNICODE):
            raise NotImplemented('only text data is supported yet')

        self.type = s.DataType.value
        self.language = s.Language.value
        data = array('B', s.Data[:]).tostring().rstrip('\x00')
        if self.type == SAHPI_TL_TYPE_TEXT:
            self.data = data.decode('ascii')
        else:
            self.data = data.decode('utf_16_le')

        return self

    def to_ctype(self):
        if self.type != SAHPI_TL_TYPE_TEXT:
            raise NotImplemented('only text data is supported yet')

        t = SaHpiTextBufferT()
        t.DataType = SaHpiTextTypeT(self.type)
        t.Language = SaHpiLanguageT(self.language)
        t.DataLength = SaHpiUint8T(len(self.data))
        data = array('B', str(self.data)).tolist()
        t.Data = (SaHpiUint8T * SAHPI_MAX_TEXT_BUFFER_LENGTH)(*data)
        return t

    def __eq__(self, a):
        return self.data == a

    def __str__(self):
        return self.data

    def __len__(self):
        return len(self.data)

    def __getslice__(self, a, b):
        return self.data[a:b]

    def __delslice__(self, a, b):
        del self.data[a:b]

    def __getitem__(self, a):
        return self.data[a]

def enumeration_name(enum_cls, value):
    return enum_cls(value).name

dimi_test_status_str = partial(enumeration_name, SaHpiDimiTestRunStatusT)
fumi_upgrade_status_str = partial(enumeration_name, SaHpiFumiUpgradeStatusT)
severity_str = partial(enumeration_name, SaHpiSeverityT)
event_type_str = partial(enumeration_name, SaHpiEventTypeT)
resource_event_type_str = partial(enumeration_name, SaHpiResourceEventTypeT)
