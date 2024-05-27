import unittest

import agb.tests as tests

suite = unittest.TestLoader().discover("agb/tests/", pattern="*.py")

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite)
 