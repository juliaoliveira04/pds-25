"""
Exemplo de uso da classe serial_lib.py
Desenvolvido por: Adalberto Oliveira
Fainor - Curso de Engenharia de Computação
Processamento Digital de Sinais
Outubro de 2024
"""

import time
from serial_lib import SerialCommunication
from processamento_lib import Processamento

# Defining serial port info
port = "/dev/cu.usbserial-140"
baud_rate = 9600

serial = SerialCommunication(port=port, 
                          baud_rate=baud_rate, 
                          data_length=1,  # We expect 1 value after the #! prefix
                          health_test=True, 
                          timeout=0.1)  # Reduced timeout for faster response
serial.start()
pds = Processamento(vin=12, tensao_base=4.94)

while True:
    # Reading serial port without delay
    serial_data = serial.get_data()
    
    if serial_data is not None:  # Changed from if serial_data to be more explicit
        valor = serial_data[0]  # Get the first (and only) value
        tensao = pds.tensao(valor)
        print(f"Amostra: {round(pds.amostra,2)} Tensao: {round(tensao,2)}")
