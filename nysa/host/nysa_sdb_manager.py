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


# -*- coding: utf-8 -*-


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

from common.status import Status

from cbuilder.sdb_component  import SDB_ROM_RECORD_LENGTH
from cbuilder import sdb_component as sdbc
from cbuilder import sdb_object_model as som
from cbuilder import som_rom_parser as srp
from cbuilder import device_manager
from cbuilder.sdb import SDBError

class NysaSDBManager(object):

    def __init__(self, status = None):
        self.s = status

        if self.s is None:
            self.s = Status()
            self.s.Important("Generating a new Status")

    #SOM Functions
    def get_number_of_devices(self):
        """
        Return the number of devices in the SDB Bus

        Args:
            Nothing

        Returns:
            (Integer) Number of devices on the SDB Bus

        Raises:
            Nothing
        """
        pass

    def find_device_from_ids(self, vendor_id = None, product_id = None):
        """
        Returns the URN of the device with the given vendor and or product ID

        Args:
            vendor_id (None or Integer): the vendor id number of the device
            product_id (None or Integer): the product id number of the device

        Returns:
            (String): URN of the device of the form:
            /peripherals/gpio1

        Raises:
            SDBError: device isn't found
        """
        pass

    def find_device_from_address(self, address):
        """
        Returns the URN of the device with the given address

        Args:
            address (Integer): the absolute base address of the device

        Returns:
            (String): URN of the device of the form:
            /peripherals/gpio1

        Raises:
            SDBError: device isn't found
        """
        pass

    def find_device_from_abi(self, abi_class = 0, abi_major = None, abi_minor = None):
        """
        Returns the URN of the device with the given address

        Args:
            abi_class (Nothing/Integer): class of the device, note abi_class has
                not been formally defined and this function may change for the
                future
            abi_major: (Nothing/Integer): major number of the device, refer to
                to the device list to find the associated number of a device
            abi_minor: (Nothing/Integer): minor nuber of the device, refer to
                the device list to find the associated number of a device

        Returns:
            (String): URN of the device of the form:
            /peripherals/gpio1

        Raises:
            SDBError: device isn't found
        """

        pass

    def read_sdb(self, n):
        """
        Reads the SDB of the device, this is used to initialize the SDB Object
        Model with the content of the SDB on the host

        Args:
            n (Nysa Instance): A reference to nysa that the controller will
                use to extrapolate the SDB from the device

        Returns:
            Nothing

        Raises:
            NysaCommError: Errors associated with communication
        """
        self.s.Important("Parsing Top Interconnect Buffer")
        #Because Nysa works with many different platforms we need to get the
        #platform specific location of where the SDB actually is
        #XXX: Create this function in nysa
        sdb_base_address = n.get_sdb_base_address()
        self.som = som.SOM()
        self.som.initialize_root()
        bus = self.som.get_root()
        _parse_bus(n, self.som, bus, sdb_base_address, sdb_base_address, self.s)

    def is_wishbone_bus(self, urn = None):
        """
        Returns true if the SDB bus is a wishbone bus

        Args:
            urn (None/String): Absolute reference to the bus
                leave blank for root

        Returns (Boolean):
           True: Is a wishbone bus 
           False: Not a wishbone bus

        Raises:
            Nothing
        """
        root = self.som.get_root()
        c = root.get_component()
        if c.get_bus_type_as_int() == 0

    def is_axi_bus(self):
        """
        Returns true if the SDB bus is an axi bus

        Args:
            urn (None/String): Absolute reference to the bus
                leave blank for root

        Returns (Boolean):
           True: Is an axi bus 
           False: Not an axi bus

        Raises:
            Nothing
        """

        raise AssertionError("AXI bus not implemented yet")

    def is_storage_bus(self):
        """
        Returns true if the SDB bus is a storage bus

        Args:
            urn (None/String): Absolute reference to the bus
                leave blank for root

        Returns (Boolean):
           True: Is a storage bus 
           False: Not a storage bus

        Raises:
            Nothing
        """
        root = self.som.get_root()
        c = root.get_component()
        return c.get_bus_type_as_int() == 1

    def get_total_memory_size(self):
        pass

    #Device Functions
    def get_device_address(self, urn):
        pass

    def get_device_size(self, urn):
        pass

    def get_device_vendor_id(self, urn):
        pass

    def get_device_product_id(self, urn):
        pass

    def get_device_size(self, urn):
        pass

    def get_device_abi_class(self, urn):
        pass

    def get_device_abi_major(self, urn):
        pass

    def get_device_abi_minor(self, urn):
        pass

    #Board Functions
    def get_board_name(self):
        pass

    #Helpful Fuctions
    def pretty_print_sdb(self):
        self.s.Verbose("pretty print SDB")
        self.s.PrintLine("SDB ", color = "blue")
        #self.som
        root = self.som.get_root()
        self._print_bus(root, depth = 0)

    def _print_bus(self, bus, depth = 0):
        c = bus.get_component()
        for t in range(depth):
            self.s.Print("\t")
        s = "Bus: {0:<10} @ 0x{1:0=16X} : Size: 0x{2:0=8X}".format(bus.get_name(), c.get_start_address_as_int(), c.get_size_as_int())
        self.s.PrintLine(s, "purple")

        for i in range(bus.get_child_count()):
            c = bus.get_child_from_index(i)
            if self.som.is_entity_a_bus(bus, i):
                self._print_bus(c, depth = depth + 1)
            else:
                c = bus.get_child_from_index(i)
                c = c.get_component()
                major = c.get_abi_version_major_as_int()
                minor = c.get_abi_version_minor_as_int()
                dev_name = device_manager.get_device_name_from_id(major)
                for t in range(depth + 1):
                    self.s.Print("\t")
                s = "{0:20} Type (Major:Minor) ({1:0=2X}:{2:0=2X}): {3:10}".format(c.get_name(),
                                                   major,
                                                   minor,
                                                   dev_name)

                self.s.PrintLine(s, "green")
                for t in range(depth + 1):
                    self.s.Print("\t")
                s = "Address:        0x{0:0=16X}-0x{1:0=16X} : Size: 0x{2:0=8X}".format(c.get_start_address_as_int(),
                                                                    c.get_end_address_as_int(),
                                                                    c.get_size_as_int())
                self.s.PrintLine(s, "green")
                for t in range(depth + 1):
                    self.s.Print("\t")
                s = "Vendor:Product: {0:0=16X}:{1:0=8X}".format(c.get_vendor_id_as_int(),
                                                                c.get_device_id_as_int())

                self.s.PrintLine(s, "green")
                self.s.PrintLine("")


