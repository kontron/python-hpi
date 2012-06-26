from pyhpi import Session, EventListener

def main():
    s = Session()
    s.open()
    listener = EventListener(s)
    listener.subscribe()
    while True:
        print listener.get()
    listener.unsubscribe()
    s.close()

if __name__ == '__main__':
    main()
