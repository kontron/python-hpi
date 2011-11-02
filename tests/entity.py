import unittest

from pyohpi import Entity, EntityPath
from pyparsing import ParseException

class EntityTest(unittest.TestCase):
    def test_from_string(self):
        e = Entity()
        e.from_string('{POWER_SUPPLY,1}')
        self.assertEqual((e.type, e.location), (10,1))
        e.from_string('{ POWER_SUPPLY,1}')
        self.assertEqual((e.type, e.location), (10,1))
        e.from_string('{POWER_SUPPLY, 1}')
        self.assertEqual((e.type, e.location), (10,1))
        e.from_string('{POWER_SUPPLY , 1}')
        self.assertEqual((e.type, e.location), (10,1))
        e.from_string('{ POWER_SUPPLY , 1}')
        self.assertEqual((e.type, e.location), (10,1))
        e.from_string('{ POWER_SUPPLY , 1 }')
        self.assertEqual((e.type, e.location), (10,1))
        e.from_string('{ POWER_SUPPLY , 1 }')
        self.assertEqual((e.type, e.location), (10,1))
        e.from_string('{ POWER_SUPPLY , 1 }')
        self.assertEqual((e.type, e.location), (10,1))

    def test_from_string_numeric(self):
        e = Entity()
        e.from_string('{1,1}')
        self.assertEqual((e.type, e.location), (1,1))
        e.from_string('{2,1}')
        self.assertEqual((e.type, e.location), (2,1))

    def test_from_string_error(self):
        e = Entity()
        self.assertRaises(ValueError, e.from_string, '{AAAA,1}')
        self.assertRaises(ParseException, e.from_string, '{AAAA')
        self.assertRaises(ParseException, e.from_string, 'AAAA,1}')
        self.assertRaises(ParseException, e.from_string, '{AAAA}')


class EntityPathTest(unittest.TestCase):
    def test_from_string(self):
        ep = EntityPath()
        ep.from_string('{{ADD_IN_CARD,3},{POWER_SUPPLY,1}}')
        self.assertEqual(len(ep), 2)
        self.assertEqual((ep[0].type, ep[0].location), (11,3))
        self.assertEqual((ep[1].type, ep[1].location), (10,1))


if __name__ == '__main__':
    unittest.main()
