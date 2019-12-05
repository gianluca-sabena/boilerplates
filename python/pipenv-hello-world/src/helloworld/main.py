# absolute import in the main file as explained here <https://docs.python.org/3.7/tutorial/modules.html#importing-from-a-package>
# this file is the "main" entry point used in setup.py to provide a console script
import helloworld.package.module_1
import helloworld.ns_mod_1

def msg():
    return helloworld.package.module_1.echo()

def run_cli():
    print("cli entry point")
    print("append message from other module function:",msg())

if __name__ == "__main__":
    run_cli()