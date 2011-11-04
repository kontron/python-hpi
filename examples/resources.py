from pyhpi import Session

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

        print "  RDRs:"
        for rdr in res.rdrs():
            print """
    Record Id:           %(record_id)d
    RDR Type:            %(rdr_type)s
    RDR Entity Path:     %(entity)s
    Is FRU:              %(is_fru)s
    Id String:           %(id_string)s
"""[1:-1] % rdr.__dict__

    s.close()

if __name__ == '__main__':
    main()
