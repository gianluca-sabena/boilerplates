# Relative imports
from .subpackage_1 import module_1
from .subpackage_1 import  module_2


def echo():
    print("cli entry point")
    module_1.echo()
    module_2.echo()
    return "package/module_1.py"
