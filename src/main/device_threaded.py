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
DEFAULT_CACHE_SIZE = 25
DATA_LOG = False


class DeviceReader(serial.threaded.LineReader):
    def __init__(self):
        super(DeviceReader, self).__init__()
        self._cached_readings = queue.Queue(DEFAULT_CACHE_SIZE)
        self._last_reading = None
        # self.save_path = os.path.join(SAVE_DIR, SAVE_NAME)
        # with open(self.save_path, mode='w') as f:
        #     f_writer = csv.writer(f, delimiter=',')
        #     f_writer.writerow(['time','distance','yaw','pitch','roll','accel_x','accel_y','accel_z'])


    def handle_line(self, data):
        if data == self._last_reading:
            raise Exception('no new data')
        # self._last_reading = data
        if data != 'FIFO overflow!':
            data_list = [float(i) for i in data.split(',')]
            timestamp = time.time()
            # if WRITE_DATA:
            #     if len(data_list) == 7:
            #         with open(self.save_path, mode='a') as f:
            #             f_writer = csv.writer(f, delimiter=',')
            #             f_writer.writerow([timestamp] + data_list)
            # if len(data_list) == 7:
            #     reading = { 
            #         'time':timestamp,
            #         'data':data_list
            #     }
            #     self._cache_reading(reading)
        if DATA_LOG:
            print(data)


    def connection_lost(self, exc):
        raise exc
        # sys.stdout.write('port closed\n')


    def get_cached_readings(self):
        return list(self._cached_readings.queue)


    def _cache_reading(self, reading):
        if self._cached_readings.full():
            self._cached_readings.get()
        self._cached_readings.put(reading)


class Device:
    def __init__(self, device_path=DEFAULT_DEVICE_PATH, serial_rate=DEFAULT_SERIAL_RATE, cache_size=DEFAULT_CACHE_SIZE, buffer=True):
        print('==== INITIALIZING DEVICE')
        ser = serial.serial_for_url(device_path, baudrate=serial_rate, timeout=1)
        device_reader = serial.threaded.ReaderThread(ser, DeviceReader)
        device_reader._target = device_reader.run
        device_reader.start()
        self.device_reader = device_reader
        self.serial = ser
        self.ready = False
        if buffer:
            self._buffer()
        print('==== DEVICE INITIALIZED')

    
    def measure(self):
        '''returns a dictionary containing 
            velocity (m/s)
            distance (mm)
        '''
        metrics = None
        if self.ready_to_measure():
            readings = self.get_readings()
            metrics = {
                'velocity': self.velocity(readings),
                'distance': readings[-1]['distance']
            }
        return metrics
        
    
    def velocity(self, readings):
        # readings = self.get_readings()
        v = []
        for i in range(len(readings)-1):
            reading_prev = readings[i]
            reading_next = readings[i+1]
            delta_time = reading_next['time'] - reading_prev['time']
            accel_next = (reading_next['accel_x']**2 + reading_next['accel_y']**2) ** 1/2
            velocity_i = accel_next * delta_time
            v.append(velocity_i)
            reading_prev = reading_next
        v = np.array(v)
        velocity = v.mean()
        return velocity


    def get_readings(self):
        raw_readings = self.device_reader.protocol.get_cached_readings()
        parsed_readings = []
        for r in raw_readings:
            if len(r['data']) == 7:
                parsed_reading = {
                    'time': r['time'],
                    'distance': r['data'][0],
                    'yaw': r['data'][1],
                    'pitch': r['data'][2],
                    'roll': r['data'][3],
                    'accel_x': self._ms2_accel(r['data'][4]),
                    'accel_y': self._ms2_accel(r['data'][5]),
                    'accel_z': self._ms2_accel(r['data'][6]),
                }
                parsed_readings.append(parsed_reading)
        return parsed_readings


    def ready_to_measure(self):
        return self.ready #and self.serial.in_waiting > 0


    def _ms2_accel(self, acc, scale_factor=16384):
        '''converts raw acceleration units to m/s^2
        
            divide by 16384 to convert scaled g -> g (https://electronics.stackexchange.com/questions/39714/how-to-read-a-gyro-accelerometer)
            multiply by 9.80665 to convert g -> m/s^2
        '''
        return acc * 9.80665 / 16384


    def _buffer(self):
        if self.device_reader.protocol == None:
            raise Exception('protocol not established')
        # if self.serial.in_waiting == 0:
        #     raise Exception('no serial input')
        while not self.ready:
            if len(self.device_reader.protocol.get_cached_readings()) == 25:
                self.ready = True


if __name__ == '__main__':
    device = Device()
    if not DATA_LOG:
        time.sleep(2)
        while True:
            metrics = device.measure()
            if metrics:
                print(metrics)
            time.sleep(0.25)
    else:
        while True:
            pass