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

import sys
import os

from nysa.common import site_manager
from nysa.common.site_manager import SiteManagerError
from nysa.common import status as sts

NAME = "install-examples"
SCRIPT_NAME = "nysa %s" % NAME

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "install FPGA Project examples to the local system"
EPILOG = "Install a set of examples for a platform\n" + \
"if no example platform is specified then the remote examples are listed\n" + \
"if 'all' is specified then all platform available will be downloaded\n" + \
"and installed\n"

def setup_parser(parser):
    parser.description = DESCRIPTION
    parser.epilog = EPILOG
    parser.add_argument("name",
                        type = str,
                        nargs = '?',
                        default = "list",
                        help = "Specify what to install")

    return parser

def install(args, status):
    s = status
    sm = site_manager.SiteManager(status)
    names = []

    if s: s.Verbose("Args: %s" % str(args))
    user_path = None
    try:
        user_path = sm.get_nysa_user_base_directory()
    except SiteManagerError as ex:
        print "%sError: %s%s" % (sts.red, str(ex), sts.white)
        sys.exit(-1)

    ex_dict = sm.get_remote_example_dict()

    if args.name == "list":
        if s:s.Info("Get a list of the remote examples")

        print "%sExample packages:%s" % (sts.purple, sts.white)
        for name in ex_dict:
            print "\t%s%s%s" % (sts.blue, name, sts.white)
            print "\t\t%sAdded: %s%s" % (sts.green, ex_dict[name]["timestamp"], sts.white)
            print "\t\t%sRepo: %s%s" % (sts.green, ex_dict[name]["repository"], sts.white)

        sys.exit(0)

    if args.name == "all":
        if s:s.Info("Install all platforms")
        names = ex_dict.keys()
    else:
        names = [args.name]


    print "%sInstalling platforms examples%s " % (sts.purple, sts.white)
    for name in names:
        dest = os.path.join(user_path, "examples", name)
        print "%s\tInstalling %s to: %s%s" % (sts.blue, name, dest, sts.white)
        sm.install_examples(name, dest)
