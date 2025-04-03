"""
Real-time tension variation graph
Desenvolvido por: Adalberto Oliveira
Fainor - Curso de Engenharia de Computação
Processamento Digital de Sinais
Outubro de 2024
"""

import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from serial_lib import SerialCommunication
from processamento_lib import Processamento
from collections import deque

# Serial configuration
port = "/dev/cu.usbserial-140"
baud_rate = 9600

# Initialize serial communication
serial = SerialCommunication(port=port, 
                          baud_rate=baud_rate, 
                          data_length=1,
                          health_test=True, 
                          timeout=0.1)
serial.start()

# Initialize processing
pds = Processamento(vin=12, tensao_base=4.94)

# Data storage
max_points = 200  # Increased number of points for smoother line
times = deque(maxlen=max_points)
tensions = deque(maxlen=max_points)

# Initialize with some data points
start_time = time.time()
for i in range(10):
    times.append(start_time + i)
    tensions.append(2.5)  # Initial value

# Create the figure and axis
plt.style.use('default')  # Use default style
fig, ax = plt.subplots(figsize=(12, 6))
line, = ax.plot(list(times), list(tensions), 'b-', label='Tensão', linewidth=2)
ax.set_title('Variação de Tensão em Tempo Real', fontsize=12, pad=15)
ax.set_xlabel('Tempo (s)', fontsize=10)
ax.set_ylabel('Tensão (V)', fontsize=10)
ax.grid(True, linestyle='--', alpha=0.7)
ax.legend(fontsize=10)

# Add text for current value
value_text = ax.text(0.02, 0.98, '', transform=ax.transAxes, 
                    verticalalignment='top', fontsize=12,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Set the axis limits
ax.set_ylim(0, 5)  # Adjust based on your expected voltage range
ax.set_xlim(start_time, start_time + 10)  # Show last 10 seconds

def update(frame):
    # Get current time
    current_time = time.time()
    
    # Read serial data
    serial_data = serial.get_data()
    
    if serial_data is not None:
        valor = serial_data[0]
        tensao = pds.tensao(valor)
        
        # Update data
        times.append(current_time)
        tensions.append(tensao)
        
        # Update the line data
        line.set_data(list(times), list(tensions))
        
        # Update the current value text
        value_text.set_text(f'Tensão Atual: {tensao:.2f}V')
        
        # Adjust x-axis limits to show the last 10 seconds
        if len(times) > 0:
            ax.set_xlim(max(0, times[-1] - 10), times[-1])
            
            # Auto-adjust y-axis limits with some padding
            y_min = min(tensions) * 0.95
            y_max = max(tensions) * 1.05
            ax.set_ylim(y_min, y_max)
    
    return line, value_text

# Create animation with faster update rate
ani = FuncAnimation(fig, update, interval=20, blit=True)  # Update every 20ms

# Adjust layout to prevent text cutoff
plt.tight_layout()

# Show the plot
plt.show() 