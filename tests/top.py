import unittest

from pyohpi import Session
from pyohpi import SaHpiError

class TestSession(unittest.TestCase):
    def test_open_close(self):
        s = Session()
        s.open()
        s.close()

    def test_close_wo_open(self):
        s = Session()
        self.assertRaises(SaHpiError, s.close)

if __name__ == '__main__':
    unittest.main()
