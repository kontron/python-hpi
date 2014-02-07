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

import sys
import time

from pyhpi import Session, EntityPath
from pyhpi.utils import fumi_upgrade_status_str
from pyhpi.errors import SaHpiError

from pyhpi.sahpi import *

def poll_until_equal(func, value, poll_interval=1, timeout=10):
    start_time = time.time()
    while func() != value and start_time + timeout > time.time():
        time.sleep(poll_interval)

def poll_unless_equal(func, value, poll_interval=1, timeout=10):
    start_time = time.time()
    actual_value = func()
    while actual_value == value and start_time + timeout > time.time():
        time.sleep(poll_interval)
        actual_value = func()
    return actual_value

def print_fumi_status(status):
    print '  FUMI update status is %s (%d).' % (fumi_upgrade_status_str(status), status)

def main():
    try:
        s = Session()
        s.open()
        s.discover()

        # set source
        ep = EntityPath()
        ep.from_string(sys.argv[1])

        print 'Entity path is "%s"' % ep
        r = s.get_resources_by_entity_path(ep)[0]
        f = r.fumi_handler_by_num(fumi_num=int(sys.argv[2]))
        b = f.logical_bank()

        print 'Setting Source to "%s"' % (sys.argv[3],)
        b.set_source(sys.argv[3])

        # validation
        print '[1] Validate'
        b.start_validation()
        status = b.status()
        print '  Polling status'
        status = poll_unless_equal(b.status, SAHPI_FUMI_SOURCE_VALIDATION_INITIATED)
        print_fumi_status(status)
        if status != SAHPI_FUMI_SOURCE_VALIDATION_DONE:
            print 'FAILED'
            sys.exit(1)

        print '  Source image informations:'
        info = b.source_info()
        print """
        URI: %(source_uri)s
        Status: %(source_status)s
        Identifier: %(identifier)s
        Description: %(description)s
        Date: %(date_time)s
        Version: %(major_version)s.%(minor_version)s.%(aux_version)08x
    """[1:-1] % info.__dict__

        # installation
        print '[2] Install'
        b.start_installation()
        print '  Polling status'
        status = poll_unless_equal(b.status, SAHPI_FUMI_INSTALL_INITIATED)
        print_fumi_status(status)
        if status != SAHPI_FUMI_INSTALL_DONE:
            print 'FAILED'
            sys.exit(1)

        # activation
        print '[3] Activate'
        f.start_activation()
        print '  Polling status'
        status = poll_unless_equal(b.status, SAHPI_FUMI_ACTIVATE_INITIATED)
        print_fumi_status(status)
        if status != SAHPI_FUMI_ACTIVATE_DONE:
            print 'FAILED'
            sys.exit(1)

        # cleanup
        print '[4] Cleanup'
        b.cleanup()

        s.close()
    except SaHpiError, e:
        print 'ERROR: %s' % e.error

if __name__ == '__main__':
    main()
