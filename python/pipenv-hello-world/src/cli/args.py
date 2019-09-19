import argparse
import sys


def read():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help='a string', required=False)
    args = parser.parse_args()
    return args
