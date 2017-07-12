#!/usr/bin/env python3
"""
A simple script approved by pylint
"""
from __future__ import print_function
import argparse
import sys

def hello(msg):
    """docs string"""
    print('Hello, {0}!'.format(msg.name))


def goodbye(msg):
    """docs string"""
    print('Goodbye, {0}!'.format(msg.name))


def main():
    """Main"""
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    hello_parser = subparsers.add_parser('hello')
    hello_parser.add_argument('name')  # add the name argument
    hello_parser.set_defaults(func=hello)  # set the default function to hello

    goodbye_parser = subparsers.add_parser('goodbye')
    goodbye_parser.add_argument('name')
    goodbye_parser.set_defaults(func=goodbye)
    print("Hello, world!")
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args.func(args)  # call the default function

if __name__ == '__main__':
    main()
