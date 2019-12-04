import sys
# absolute import in the main file as explained here <https://docs.python.org/3.7/tutorial/modules.html#importing-from-a-package>
import helloworld.package.module_1
import helloworld.ns_mod_1

def run_cli():
    print("cli entry point")
    print(helloworld.ns_mod_1.echo())
    helloworld.package.module_1.echo()

if __name__ == "__main__":
    run_cli()