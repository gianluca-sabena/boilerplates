import argparse
import sys


def read():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='foo help', required=True)
    parser.add_argument('--access-key', help='foo help', required=True)
    parser.add_argument('--secret-key', help='foo help', required=True)
    args = parser.parse_args()
    return args
