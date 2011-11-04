from pyhpi import Session

def main():
    s = Session()
    s.open()
    for rpt in s.get_rpt_entries():
        print """
Entity Path:             %(entity_path)s
  Entry Id:              %(entry_id)d
  Hotswap Capabilities:  %(hotswap_capabilities)Xh
  Resource Capabilities: %(resource_capabilities)Xh
  Resource Failed:       %(resource_failed)d
  Resource Id:           %(resource_id)d
  Resource Info:         %(resource_info)s
  Resource Severity:     %(resource_severity)d
  Resource Tag:          %(resource_tag)s
"""[1:-1] % rpt.__dict__
    s.close()

if __name__ == '__main__':
    main()
