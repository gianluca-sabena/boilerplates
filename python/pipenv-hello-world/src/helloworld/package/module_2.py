# Pylint issue https://github.com/PyCQA/pylint/issues/2967
# Relative imports
from .subpackage import module_1
from .subpackage import  module_2

def echo():
    return "message from file src/helloworld/package/module_2.py"

