import serial
import sys
import time
import numpy as np


DEFAULT_DEVICE_PATH = '/dev/cu.usbmodem14101'
DEFAULT_SERIAL_RATE = 9600
N_SAMPLES = 5
CHANGE_THRESHOLD = 13000


class Device:
    '''simple API for our motion sensing device'''
    
    def __init__(self, device_path=DEFAULT_DEVICE_PATH, serial_rate=DEFAULT_SERIAL_RATE):
        self._device = serial.Serial(device_path, serial_rate, timeout=1)
        self._last_good_reading = None
        self._buffer()


    def terminate(self):
        self._device.close()


    def get_velocity(self):
        '''returns the instantaneous velocity of the device'''
        v = []
        samples_collected = 0
        reading_prev = self._parsed_read()
        while samples_collected < N_SAMPLES:
            reading_next = self._parsed_read()
            delta_time = reading_next['timestamp'] - reading_prev['timestamp']
            accel_next = (reading_next['accel_x']**2 + reading_next['accel_y']**2) ** 1/2
            velocity_i = accel_next * delta_time
            v.append(velocity_i)
            reading_prev = reading_next
            samples_collected += 1
        v = np.array(v)
        velocity = v.mean()
        return velocity

    
    def get_accel(self):
        reading = self._parsed_read()
        return reading['accel_x'], reading['accel_y']


    def _buffer(self):
        for i in range(5):
            self._raw_read()


    def _parsed_read(self):
        list_reading = self._list_read()
        parsed_reading = {
            'timestamp': time.time(),
            'distance': list_reading[0],
            'gyro_x': list_reading[1],
            'gyro_y': list_reading[2],
            'gyro_z': list_reading[3],
            'accel_x': self._threshold_value(list_reading[4], -13000, 13000),
            'accel_y': self._threshold_value(list_reading[5], -13000, 13000),
            'accel_z': list_reading[6]
        }
        return parsed_reading


    def _threshold_value(self, value, lower_limit, upper_limit):
        r = value
        if value > upper_limit:
            r = upper_limit
        elif value < lower_limit:
            r = lower_limit
        return r


    def _list_read(self):
        raw_reading = self._raw_read()
        list_reading = raw_reading.replace('\r', '').replace('\n', '').split(',')
        bad_read = True
        while bad_read:
            raw_reading = self._raw_read()
            list_reading = raw_reading.replace('\r', '').replace('\n', '').split(',')
            if len(list_reading) == 7:
                list_reading = [float(i) for i in list_reading]
                if self._last_good_reading == None:
                    bad_read = False
                else:
                    bad_read = self._is_outlier(list_reading)
            if bad_read:
                print('discarded reading: {}'.format(raw_reading))
        self._last_good_reading = list_reading
        return list_reading

    
    def _is_outlier(self, list_reading):
        is_outlier = False
        accel_x = list_reading[4]
        accel_y = list_reading[5]
        last_good_accel_x = self._last_good_reading[4]
        last_good_accel_y = self._last_good_reading[5]
        if abs(last_good_accel_x - accel_x) > CHANGE_THRESHOLD or abs(last_good_accel_y - accel_y) > CHANGE_THRESHOLD:
            is_outlier = True
            print('outlier reading: {}\nprev reading: {}'.format(list_reading, self._last_good_reading))
        return is_outlier


    def _raw_read(self):
        raw_reading = self._device.readline().decode('utf-8')
        self._device.flush()
        return raw_reading
    

if __name__ == '__main__':
    # initialize device connection
    device = Device()
    print(device._parsed_read())

    # device.terminate()
