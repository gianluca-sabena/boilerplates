import helloworld.main


def test_call():
    assert helloworld.main.msg() == ['message from file src/helloworld/package/subpackage/module_1.py', 'message from file src/helloworld/package/subpackage/module_2.py',
                                     'message from file src/helloworld/package/module_2.py', 'message from file src/helloworld/package/module_1.py']
