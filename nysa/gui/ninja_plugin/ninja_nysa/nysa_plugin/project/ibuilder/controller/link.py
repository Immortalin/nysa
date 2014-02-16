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


#A huge thanks to 'Rapid GUI Programming with Python and Qt' by Mark Summerfield

#Thanks to http://github.com/woopeex edd repository... I love his picture too

'''
Log
  6/05/2013: Initial commit
'''

__author__ = "Dave McCoy dave.mccoy@cospandesign.com"


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from visual_graph.link import Link as VLink

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

link_type = enum(   "bus",
                    "host_interface",
                    "arbitor",
                    "slave",
                    "port",
                    "arbitor_master")


side_type = enum(   "top",
                    "bottom",
                    "right",
                    "left")

from defines import BEZIER_CONNECTION

from defines import LINK_ARBITOR_COLOR
from defines import LINK_BUS_COLOR
from defines import LINK_HOST_INTERFACE_COLOR
from defines import LINK_PORT_COLOR
from defines import LINK_MASTER_COLOR
from defines import LINK_SLAVE_COLOR
from defines import LINK_ARBITOR_MASTER_COLOR


padding = 20


class BoxLinkError(Exception):
    """
    Errors associated with Links between boxes

    Error associated with:
        -invalid side
        -invalid link type
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Link (VLink):

    def __init__(self, from_box, to_box, scene, ltype):
        super(Link, self).__init__(from_box, to_box, ltype = ltype)

    def paint(self, painter, option, widget):
        center_point = QLineF(self.start, self.end).pointAt(0.5)

        pen = self.pen
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setWidth(4)
        if self.link_type == link_type.bus:
            pen.setWidth(4)
        if self.link_type == link_type.host_interface:
            pen.setWidth(8)
        if self.link_type == link_type.arbitor:
            pen.setWidth(4)
        if self.link_type == link_type.port:
            pen.setWidth(4)
        if self.link_type == link_type.slave:
            pen.setWidth(2)
        if self.link_type == link_type.arbitor_master:
            pen.setWidth(2)

        painter.setPen(pen)
        path = QPainterPath()
        
        pstart = self.start_offset.p1()
        pend = self.end_offset.p1()

        if self.link_type == link_type.slave:
            pstart = QPointF(pstart.x(), pend.y())
            path.moveTo(pstart)
            path.lineTo(pend)
            #self.from_box.slave_adjust(mapToItem(from_box, pstart))

        else:
            one = (QPointF(pend.x(), pstart.y()) + pstart) / 2
            two = (QPointF(pstart.x(), pend.y()) + pend) / 2
            path.moveTo(pstart)

 
            if self.bezier_en:
                path.cubicTo(one, two, pend)
 
            else:
                if (pstart.x() + padding) < pend.x():
                    path.lineTo(one)
                    path.lineTo(two)
                    path.lineTo(pend)
  
                else:
                    start_pad = QPointF(pstart.x() + padding, pstart.y())
                    end_pad = QPointF(pend.x() - padding, pend.y())
                    center = QLineF(pstart, pend).pointAt(0.5)
                    one = (QPointF(start_pad.x(), center.y()))
                    two = (QPointF(end_pad.x(), center.y()))
  
  
                    path.lineTo(start_pad)
                    path.lineTo(one)
                    path.lineTo(two)
                    path.lineTo(end_pad)
                    path.lineTo(pend)

        #painter.drawRect(self.rect)
        #painter.drawText(self.rect, Qt.AlignCenter, "%s,%s" % (str(start.x()), str(start.y())))
        self.path = path
        painter.drawPath(path)





def get_color_from_type(lt):
    if lt == link_type.bus:
        return LINK_BUS_COLOR
    elif lt == link_type.host_interface:
        return LINK_HOST_INTERFACE_COLOR
    elif lt == link_type.arbitor:
        return LINK_ARBITOR_COLOR
    elif lt == link_type.port:
        return LINK_PORT_COLOR
    elif lt == link_type.slave:
        return LINK_SLAVE_COLOR
    elif lt == link_type.arbitor_master:
        return LINK_ARBITOR_MASTER_COLOR
    raise BoxLinkError("Invalid or undefined link type: %s, valid options \
            are: %s" % (str(lt), str(link_type)))

def get_inverted_side(side):
    if side == side_type.top:
        return side_type.bottom
    if side == side_type.bottom:
        return side_type.top
    if side == side_type.right:
        return side_type.left
    if side == side_type.left:
        return side_type.right
    #This should be an error
    raise BoxLinkError("Invalid side: %s" % str(side))
