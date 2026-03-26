from adafruit_io.client import Client as AdafruitClient

ADAFRUIT_IO_KEY = "YOUR_AIO_KEY"
ADAFRUIT_IO_USERNAME = "YOUR_AIO_USERNAME"

aio_client = AdafruitClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)