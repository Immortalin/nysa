#! /usr/bin/python

#Distributed under the MIT licesnse.
#Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in 
#the Software without restriction, including without limitation the rights to 
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
#of the Software, and to permit persons to whom the Software is furnished to do 
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all 
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
#SOFTWARE.

from nysa.ibuilder.lib import utils
from nysa.common import status as st

NAME = "utils"
SCRIPT_NAME = "nysa %s" % NAME
DESCRIPTION = "utility functions"
EPILOG = "\n" \
         "Read Nysa version number\n" \
         "%s -v\n" % (SCRIPT_NAME)


def setup_parser(parser):
    parser.description = DESCRIPTION
    parser.add_argument("-v", "--verilog", action="store_true", help="display verilog packages")
    parser.add_argument("-u", "--update", action="store_true", help="update verilog and board packages")
    parser.add_argument("-c", "--clean", action="store_true", help="clean up the packages")
    #parser.add_argument("-b", "--boards", action="store_true", help="view the boards attached to this device")
    #parser.add_argument("-p", "--platforms", action="store_true", help="view the board platforms")
    return parser

def nysa_utils(args, status):
    s = status
    if args.clean:
        s.Info("Cleaning up verilog paths")
        utils.clean_verilog_package_paths()

    if args.update:
        s.Debug("Update verilog packages")
        vpackages = utils.get_local_verilog_path_dict()
        utils.clean_verilog_package_paths()
        for vpackage in vpackages:
            utils.update_verilog_package("nysa-verilog")
            s.Important("Updated %s, located at: %s" % ("nysa-verilog", utils.get_local_verilog_path("nysa-verilog")))

    if args.verilog:
        s.Important("View the verilog packages installed")
        print "%sVerilog Packages%s" % (st.purple, st.white)
        paths = utils.get_local_verilog_path_dict()
        for name in paths:
            print "\t%s%s: %s%s" % (st.blue, name, paths[name], st.white)

