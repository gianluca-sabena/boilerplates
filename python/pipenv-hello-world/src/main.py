import sys
import hello.hello
import cli.args


if __name__ == "__main__":
    args = cli.args.read()
    print(f"argument name: {args.name}")
    hello.hello.echo()
