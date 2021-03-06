import doctest
import unittest

from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

import wigo.crmtool

OPTION_FLAGS = doctest.NORMALIZE_WHITESPACE | \
               doctest.ELLIPSIS

ptc.setupPloneSite(products=['wigo.crmtool'])


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            zcml.load_config('configure.zcml',
              wigo.crmtool)

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='wigo.crmtool',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='wigo.crmtool.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'INTEGRATION.txt',
            package='wigo.crmtool',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),

        # -*- extra stuff goes here -*-

        # Integration tests for HostedDomain
        ztc.ZopeDocFileSuite(
            'HostedDomain.txt',
            package='wigo.crmtool',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        # Integration tests for CRMTool
        ztc.ZopeDocFileSuite(
            'CRMTool.txt',
            package='wigo.crmtool',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        # Integration tests for Customer
        ztc.ZopeDocFileSuite(
            'Customer.txt',
            package='wigo.crmtool',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
