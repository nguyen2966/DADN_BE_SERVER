from Adafruit_IO.client import Client as AdafruitClient
import os
from dotenv import load_dotenv

load_dotenv()  

ADAFRUIT_AIO_USERNAME = os.getenv("ADAFRUIT_AIO_USERNAME")
ADAFRUIT_AIO_KEY = os.getenv("ADAFRUIT_AIO_KEY")


aio_client = AdafruitClient(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)

