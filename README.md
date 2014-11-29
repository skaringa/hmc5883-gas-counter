hmc5883-gas-counter
====================

Program to monitor the consumption of gas used for heating in a household .

Prerequisites
=============

* Gas counter with a rotating magnet
* Digital 3 axis magnetometer HMC5883L
* Raspberry Pi Model A or B
* Python 2.7

hmc5883\_gas\_counter.py
========================

This program uses a 3 axis magnetometer to read the magnetic induction that is produced by a gas counter. The gas counter contains a small magnet that is attached to a rotating counter ring. Each rotation of the counter ring means a consumption of 0.01 m³ gas. The magnetic induction produced by the rotating magnet is read with a 3 axis magnetometer that is attached to the I²C bus of a Raspberry Pi.

The program monitors that magnetic induction and every time it detects a rotation of the magnet it writes the actual counter and consumption values into a round robin database. 

*Help:* 

  ./hmc5883\_gas\_counter.py -h

*Create rrd databases:*

  ./hmc5883\_gas\_counter.py -c

*Store values of magnetic induction into mag.rrd:*

  ./hmc5883\_gas\_counter.py -m

*Normal operation:*

  ./hmc5883\_gas\_counter.py

License
=======

Copyright 2014 Martin Kompf

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

