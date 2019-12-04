from . import module_2

def echo():
    print("Hello from subpackage_1 - module_1")
    module_2.echo("Relative import from subpackage_1 - module_1")