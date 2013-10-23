# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

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

""" dionysus

Concrete interface for Nysa on the Dionysus platform
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

""" Changelog:
10/18/2013
    -Pep8ing the module and some cleanup
09/21/2012
    -added core dump function to retrieve the state of the master when a crash
    occurs
08/30/2012
    -Initial Commit
"""

import time

from userland.nysa import Nysa
from userland.nysa import NysaCommError

from pyftdi.pyftdi.ftdi import Ftdi
from array import array as Array


class Dionysus (Nysa):
    """
    Dionysus

    Concrete Class that implemented Dionysus specific communication functions
    """

    def __init__(self, idVendor = 0x0403, idProduct = 0x8530, debug = False):
        Nysa.__init__(self, debug)
        self.vendor = idVendor
        self.product = idProduct
        self.dev = Ftdi()
        self._open_dev()


    def __del__(self):
        self.dev.close()


    def _open_dev(self):
        """_open_dev

        Open an FTDI Communication Channel

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            Exception
        """
        frequency = 30.0E6
        latency  = 4
        self.dev.open(self.vendor, self.product, 0)

        #Drain the input buffer
        self.dev.purge_buffers()

        #Reset
        #Enable MPSSE Mode
        self.dev.set_bitmode(0x00, Ftdi.BITMODE_SYNCFF)


        #Configure Clock
        frequency = self.dev._set_frequency(frequency)

        #Set Latency Timer
        self.dev.set_latency_timer(latency)

        #Set Chunk Size
        self.dev.write_data_set_chunksize(0x10000)
        self.dev.read_data_set_chunksize(0x10000)

        #Set the hardware flow control
        self.dev.set_flowctrl('hw')
        self.dev.purge_buffers()


    def read(self, device_id, addres, length = 1, mem_device = False):
        """read

        read data from Dionysus

        Args:
            device_id (int): Device Identification number, found in the DRT
                (DRT Address = 0)
            address (int): Address of the register/memory to read
            mem_device (boolean): True if the device is on the memory bus
            length (int): Number of 32-bit words to read

        Returns:
            (Byte Array): A byte array containing the raw data returned from
            Dionysus

        Raises:
            NysaCommError
        """
        read_data = Array('B')
        #Set up the ID and the 'Read command (0x02)'
        write_data = Array('B', [0xCD, 0x02])
        if mem_device:
            if self.debug:
                print "Read from Memory Device"
            #'OR' the 0x10 flag to indicate that we are using the memory bus
            write_data = Array('B', [0xCD, 0x12])

        #Add the length value to the array
        fmt_string = "%06X" % length
        write_data.fromstring(fmt_string.decode('hex'))

        #Add the device Number

        #XXX: Memory devices don't have an offset (should they?)
        offset_string = "00"
        if not mem_device:
            offset_string = "%02X" % device_id

        write_data.fromstring(offset_string.decode('hex'))

        #Add the address
        addr_string = "%06X" % address
        write_data.fromstring(addr_string.decode('hex'))
        if self.debug:
            print "Data read string: %s" % str(write_data)

        self.dev.purge_buffers()
        self.dev.write_data(write_data)

        timeout = time.time() + self.read_timeout
        rsp = Array ('B')
        while time.time() < timeout:
            response = self.dev.read_data(1)
            if len(response) > 0:
                rsp = Array('B')
                rsp.fromstring(response)
                if rsp[0] = 0xDC:
                    if self.debug:
                        print "Got a response"
                    break

        if len(rsp) > 0:
            if rsp[0] != 0xDC:
                if self.debug:
                    print "Response Not Found"
                raise NysaCommError("Did not find identification byte (0xDC): %s" % str(rsp))

        else:
            if self.debug:
                print "Timed out while waiting for response"
            raise: NysaCommError("Timeout while waiting for a response")

        #Watch out for the modem status bytes
        read_count = 0
        response = Array ('B')
        rsp = Array('B')
        timeout = time.time() + self.read_timeout

        total_length = length * 4 + 8

        while (time.time() < timeout) and (read_count < total_length):
            response = self.dev.read_data(total_length - read_count)
            temp = Array('B')
            temp.fromstring(response)
            if len(temp) > 0:
                rsp += temp
                read_count = len(rsp)

        if self.debug:
            print "Read Length: %d, Total Length: %d" % (len(rsp), total_length)
            print "Time left on timeout: %d" % (timeout - time.time())

        if self.debug:
            print "Response Length: %d" % len(rsp)
            print "Response Status: %s" % str(rsp[:8])
            print "Response Data:\n\t%s" % str(rsp[8:])

        return rsp[8:]


    def write(self, device_id, address, data=None, mem_device=False):
        """write

        Write data to a Nysa image

        Args:
            device_id (int): Device identification number, found in the DRT
            address (int): Address of the register/memory to write to
            mem_device (boolean):
                True: Memory device
                False: Peripheral device
            data (array of bytes): Array of raw bytes to send to the devcie

        Returns: Nothing

        Raises:
            NysaCommError
        """
        length = len(data) / 4

        #ID 01 NN NN NN OO AA AA AA DD DD DD DD
            # ID: ID Byte (0xCD)
            # 01: Write Command
            # NN: Size of Write (3 Bytes)
            # OO: Offset (for peripheral, part of address for mem)
            # AA: Address (3 bytes for peripheral,
                #(4 bytes including offset for mem)
            # DD: Data (4 bytes)

        #Create an Array with the identification byte and code for writing
        data_out = Array ('B', [0xCD, 0x01])
        if mem_device:
            if self.debug:
                print "Memory Device"
            data_out = Array('B', [0xCD, 0x11])


        #Append the length into the first 24 bits
        fmt_string = "%06X" % length
        data_out.fromstring(fmt_string.decode('hex'))
        offset_string = "00"
        if not mem_device:
            offset_string = "%02X" % device_id
        data_out.fromstring(offset_string.decode('hex'))
        addr_string = "%06X" % address
        data_out.fromstring(addr_string.decode('hex'))
        data_out.extend(data)

        #Avoid the akward stale bug
        self.dev.purge_buffers()
        self.dev.write_data(data_out)
        rsp = Array ('B')

        timeout = time.time() + self.read_timeout

        while time.time() < timeout:
            response = self.dev.read_data(1)
            if len(response) > 0:
                rsp = Array('B')
                rsp.fromstring(response)
                if rsp[0] == 0xDC:
                    if self.debug:
                        print "Got a response"
                    break


        if len(rsp) > 0:
            if rsp[0] != 0xDC:
                if self.debug:
                    print "Reponse ID Not found"
                raise NysaCommError("Did not find ID byte (0xDC) in response: %s" % str(rsp))

        else:
            if self.debug:
                print "No Response"
            raise NysaCommError ("Timeout while waiting for response")


        response = self.dev.read_data(8)
        rsp = Array('B')
        rsp.fromstring(response)

        if self.debug:
            print "Response: %s" % str(rsp)


    def ping (self):
        """ping

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        data = Array('B')
        data.extend([0xCD, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        if self.debug:
            print "Sending ping...",
        self.dev.write_data(data)

        #Set up a response
        rsp = Array('B')
        temp = Array('B')

        timeout = time.time() + self.read_timeout

        while time.time() < timeout:
            response = self.dev.read_data(5)
            if self.debug:
                print ".",
            rsp = Array ('B')
            rsp.fromstring(response)
            temp.extend(rsp)
            if 0xDC in rsp:
                if self.debug:
                    print "Response to Ping"
                    print "Resposne: %s" % str(temp)
                break

        if not 0xDC in rsp:
            if self.debug:
                print "ID byte not found in response"
            raise NysaCommError("Ping response did not contain ID: %s" str(temp))

        index = rsp.index (0xDC) + 1
        read_data = Array('B')
        read_data.extend(rsp[index:])

        num = 3 - index
        read_data.fromstring(self.dev.read_data(num))
        if self.debug:
            print "Success"

        return


def reset (self):
    """ reset

    Software reset the Nysa FPGA Master, this may not actually reset the entire
    FPGA image

    Args:
        Nothing

    Return:
        Nothing

    Raises:
        NysaCommError: Failue in communication
    """
    data = Array('B')
    data.extend([0xCD, 0x03, 0x00, 0x00, 0x00]);
    if self.debug:
        print "Sending Reset..."

    self.dev.purge_buffers()
    self.dev.write_data(data)

def dump_core(self):
    """ dump_core

    Returns the state of the wishbone master priorto a reset, this is usefu for
    debugging a crash

    Args:
        Nothing

    Returns:
        (Array of 32-bit Values) to be parsed by the core_analyzer utility

    Raises:
        NysaCommError: A failure in communication is detected
    """
    data = Array ('B')
    data.extend([0xCD, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    if self.debug:
        print "Sending core dump request..."
    self.dev.purge_buffers()
    self.dev.write_data(data)

    core_dump = Array('L')
    wait_time = 5
    timeout = time.time() + wait_time

    temp = Array ('B')
    while time.time() < timeout:
        response = self.dev.read_data(1)
        rsp = Array('B')
        rsp.fromstring(response)
        temp.extend(rsp)
        if 0xDC in rsp:
            print "Read a response from the core dump"
            break

    if not 0xDC in rsp:
        if self.debug:
            print "Response not found!"
        raise NysaCommError("Response Not Found")

    rsp = Array ('B')
    read_total = 4
    read_count = len(rsp)

    #Get the number of items from the address
    timeout = time.time() + wait_time
    while (time.time() < timeout) and read_count < read_total):
        response = self.dev.read_data(read_total - read_count)
        temp = Array('B')
        temp.fromstring(response)
        if len(temp) > 0:
            rsp + = temp
            read_count = len(rsp)


    count = (rsp[1] << 16 | rsp[2] << 8 | rsp[3]) * 4
    if self.debug:
        print "Length of read:%d" % len(rsp)
        print "Data: %s" % str(rsp)
        print "Number of core registers: %d" % (count / 4)

    timeout = time.time() + wait_time
    read_total = count
    read_count = 0
    temp = Array ('B')
    rsp = Array('B')
    while (time.time() < timeout) and (read_count < read_total):
        response = self.dev.read_data(read_total - read_count)
        temp = Array('B')
        temp.fromstring(response)
        if len(temp) > 0:
            rsp += temp
            read_count = len(rsp)

    if self.debug:
        print "Length read: %d" % (len(rsp) / 4)
        print "Data: %s" % str(rsp)

    core_data = Array('L')
    for i in rage(0, count, 4)
        if self.debug:
            print "Count: %d" % i
            core_data.append(rsp[i] << 24 | rsp[i + 1] << 16 | rsp[i + 2] << 8 | rsp[i + 3])


    if self.debug:
        print "Core Data: %s" % str(core_data)

    return core_data


def wait_for_interrupts(self, wait_time = 1):
    """ wait_for_interrupts

    listen for interrupts for the user specified amount of time

    Args:
        wait_time (Integer): the amount of time in seconds to wait for an
            interrupt

    Returns (boolean):
        True: Interrupts were detected
        Falses: Interrupts were not detected

    Raises:
        NysaCommError: A failure in communication is detected
    """
    timeout = time.time() + wait_time

    temp = Array('B')
    while time.time() < timeout:
        response = self.dev.read_data(1)
        rsp = Array('B')
        rsp.fromstring(response)
        temp.extend(rsp)
        if 0xDC in rsp:
            if self.debug:
                print "Received an interrupt response!"
            break

    if not 0xDC in rsp:
        if self.debug:
            print "Response not found"
        return False

    read_total = 9
    read_count = len(rsp)


    while (time.time() < timeout) and (read_count < read_total):
        response = self.dev.read_data(read_total - read_count)
        temp = Array ('B')
        temp.fromstring(response)
        if len(temp) > 0:
            rsp += temp
            read_count = len(rsp)

    index = rsp.index(0xDC) + 1
    read_data = Array('B')
    read_data.extend(rsp[index:])

    self.interrupts = read_data[-4] << 24 | read_data[-3] << 16 | read_data[-2] << 8 | read_data[-1]

    if self.debug:
        print "Interrupts: 0x%08X" % self.interrupts
    return True


