import sys
import hello.hello
import cli.args
import storage.client

if __name__ == "__main__":
    print("Hello world!")
    args = cli.args.read()
    print(args.host)
    hello.hello.echo()
    client = storage.client.Client(args.host, args.access_key, args.secret_key)
    print(client.get_client())
    print(client.list_objects("aaa"))
