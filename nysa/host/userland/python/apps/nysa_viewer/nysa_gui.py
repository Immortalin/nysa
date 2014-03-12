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


""" nysa interface
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'


import argparse
import sys
import os
from PyQt4.Qt import *
from PyQt4.QtCore import *

p = os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common")

sys.path.append(p)

from platform_scanner import PlatformScanner

from view.main_view import MainForm
from status import Status
from actions import Actions

DESCRIPTION = "\n" \
"\n"\
"usage: nysa.py [options]\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\ttest_dionysus.py\n"\
"\n"

debug = False

class NysaGui(QObject):

    def __init__(self):
        super (NysaGui, self).__init__()

        app = QApplication(sys.argv)
        self.mf = MainForm()
        self.fv = self.mf.get_fpga_view()
        self.actions = Actions()
        self.status = Status()
        self.status.Debug(self, "Created main form!")

        self.uid = None

        #Connect the action signal to a local function
        self.actions.refresh_signal.connect(self.refresh_platform_tree)
        self.actions.platform_tree_changed_signal.connect(self.nysa_device_changed)
        self.refresh_platform_tree()
        sys.exit(app.exec_())

    def refresh_platform_tree(self):
        self.actions.clear_platform_tree_signal.emit()
        ps = PlatformScanner(self.status)
        platforms_dict = ps.get_platforms()

        for pis in platforms_dict:
            print "pis: %s" % pis
            for pi in platforms_dict[pis]:
                print "pi: %s" % str(pi)
                self.status.Info(self, "Refresh The Platformsical Tree")
                t = platforms_dict[pis][pi]
                self.actions.add_device_signal.emit(pis, pi, t)
         
            self.actions.platform_tree_get_first_dev.emit()


    def nysa_device_changed(self, uid, dev_type, nysa_device):
        if self.uid == uid:
            #Don't change anything if it's the same UID
            self.status.Verbose(self, "Same UID, no change")
            return

        self.status.Debug(self, "Device Changed")
        self.dev_type = dev_type
        if dev_type is None:
            self.n = None
            self.status.Info(self, "No Device Selected")
            self.fv.clear()
            return

        self.uid = uid
        self.n = nysa_device

        self.n.read_drt()
        config_dict = drt_to_config(self.n)
        self.fv.update_nysa_image(self.n, config_dict)


def drt_to_config(n):

    config_dict = {}

    #Read the board id and find out what type of board this is
    config_dict["board"] = n.get_board_name()
    print "Name: %s" % config_dict["board"]

    #Read the bus flag (Wishbone or Axie)
    if n.is_wishbone_bus():
        config_dict["bus_type"] = "wishbone"
        config_dict["TEMPLATE"] = "wishbone_template.json"
    if n.is_axie_bus():
        config_dict["bus_type"] = "axie"
        config_dict["TEMPLATE"] = "axie_template.json"

    config_dict["SLAVES"] = {}
    config_dict["MEMORY"] = {}
    #Read the number of slaves
    #Go thrugh each of the slave devices and find out what type it is
    for i in range (n.get_number_of_devices()):
        if n.is_memory_device(i):
            name = "Memory %d" % i
            config_dict["MEMORY"][name] = {}
            config_dict["MEMORY"][name]["sub_id"] = n.get_device_sub_id(i)
            config_dict["MEMORY"][name]["unique_id"] = n.get_device_unique_id(i)
            config_dict["MEMORY"][name]["address"] = n.get_device_address(i)
            config_dict["MEMORY"][name]["size"] = n.get_device_size(i)
            continue

        name = n.get_device_name_from_id(n.get_device_id(i))
        config_dict["SLAVES"][name] = {}
        #print "Name: %s" % n.get_device_name_from_id(n.get_device_id(i))
        config_dict["SLAVES"][name]["id"] = n.get_device_id(i)
        config_dict["SLAVES"][name]["sub_id"] = n.get_device_sub_id(i)
        config_dict["SLAVES"][name]["unique_id"] = n.get_device_unique_id(i)
        config_dict["SLAVES"][name]["address"] = n.get_device_address(i)
        config_dict["SLAVES"][name]["size"] = n.get_device_size(i)

    config_dict["INTERFACE"] = {}
    return config_dict
    #Read the number of memory devices




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

    n = NysaGui()

if __name__ == "__main__":
    main(sys.argv)
