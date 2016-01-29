##
# This software was developed and / or modified by Raytheon Company,
# pursuant to Contract DG133W-05-CQ-1067 with the US Government.
# 
# U.S. EXPORT CONTROLLED TECHNICAL DATA
# This software product contains export-restricted data whose
# export/transfer/disclosure is restricted by U.S. law. Dissemination
# to non-U.S. persons whether in the United States or abroad requires
# an export license or other authorization.
# 
# Contractor Name:        Raytheon Company
# Contractor Address:     6825 Pine Street, Suite 340
#                         Mail Stop B8
#                         Omaha, NE 68106
#                         402.291.0100
# 
# See the AWIPS II Master Rights File ("Master Rights File.pdf") for
# further licensing information.
##

from __future__ import print_function
from ufpy.dataaccess import DataAccessLayer as DAL

import baseDafTestCase
import dafTestsArgsUtil
import sys
import unittest

class GridTestCase(baseDafTestCase.DafTestCase):
    """
    Tests that grid data can be retrieved through the DAF, primarily ensuring
    that no unexpected exceptions are thrown while retrieving it and that the
    returned data is not None. The only data validation that is performed is to
    check that all retrieved grid data have the same shape.
    """

    datatype = "grid"

    model = "GFS160"

    @classmethod
    def setUpClass(cls):
        print("STARTING GRID TESTS\n\n")

    def testParameters(self):
        req = DAL.newDataRequest(self.datatype)
        req.addIdentifier("info.datasetId", self.model)

        self.runParametersTest(req)

    def testLocations(self):
        req = DAL.newDataRequest(self.datatype)
        req.addIdentifier("info.datasetId", self.model)

        self.runLocationsTest(req)

    def testLevels(self):
        req = DAL.newDataRequest(self.datatype)
        req.addIdentifier("info.datasetId", self.model)

        self.runLevelsTest(req)

    def testTimes(self):
        req = DAL.newDataRequest(self.datatype)
        req.addIdentifier("info.datasetId", self.model)
        req.setLevels("2FHAG")

        self.runTimesTest(req)

    def testGridData(self):
        req = DAL.newDataRequest(self.datatype)
        req.addIdentifier("info.datasetId", self.model)
        req.setLevels("2FHAG")
        req.setParameters("T")

        self.runGridDataTest(req)

    @classmethod
    def tearDownClass(cls):
        print("GRID TESTS COMPLETE\n\n\n")

def getArgs():
    parser = dafTestsArgsUtil.getParser()
    parser.add_argument("-m", action="store", dest="model", default=GridTestCase.model,
                        help="model to retrieve data for",
                        metavar="modelName")
    return parser.parse_args()

if __name__ == '__main__':
    args = getArgs()
    dafTestsArgsUtil.handleArgs(args)
    GridTestCase.model = args.model
    unittest.main(argv=sys.argv[:1])
