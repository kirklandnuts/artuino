import serial
import serial.threaded
import sys
import time
import numpy as np
import queue
import traceback
import os
import csv

DEFAULT_DEVICE_PATH = '/dev/cu.usbmodem14101'
DEFAULT_SERIAL_RATE = 9600
DEFAULT_CACHE_SIZE = 10
DATA_LOG = False


class DeviceReader(serial.threaded.LineReader):
    def __init__(self):
        super(DeviceReader, self).__init__()
        self._cached_readings = queue.Queue(DEFAULT_CACHE_SIZE)
        self._range_list = []
        self._collect_range = True


    def handle_line(self, data):
        try:
            d = int(data)
            if d < 8191:
                self._cache_reading(d)
                if self._collect_range:
                    self._range_list.append(d)
        except:
            pass
        if DATA_LOG:
            print(data)

    def connection_lost(self, exc):
        raise exc
        # sys.stdout.write('port closed\n')

    def get_cached_readings(self):
        return list(self._cached_readings.queue)

    def get_range_list(self):
        self._collect_range = False
        return self._range_list

    def _cache_reading(self, reading):
        if self._cached_readings.full():
            self._cached_readings.get()
        self._cached_readings.put(reading)


class Device:
    
    def __init__(self, device_path=DEFAULT_DEVICE_PATH, serial_rate=DEFAULT_SERIAL_RATE,\
                 cache_size=DEFAULT_CACHE_SIZE, buffer=True):
        ser = serial.serial_for_url(device_path, baudrate=serial_rate, timeout=1)
        device_reader = serial.threaded.ReaderThread(ser, DeviceReader)
        device_reader._target = device_reader.run
        device_reader.start()
        self.device_reader = device_reader
        self.serial = ser
        self.cache_filled = False
        self.range_defined = False
        self.min = None
        self.max = None
    

    def distance(self):
        if not self.cache_filled:
            d = None
            if len(self.get_cache()) == DEFAULT_CACHE_SIZE:
                self.cache_filled = True
        if self.cache_filled:
            d = np.array(self.get_cache()).mean()
            if self.range_defined:
                d = self._threshold_value(d)
                d = self._scale_value(d)
        return d


    def define_range(self, verbose=False):
        range_list = self.device_reader.protocol.get_range_list()
        self.min = min(range_list)
        self.max = max(range_list)
        self.range_defined = True
        if verbose:
            print('Defined range: [{},{}]'.format(self.min, self.max))
        return self.min, self.max
    
    def get_cache(self):
        return self.device_reader.protocol.get_cached_readings()

    def _scale_value(self, value):
        '''scales distance proportionally so that 0 < d < 1
        '''
        return (value - self.min) / (self.max - self.min)


    def _threshold_value(self, value):
        r = value
        if value > self.max:
            r = self.max
        elif value < self.min:
            r = self.min
        return r



if __name__ == '__main__':
    device = Device()
    t0 = time.time()
    while True:
        if time.time() - t0 > 10:
            device.define_range(True)
        print('{} -> {}'.format(time.ctime(), device.distance()))
        time.sleep(0.25)