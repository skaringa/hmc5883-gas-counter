#!/usr/bin/python -u
#
# qmc5883_gas_counter.py
# 
# Program to read the gas counter value by using the digital magnetometer HMC5883

# Copyright 2014 Martin Kompf
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import smbus
import time
import math
import rrdtool
import os
import re
import argparse

# Global data
# I2C bus (1 at newer Raspberry Pi, older models use 0)
bus = smbus.SMBus(1)
# I2C address of HMC5883
address = 0x0d

# Trigger level and hysteresis
trigger_level = 1000
trigger_hyst = 100
# Amount to increase the counter at each trigger event
trigger_step = 0.01

# Path to RRD with counter values
count_rrd = "%s/count.rrd" % (os.path.dirname(os.path.abspath(__file__)))

# Path to RRD with magnetometer values (for testing and calibration only)
mag_rrd = "%s/mag.rrd" % (os.path.dirname(os.path.abspath(__file__)))

# Read block data from HMC5883
def read_data():
  return bus.read_i2c_block_data(address, 0x00)

# Convert val to signed value
def twos_complement(val, len):
  if (val & (1 << len - 1)):
    val = val - (1<<len)
  return val

# Convert two bytes from data starting at offset to signed word
def convert_sw(data, offset):
  return twos_complement(data[offset] << 8 | data[offset+1], 16)

# Write one byte to HMC5883
def write_byte(adr, value):
  bus.write_byte_data(address, adr, value)

# Create the Round Robin Databases
def create_rrds():
  print 'Creating RRD: ' + mag_rrd
  # Create RRD to store magnetic induction values bx, by, bz:
  # 1 value per second
  # 86400 rows == 1 day
  try:
    rrdtool.create(mag_rrd, 
      '--no-overwrite',
      '--step', '1',
      'DS:bx:GAUGE:2:-2048:2048',
      'DS:by:GAUGE:2:-2048:2048',
      'DS:bz:GAUGE:2:-2048:2048',
      'RRA:AVERAGE:0.5:1:86400')
  except Exception as e:
    print 'Error ' + str(e)

  print 'Creating RRD: ' + count_rrd
  # Create RRD to store counter and consumption:
  # 1 trigger cycle matches consumption of 0.01 m**3
  # Counter is GAUGE
  # Consumption is ABSOLUTE
  # 1 value per minute for 3 days
  # 1 value per day for 30 days
  # 1 value per week for 10 years
  # Consolidation LAST for counter
  # Consolidation AVERAGE for consumption
  try:
    rrdtool.create(count_rrd, 
      '--no-overwrite',
      '--step', '60',
      'DS:counter:GAUGE:86400:0:100000',
      'DS:consum:ABSOLUTE:86400:0:1',
      'RRA:LAST:0.5:1:4320',
      'RRA:AVERAGE:0.5:1:4320',
      'RRA:LAST:0.5:1440:30',
      'RRA:AVERAGE:0.5:1440:30',
      'RRA:LAST:0.5:10080:520',
      'RRA:AVERAGE:0.5:10080:520')
  except Exception as e:
    print 'Error ' + str(e)

# Get the last counter value from the rrd database
def last_rrd_count():
  val = 0.0
  handle = os.popen("rrdtool lastupdate " + count_rrd)
  for line in handle:
    m = re.match(r"^[0-9]*: ([0-9.]*) [0-9.]*", line)
    if m:
      val = float(m.group(1))
      break
  handle.close()
  return val

# Write values of magnetic induction into mag rrd
# This is for testing and calibration only!
def write_mag_rrd(bx, by, bz):
  update = "N:%d:%d:%d" % (bx, by, bz)
  #print update
  rrdtool.update(mag_rrd, update)

# Main
def main():
  # Check command args
  parser = argparse.ArgumentParser(description='Program to read the gas counter value by using the digital magnetometer HMC5883.')
  parser.add_argument('-c', '--create', action='store_true', default=False, help='Create rrd databases if necessary')
  parser.add_argument('-m', '--magnetometer', action='store_true', default=False, help='Store values of magnetic induction into mag rrd')
  args = parser.parse_args()

  if args.create:
    create_rrds()

  # Init HMC5883
  write_byte(0, 0b01110000) # Rate: 8 samples @ 15Hz
  write_byte(1, 0b11100000) # Sensor field range: 8.1 Ga
  write_byte(2, 0b00000000) # Mode: Continuous sampling

  trigger_state = 0
  timestamp = time.time()
  counter = last_rrd_count()
  print "restoring counter to %f" % counter

  while(1==1):
    # read data from HMC5883
    data = read_data()
  
    # get x,y,z values of magnetic induction
    bx = convert_sw(data, 3) # x
    by = convert_sw(data, 7) # y 
    bz = convert_sw(data, 5) # z

    if args.magnetometer:
      # write values into mag rrd
      write_mag_rrd(bx, by, bz)

    # compute the scalar magnetic induction
    # and check against the trigger level
    old_state = trigger_state
    b = math.sqrt(float(bx*bx) + float(by*by) + float(bz*bz))
    if b > trigger_level + trigger_hyst:
      trigger_state = 1
    elif b < trigger_level - trigger_hyst:
      trigger_state = 0
    if old_state == 0 and trigger_state == 1:
      # trigger active -> update count rrd
      counter += trigger_step
      update = "N:%f:%f" % (counter, trigger_step)
      #print update
      rrdtool.update(count_rrd, update)
      timestamp = time.time()
    elif time.time() - timestamp > 3600:
      # at least on update every hour
      update = "N:%f:%f" % (counter, 0)
      #print update
      rrdtool.update(count_rrd, update)
      timestamp = time.time()

    time.sleep(1)

if __name__ == '__main__':
  main()
