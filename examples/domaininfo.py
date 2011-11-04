from pyhpi import Session

def main():
    s = Session()
    s.open()
    print s.domain_info()
    s.close()

if __name__ == '__main__':
    main()
