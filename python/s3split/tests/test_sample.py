import s3split
import unittest

def func(x):
    return x + 1


def test_answer():
    assert func(3) == 4


class MyTestCase(unittest.TestCase):
    def test1(self):
        self.assertRaises(SomeCoolException, s3split.main(["--s3-secret-key", "A", "--s3-access-key", "B", "--s3-endpoint", "C", "--s3-bucket", "D", "--source-path", "E"]))

# def test_main():
#     s3split.main(["--s3-secret-key", "A", "--s3-access-key", "B", "--s3-endpoint", "C", "--s3-bucket", "D", "--source-path", "E"])
