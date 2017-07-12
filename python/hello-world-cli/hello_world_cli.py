#!/usr/bin/env python3
"""
A simple script approved by pylint
"""
from __future__ import print_function
import argparse
import sys


class App:
    """a class"""

    config = {
        "key": {
            "key-nested": "value"
        }
    }

    def __init__(self):
        self.data = []
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers()

        hello_parser = subparsers.add_parser('hello')
        hello_parser.add_argument('name')  # add the name argument
        # set the default function to hello
        hello_parser.set_defaults(func=self.hello)

        goodbye_parser = subparsers.add_parser('goodbye')
        goodbye_parser.add_argument('name')
        goodbye_parser.set_defaults(func=self.goodbye)
        print("Hello, world! {0}".format(self.config["key"]))
        args = parser.parse_args()
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)
        args.func(args)  # call the default function

    def hello(self, msg):
        """docs string"""
        print('Hello, {0}!'.format(msg.name))

    def goodbye(self, msg):
        """docs string"""
        print('Goodbye, {0}!'.format(msg.name))


def main():
    """Main"""
    App()

if __name__ == '__main__':
    main()
