import hello.hello


def test_echo_string():
    assert hello.hello.echo_string() == "hello world!"


def func(x):
    return x + 1


def test_answer():
    assert func(3) == 4
