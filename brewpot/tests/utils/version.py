import unittest
from brewpot.utils import version


class VersionTestFunction(unittest.TestCase):

    def test_version_final(self):
        v = (0, 1, 0, 'final', 0)
        v_str = version.get_version(v)
        self.assertEqual('0.1', v_str)

    def test_version_alpha(self):
        v = (0, 1, 0, 'alpha', 1)
        v_str = version.get_version(v)
        self.assertEqual('0.1a1', v_str)

if __name__ == '__main__':
    unittest.main()
