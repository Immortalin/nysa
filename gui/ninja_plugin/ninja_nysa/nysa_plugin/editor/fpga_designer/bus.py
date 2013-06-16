# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

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

'''
Log
  6/14/2013: Initial commit
'''

import os
import sys
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4 import QtCore
from PyQt4.QtGui import *

from box import Box

from defines import PERIPHERAL_BUS_RECT
from defines import PERIPHERAL_BUS_POS
from defines import PERIPHERAL_BUS_COLOR
from defines import PERIPHERAL_BUS_ID

from defines import SLAVE_RECT
from defines import SLAVE_VERTICAL_SPACING
from defines import SLAVE_HORIZONTAL_SPACING

from link import Link
from link import link_type as lt
from link import side_type as st

#from fpga_designer import FPGADesignerError
import fpga_designer

class Bus(Box):
    """Host Interface Box"""

    def __init__(self,
                 position,
                 scene,
                 name,
                 color,
                 rect,
                 select_func,
                 deselect_func,
                 user_data,
                 master,
                 slave_class):

        super(Bus, self).__init__(position = position,
                                  scene = scene,
                                  name = name,
                                  color = color,
                                  select_func = select_func,
                                  deselect_func = deselect_func,
                                  rect = rect,
                                  user_data = user_data)
        #Need a reference to a master to update the link if the peripheral bus
        #   grows
        self.slave_class = slave_class
        self.master = master
        self.slaves = []
        self.links = {}

    def recalculate_size_pos(self):
        raise NotImplementedError("Subclass must implement this function")

    def find_index_from_position(self, position):
        index = 0
        for slave in self.slaves:
            pos = slave.pos()
            height = slave.rect.height()
            midpoint = pos.y() + (height/2)
            if position < midpoint:
                return index
            index += 1

        #at the end
        return -1
            

    def update_slaves(self, slave_list):
        #might need to change the slaves around
        #remove all the links
        for link in self.links:
            self.scene().removeItem(self.links[link])

        #remove all the slaves
        for slave in self.slaves:
            self.scene().removeItem(slave)

        self.links = {}
        self.slaves = []

        #add all the slaves/links
        for i in range(len(slave_list)):
            params = slave_list[i]
            instance_name = slave_list[i]["instance_name"]
            params = slave_list[i]["parameters"]
            slave = self.slave_class (scene = self.scene(),
                                      instance_name = instance_name,
                                      select_func = self.select_func,
                                      deselect_func = self.deselect_func,
                                      parameters = params)
            self.slaves.append(slave)
            self.links[slave] = Link(self, slave, self.scene(), lt.slave)
            self.links[slave].from_box_side(st.right)
            self.links[slave].to_box_side(st.left)
            self.recalculate_size_pos()
            self.update_links()

    def update_links(self):
        right_x = self.mapToScene(self.side_coordinates(st.right)).x()
        #print "Updating slave links"
        for i in range (len(self.slaves)):
            slave = self.slaves[i]
            link = self.links[slave]
            left = self.mapFromItem(slave, slave.side_coordinates(st.left))
            left = self.mapToScene(left)
            right = QPointF(right_x, left.y())
            link.set_start_end(right, left)
            #print "\tUpdating slave link: %s" % slave.box_name
            #print "\t\tlink start: %f,%f" % (right.x(), right.y())
            #print "\t\tlink end: %f,%f" % (left.x(), left.y())
            link.update()
 

    def add_slave(self, module_name, instance_name, index=-1):
        #the first slave should be at the same y position as the bus
        slave = slave_class      (scene = self.scene(),
                                 module_name = module_name,
                                 select_func = self.box_select,
                                 deselect_func = self.box_deselect,
                                 instance_name = instance_name)
        self.slaves.insert(index, slave)
        self.links[slave] = Link(self, slave, self.scene(), lt.slave)
        self.links[slave].from_box_side(st.right)
        self.links[slave].to_box_side(st.left)
        self.recalculate_size_pos()




    def remove_slave(self, instance_name = None, index = None):
        found_index = -1
        if instance_name is not None:
            for i in range(len(self.slaves)):
                if self.slaves[i].user_data == instance_name:
                    found_index = i
                    break

        elif index is None:
            raise fpga_designer.FPGADesignerError("index and instance name are not declared in remove_slave is not in peripheral bus")
        else:
            found_index = index

        slave = self.slaves[found_index]
        self.slaves.remove(found_index)
        self.scene().removeItem(slave)
        self.recalculate_size_pos()

    def move_slave(self, name = None, from_index = None, to_index = None):
        slave = self.slaves[from_index]
        self.slaves.insert(to_index, slave)
        self.slaves.remove(from_index)
        self.recalculate_size_pos()

    def update(self):
        self.master.update()
        super(Bus, self).update()
