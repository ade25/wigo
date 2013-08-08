import doctest
import unittest

from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

import wigo.statusapp

OPTION_FLAGS = doctest.NORMALIZE_WHITESPACE | \
               doctest.ELLIPSIS

ptc.setupPloneSite(products=['wigo.statusapp'])


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            zcml.load_config('configure.zcml',
              wigo.statusapp)

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='wigo.statusapp',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='wigo.statusapp.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'INTEGRATION.txt',
            package='wigo.statusapp',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),

        # -*- extra stuff goes here -*-

        # Integration tests for Compontent
        ztc.ZopeDocFileSuite(
            'Compontent.txt',
            package='wigo.statusapp',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        # Integration tests for ServerNode
        ztc.ZopeDocFileSuite(
            'ServerNode.txt',
            package='wigo.statusapp',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        # Integration tests for StatusApp
        ztc.ZopeDocFileSuite(
            'StatusApp.txt',
            package='wigo.statusapp',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
