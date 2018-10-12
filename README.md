qmc5883-gas-counter
====================

# This is a patched version support the qmc5883 model. Byte registers are changed based von the Datasheet found here: http://osoyoo.com/driver/QMC5883L-Datasheet-1.0.pdf.
# The original version may be found ![here](https://github.com/skaringa/hmc5883-gas-counter).

Program to monitor the consumption of gas used for heating in a household .

Prerequisites
=============

* Gas counter with a rotating magnet
* Digital 3 axis magnetometer qmc5883L
* Raspberry Pi Model A or B
* Python 2.7

qmc5883\_gas\_counter.py
========================

![Gas counter with magnetometer qmc5883 breakout](http://www.kompf.de/tech/images/countmag_m.jpg)

This program uses the 3 axis magnetometer qmc5883 to read the magnetic induction which is produced by a gas counter. The gas counter contains a small magnet that is attached to a rotating counter ring. Each rotation of the counter ring means a consumption of 0.01 m³ gas. The magnetic induction produced by the rotating magnet is read with the magnetometer that is connected to the I²C bus of a Raspberry Pi.

The program monitors that magnetic induction and every time it detects a rotation of the magnet it writes the actual counter and consumption values into a round robin database. 

*Help:* 

  ./qmc5883\_gas\_counter.py -h

*Create rrd databases:*

  ./qmc5883\_gas\_counter.py -c

*Store values of magnetic induction into mag.rrd:*

  ./qmc5883\_gas\_counter.py -m

*Normal operation:*

  ./qmc5883\_gas\_counter.py


www
===

The sub-directory *www* contains an example to produce a single web page to visualize daily, weekly, monthly, and yearly charts of consumption.

![Consumption of gas recorded over 24 hours](http://www.kompf.de/tech/images/consum-ph1.gif)

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

