import threading
import time


class ThreadingExample(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval
        self._val = 0
        self._checkpoint = 0
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread                                 # Start the execution

    def run(self):
        """ Method that runs forever """
        while True:
            # Do something
            self._val += 1
            print(self._val)
            time.sleep(self.interval)

    def checkpoint(self):
        self._checkpoint = self._val

    def get_checkpoint(self):
        return self._checkpoint

example = ThreadingExample()
time.sleep(3)
print('Checkpoint')
example.checkpoint()
time.sleep(2)
print('====Checkpointed val: {}'.format(example.get_checkpoint()))

