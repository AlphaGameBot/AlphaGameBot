import unittest
import sys
import agb.tests as tests

suite = unittest.TestLoader().discover("agb/tests/", pattern="*.py")

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(suite)
 
    if result.errors or result.failures:
        exit(1)