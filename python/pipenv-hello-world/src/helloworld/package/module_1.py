# Pylint issue https://github.com/PyCQA/pylint/issues/2967
# Relative imports
from .subpackage import module_1 as sub_module_1
from .subpackage import  module_2 as sub_module_2
from . import module_2 as same_module_2

def echo():
    str1 = sub_module_1.echo()
    str2 = sub_module_2.echo()
    str3 = same_module_2.echo()
    msg = "message from file src/helloworld/package/module_1.py"
    return [str1, str2, str3, msg]