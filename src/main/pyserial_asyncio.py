import asyncio
import serial_asyncio
import queue
import time


DEFAULT_DEVICE_PATH = '/dev/cu.usbmodem14101'
DEFAULT_SERIAL_RATE = 9600
VELOCITY_SAMPLE_SIZE = 5


class Output(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self._buffer_string = ''
        self._readings = queue.Queue(VELOCITY_SAMPLE_SIZE)
        print('==== Connection established')

    def data_received(self, data):
        # https://stackoverflow.com/questions/1093598/pyserial-how-to-read-the-last-line-sent-from-a-serial-device
        self._buffer_string += data.decode('utf-8')
        if '\n' in self._buffer_string:
            lines = self._buffer_string.split('\n')
            last_received = lines[-2]
            print(last_received)
            # self._store_reading(last_received)
            # self._buffer_string = lines[-1]
            # if self._readings.qsize() == VELOCITY_SAMPLE_SIZE:
            #     print('[{}] {}'.format(time.ctime(),self.get_velocity()))

    # def get_velocity(self):
    #     '''returns the instantaneous velocity of the device'''
    #     print('starting')
    #     v = []
    #     velocity_count = 0
    #     reading_prev = self._next_reading()
    #     while velocity_count < VELOCITY_SAMPLE_SIZE:
    #         reading_next = self._next_reading()
    #         print('prev: {}\tnext: {}'.format(reading_prev, reading_next))
    #         delta_time = reading_next['timestamp'] - reading_prev['timestamp']
    #         accel_next = (reading_next['accel_x']**2 + reading_next['accel_y']**2) ** 1/2
    #         velocity_i = accel_next * delta_time
    #         v.append(velocity_i)
    #         reading_prev = reading_next
    #         velocity_count += 1
    #     v = np.array(v)
    #     velocity = v.mean()
    #     return velocity

    def _store_reading(self, line):
        list_reading = line.replace('\r', '').replace('\n', '').split(',')
        if len(list_reading) == 7:
            list_reading = [float(i) for i in list_reading]
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
            self._readings.put(parsed_reading)
    
    def _threshold_value(self, value, lower_limit, upper_limit):
        r = value
        if value > upper_limit:
            r = upper_limit
        elif value < lower_limit:
            r = lower_limit
        return r

    def _next_reading(self):
        reading = self._readings.get()

        return reading

    def connection_lost(self, exc):
        print('port closed')
        self.transport.loop.stop()

    def pause_writing(self):
        print('pause writing')
        print(self.transport.get_write_buffer_size())

    def resume_writing(self):
        print(self.transport.get_write_buffer_size())
        print('resume writing')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = serial_asyncio.create_serial_connection(loop, Output, DEFAULT_DEVICE_PATH, baudrate=DEFAULT_SERIAL_RATE)
    t = time.time()
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
    print('time taken: {}s'.format(time.time() - t))