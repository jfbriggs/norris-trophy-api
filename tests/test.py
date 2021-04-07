import unittest


class SampleTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)

    def test_subtract(self):
        self.assertEqual(2 - 1, 1)

    def test_multiply(self):
        self.assertEqual(1 * 3, 3, "1 * 3 should equal 3")

