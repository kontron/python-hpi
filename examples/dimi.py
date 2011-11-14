import sys
import time

from pyhpi import Session, EntityPath
from pyhpi.utils import dimi_test_status_str

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

def print_dimi_status(status):
    print 'DIMI test status is %s (%d).' % (dimi_test_status_str(status), status)

def print_result(result):
    print '  Error Code:      %d' % result.error_code
    status = result.last_run_status
    print '  Last Run State:  %s (%d)' % (dimi_test_status_str(status), status)
    print '  Result:          %s' % result.result
    print '  Run Duration:    %s' % result.run_duration
    print '  Timestamp:       %s' % result.timestamp

def print_test_info(test):
    print 'Test Info:'
    print '  Test Name:              %s' % test.name
    print '  Service Impact:         %s' % test.service_impact
    print '  Need Service OS:        %s' % test.service_os_needed
    print '  Expected Run Duration:  %s' % test.expected_run_duration
    print '  Capabilities:           %s' % test.capabilities

def main():
    ep_str = sys.argv[1]
    dimi_num = int(sys.argv[2])
    try:
        test_num = int(sys.argv[3])
    except ValueError:
        test_num = None
        test_name = sys.argv[3]

    cancel_test = False
    if len(sys.argv) > 4:
        if sys.argv[4] == 'cancel':
            cancel_test = True
        else:
            params = None
            if len(sys.argv[4:]):
                params = [a.split('=', 1) for a in sys.argv[4:]]

    s = Session()
    s.open()

    s.discover()

    # set source
    ep = EntityPath()
    ep.from_string(ep_str)

    print 'Entity path is "%s"' % ep
    r = s.get_resources_by_entity_path(ep)[0]
    d = r.dimi_handler_by_num(dimi_num)

    if test_num is not None:
        t = d.test_list()[test_num]
    else:
        for test in d.test_list():
            if test.name == test_name:
                t = test
                break
        else:
            print 'No test with name "%s" found.' % test_name
            sys.exit(1)

    if cancel_test:
        t.cancel()
        print_dimi_status(t.status()[0])
        sys.exit(0)

    print_test_info(t)
    print 'Starting Test'
    t.start(params)
    print_dimi_status(t.status()[0])
    status = poll_unless_equal(lambda *f: t.status(*f)[0],
            SAHPI_DIMITEST_STATUS_RUNNING)
    print_dimi_status(status)
    print_result(t.results())

if __name__ == '__main__':
    main()
