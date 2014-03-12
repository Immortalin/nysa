#! /usr/bin/python

# Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (wiki.cospandesign.com/index.php?title=Nysa).
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.


"""
app template controller
"""

__author__ = 'email@example.com (name)'

import os
import sys
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "common"))

from nysa_base_controller import NysaBaseController

from view.view import View
from model.model import AppModel

from PyQt4.Qt import QApplication

#Module Defines
n = str(os.path.split(__file__)[1])

DESCRIPTION = "\n" \
"\n"\
"A template app\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\t%s Something\n"\
"\n" % n


class Controller(NysaBaseController):

    def __init__(self):
        super (Controller, self).__init__()
        self.m = AppModel()

    def start_standalone_app(self):
        app = QApplication (sys.argv)
        self.v = View(self.status, self.actions)
        self.v.setup_simple_text_output_view()
        sys.exit(app.exec_())

    def get_unique_image_id(self):
        """
        If this ia controller for an entire image return the associated unique
        image ID here
        """
        return None

    def get_device_id(self):
        """
        If this is a controller for an individual device (GPIO, I2C, UART,
        etc...) return the associted device ID here (notes for the device are in
        /nysa/cbuilder/drt/drt.json
        """
        return None

    def get_device_sub_id(self):
        """
        If this is a controller for an individual device with that has a
        specific implementation (Cospan Design's version of a GPIO controller
        as apposed to just a generic GPIO controller) return the sub ID here
        """
        return None

    def get_device_unique_id(self):
        """
        Used to differentiate devices with the same device/sub ids.
        """
        return None


def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = DESCRIPTION,
            epilog = EPILOG
    )
    debug = False

    parser.add_argument("-d", "--debug",
                        action = "store_true",
                        help = "Enable Debug Messages")

    args = parser.parse_args()

    if args.debug:
        print ("Debug Enable")
        debug = True

    c = Controller()
    c.start_standalone_app()

if __name__ == "__main__":
    main(sys.argv)