def _parse_bus(n, som, bus, addr, base_addr, status):
    #The first element at this address is the interconnect
    status.Verbose("Bus @ 0x%08X" % addr)
    entity_rom = n.read(addr, SDB_ROM_RECORD_LENGTH / 4)
    #print_sdb_rom(sdbc.convert_rom_to_32bit_buffer(entity_rom))
    bus_entity = srp.parse_rom_element(entity_rom)
    if not bus_entity.is_interconnect():
        raise SDBError("Rom data does not point to an interconnect")
    num_devices = bus_entity.get_number_of_records_as_int()
    status.Verbose("\tFound %d Devices" % num_devices)
    som.set_bus_component(bus, bus_entity)
    #print "Found bus: %s" % bus_entity.get_name()

    entity_size = []
    entity_addr_start = []

    for i in range(1, (num_devices + 1)):
        I = (i * (SDB_ROM_RECORD_LENGTH / 4)) + addr
        entity_rom = n.read(I, SDB_ROM_RECORD_LENGTH / 4)
        #print_sdb_rom(sdbc.convert_rom_to_32bit_buffer(entity_rom))
        entity = srp.parse_rom_element(entity_rom)
        end = long(entity.get_end_address_as_int())
        start = long(entity.get_start_address_as_int())
        entity_addr_start.append(start)
        entity_size.append(end - start)

        if entity.is_bridge():
            #print "Found bridge"
            sub_bus = som.insert_bus(root = bus,
                                     name = entity.get_name())
            sub_bus_addr = entity.get_bridge_address_as_int() * 2 + base_addr
            _parse_bus(n, som, sub_bus, sub_bus_addr, base_addr, status)
        else:
            som.insert_component(root = bus, component = entity)
            status.Verbose("Found device %s Type (0x%02X): %s" % (
                                            entity.get_name(),
                                            entity.get_abi_version_major_as_int(),
                                            device_manager.get_device_name_from_id(entity.get_abi_version_major_as_int())))
            #print_sdb_rom(sdbc.convert_rom_to_32bit_buffer(entity_rom))

    #Calculate Spacing
    spacing = 0
    prev_start = None
    prev_size = None
    for i in range (num_devices):
        size = entity_size[i]
        start_addr = entity_addr_start[i]
        if prev_start is None:
            prev_size = size
            prev_start = start_addr
            continue

        potential_spacing = (start_addr - prev_start)
        if potential_spacing > prev_size:
            if potential_spacing > 0 and spacing == 0:
                spacing = potential_spacing
            if spacing > potential_spacing:
                spacing = potential_spacing

        prev_size = size
        prev_start = start_addr

    som.set_child_spacing(bus, spacing)


def print_sdb_rom(rom):
    #rom = sdbc.convert_rom_to_32bit_buffer(rom)
    rom = rom.splitlines()
    print "ROM"
    for i in range (0, len(rom), 4):
        if (i % 16 == 0):
            magic = "0x%s" % (rom[i].lower())
            last_val = int(rom[i + 15], 16) & 0xFF
            print ""
            if (magic == hex(sdbc.SDB_INTERCONNECT_MAGIC) and last_val == 0):
                print "Interconnect"
            elif last_val == 0x01:
                print "Device"
            elif last_val == 0x02:
                print "Bridge"
            elif last_val == 0x80:
                print "Integration"
            elif last_val == 0x81:
                print "URL"
            elif last_val == 0x82:
                print "Synthesis"
            elif last_val == 0xFF:
                print "Empty"
            else:
                print "???"

        print "%s %s : %s %s" % (rom[i], rom[i + 1], rom[i + 2], rom[i + 3])

