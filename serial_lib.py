"""
Classe para leitura e processamento de porta serial
Desenvolvido por: Adalberto Oliveira
Fainor - Curso de Engenharia de Computação
Processamento Digital de Sinais
Outubro de 2024
"""

import serial
import time
from threading import Thread, Lock

from loguru import logger

class SerialCommunication:

   def __init__(self, port="COM5", baud_rate=230400, 
                data_length=7, health_test=True, timeout=0.5):
      """
      Class constructor
      """

      

      # Loading serial parameters
      self.port = serial.Serial(port, baud_rate, timeout=timeout)      

      # Global variables
      self.data = None
      self.length = data_length
      self.health_test = health_test
      self.last_data = None
      self.data_lock = Lock()  # Add lock for thread safety

      # Check serial availabity
      is_serial_open = self.port.isOpen() 
      
      if is_serial_open:
         logger.success(f"Serial port successfully initialized. Serial is open: {is_serial_open}")
      
      else:
         logger.error(f"Unable to open serial port. Serial is open: {is_serial_open}")

      # self.start()

   def start(self):

      """
      This method starts serial thread and background reading process.

      Parameters:
      - None

      Returns:
      - Boolean result.
      """  

      logger.info("Starting thread...")

      # Starting serial reading
      try:
         serial_thread = Thread(target=self.read_serial,args=())
         serial_thread.daemon = True
         serial_thread.start()
         is_serial_thread_alive = serial_thread.is_alive()
         
         if is_serial_thread_alive:
            logger.success(f"Serial thread successfully started. Thread alive: {is_serial_thread_alive}")
            time.sleep(2)

            return True

         else:
            logger.error(f"Unable to start serial thread. Thread alive: {is_serial_thread_alive}")

            return False


      except Exception as serial_error:
         logger.error(f"Unable to start serial thread: {serial_error}")

         return False
   
   def read_serial(self):
      """
      This function reads the serial port and returns string data.

      Parameters:
      - None

      Returns:
      - data: serial data readed from serial port
      """

      while True:
         try:
            # Reading serial port
            line = self.port.readline().decode('utf-8').strip()
            if not line:  # Skip empty lines
               continue
                
            parts = line.split()
            if len(parts) < 2:  # Skip invalid lines
               continue
                
            # Check data sanity
            if parts[0] == "#!":
               try:
                  value = int(parts[1])  # Convert to integer since we know it's from analogRead
                  with self.data_lock:
                     self.data = [value]
               except ValueError:
                  logger.error(f"Invalid number format: {parts[1]}")
                  self.data = None
            else:
               self.data = None
         
         except Exception as error:
            logger.error(f"Unable to read serial data. Error: {error}")
            self.data = None
    
   def get_serial(self):
         try:
            # Reading serial port
            serial_data = self.port.readline()
            logger.info(serial_data)
            if False:
               # Check data sanity
               if serial_data[0] == "#!":
                  processed_data = [float(item) if '.' in item else int(item) for item in serial_data[1:]]
                  self.data = processed_data
               
               else:
                  logger.error("Invalid frame. Data rejected.")
                  self.data = False

               return self.data


         except Exception as error:
            logger.error(f"Unable to read serial data. Error: {error}")
            self.data = False

            return self.data

   def get_data(self):

      """
      This function unpacks the received data and delivers it to the to caller

      Parameters:
      - None

      Returns:
      - data: serial data received from serial port if data was ok
               False if serial data has unuseful.
      """       
      # print(f"From get data serial lib: {self.data}\
      #       \nold data: {self.last_data}")
      
      
      with self.data_lock:
         if self.data and len(self.data) == self.length:
            return self.data
         return None
      
   