from sahpi import *
from utils import BaseHpiObject
from parser import tok_entity, tok_entity_path

class Entity(BaseHpiObject):
    def from_ctype(self, s):
        """Fills this Entity from a SaHpiEntityT C-structure."""
        BaseHpiObject.from_ctype(self, s)
        self.type = s.EntityType.value
        self.location = s.EntityLocation

        return self

    def to_ctype(self):
        """Converts this Entity to a SaHpiEntityT C-structure."""
        e = SaHpiEntityT()
        e.EntityType.value = self.type
        e.EntityLocation = self.location
        return e

    @property
    def typestring(self):
        """Returns the name of the current type."""
        if not hasattr(self, '_typestring'):
            g = globals()
            for attr in g:
                if attr.startswith('SAHPI_ENT_') and g[attr] == self.type:
                    self._typestring = attr[10:]
        
        return self._typestring

    def from_string(self, s):
        """Parses an entity string.

        The string has to be in the following format: {TYPE,LOCATION}. The type
        can be either a string or a number, the location has to be a number. If
        the type is a string the SaHpiEntityTypeT enumeration is search for a
        match (without the prefix SAHPI_ENT_).

        Examples:
        {NPU, 1}, {FPGA,10} or {15,5}
        """

        e = tok_entity.parseString(s)
        try:
            self.type = int(e[0], 10)
        except ValueError:
            # search global attributes
            g = globals()
            for attr in g:
                if attr == 'SAHPI_ENT_' + e[0]:
                    self.type = g[attr]
                    break
            else:
                raise ValueError('entity type "%s" not found' % e[0])
        self.location = int(e[1])

        return self

    def __str__(self):
        return '{%s, %d}' % (self.typestring, self.location)


class EntityPath(BaseHpiObject):
    def __init__(self):
        BaseHpiObject.__init__(self)
        self._is_string_ = True

    def from_ctype(self, s):
        BaseHpiObject.from_ctype(self, s)

        self.entries = list()
        num_entries = 0
        for i in xrange(SAHPI_MAX_ENTITY_PATH):
            if s.Entry[i].EntityType.value == SAHPI_ENT_ROOT:
                num_entries = i+1
                break
        for i in xrange(num_entries):
            self.entries.append(Entity().from_ctype(s.Entry[i]))

        return self

    def to_ctype(self):
        ep = SaHpiEntityPathT()
        for (i, e) in enumerate(self.entries):
            ep.Entry[i] = e.to_ctype()
        return ep

    def __len__(self):
        return len(self.entries)

    def __getslice__(self, a, b):
        return self.entries[a:b]

    def __getitem__(self, a):
        return self.entries[a]

    def from_string(self, s):
        # XXX do it more elegant :)
        ep = tok_entity_path.parseString(s)
        self.entries = list()
        root = Entity().from_string('{ROOT,0}')
        self.entries.append(root)
        for e in ep:
            entity = Entity().from_string('{%s,%d}' % (e[0], e[1]))
            self.entries.append(entity)
        # more human readable if path is reversed
        self.entries.reverse()
        return self

    def __str__(self):
        return '{%s}' % (', '.join(map(str, reversed(self.entries))))
