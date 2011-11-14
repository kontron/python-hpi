from pyhpi import Session
from pyhpi.resource import DimiRdr

def print_lines_with_indent(lines, fmt_data, indent):
    for line in lines:
        print '%s%s' % (' '*indent, line % fmt_data)

def dump_rdr(rdr, indent=0):
    lines = [
            'Record Id:              %(record_id)d',
            'RDR Type:               %(rdr_type)s',
            'RDR Entity Path:        %(entity)s',
            'Is FRU:                 %(is_fru)s',
            'Id String:              %(id_string)s',
    ]
    print_lines_with_indent(lines, rdr.__dict__, indent)

def dump_dimi_test(dimi_test, indent=0):
    lines = [
            'Test Name:              %(name)s',
            'Service Impact:         %(service_impact)d',
            'Need Service OS:        %(service_os_needed)s',
            'Expected Run Duration:  %(expected_run_duration)s',
            'Capabilities:           %(capabilities)s',
    ]
    print_lines_with_indent(lines, dimi_test.__dict__, indent)

def dump_dimi_test_parameters(param, indent=0):
    lines = [
            'Name:                   %(name)s',
            'Info:                   %(info)s',
            'Type:                   %(type)d',
            'Default:                %(default)s',
            'Min:                    %(min)s',
            'Max:                    %(max)s'
    ]
    print_lines_with_indent(lines, param.__dict__, indent)

def main():
    s = Session()
    s.open()
    for res in s.resources():
        print """
Entity Path:             %(entity_path)s
  Entry Id:              %(entry_id)d
  Hotswap Capabilities:  %(hotswap_capabilities)Xh
  Resource Capabilities: %(resource_capabilities)Xh (%(resource_capabilities)s)
  Resource Failed:       %(resource_failed)d
  Resource Id:           %(resource_id)d
  Resource Info:
"""[1:-1] % res.rpt.__dict__

        print """
    Resource Revision:   %(resource_revision)s
    Specific Version:    %(specific_version)s
    Device Support:      %(device_support)s
    Manufacturer Id:     %(manufacturer_id)d
    Product Id:          %(product_id)d
    Firmware Version:    %(firmware_major_revision)d.%(firmware_minor_revision)d.%(aux_firmware_revision)d
    GUID:                %(guid)s
"""[1:-1] % res.rpt.resource_info.__dict__

        print """
  Resource Severity:     %(resource_severity)d
  Resource Tag:          %(resource_tag)s
"""[1:-1] % res.rpt.__dict__

        print '  RDRs:'
        for rdr in res.rdrs():
            dump_rdr(rdr, 4)
            if isinstance(rdr, DimiRdr):
                d = res.dimi_handler_by_rdr(rdr)
                for (no, test) in enumerate(d.test_list()):
                    print '      Test Number:            %d' % no
                    dump_dimi_test(test, 6)
                    print '      Parameters:'
                    for param in test.parameters:
                        dump_dimi_test_parameters(param, 8)
                        print ''
                    print ''
            print ''

    s.close()

if __name__ == '__main__':
    main()
