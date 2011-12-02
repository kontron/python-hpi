#!/usr/bin/env python

from setuptools import setup

def main():
    setup(name = 'pyhpi',
            version = '1.00',
            description = 'Pure python HPI library',
            author_email = 'michael.walle@kontron.com',
            packages = [ 'pyhpi',
            ],
    )

if __name__ == '__main__':
    main()
