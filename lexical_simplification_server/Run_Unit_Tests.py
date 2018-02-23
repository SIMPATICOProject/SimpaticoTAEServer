import unittest
from lib import *
from Run_TCP_Lexical_Simplifier_Server import *

###################################################### UNIT TESTS ###################################################

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')




####################################################### RUN UNIT TESTS ################################################

if __name__ == '__main__':
    unittest.main()
