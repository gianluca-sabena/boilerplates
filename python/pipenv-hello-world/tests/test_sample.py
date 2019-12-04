import helloworld.ns_mod_1


from helloworld.package import module_1

def test_echo_string():
    helloworld.ns_mod_1.echo()
    assert helloworld.ns_mod_1.echo() == "echo ns_mod_1.py"

def test_module_1():
    assert module_1.echo() == "package/module_1.py"
