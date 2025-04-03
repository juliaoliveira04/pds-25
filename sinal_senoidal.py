"""
Análise de Sinais Senoidais e Critério de Nyquist
Desenvolvido por: Adalberto Oliveira
Fainor - Curso de Engenharia de Computação
Processamento Digital de Sinais
Outubro de 2024
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from serial_lib import SerialCommunication
from processamento_lib import Processamento
from collections import deque
import time

# Configuração da comunicação serial
port = "/dev/cu.usbserial-140"
baud_rate = 9600

# Inicialização da comunicação serial
serial = SerialCommunication(port=port, 
                          baud_rate=baud_rate, 
                          data_length=1,
                          health_test=True, 
                          timeout=0.1)
serial.start()

# Inicialização do processamento
pds = Processamento(vin=12, tensao_base=4.94)

# Parâmetros de amostragem
fs = 1000  # Taxa de amostragem (Hz)
Ts = 1/fs  # Período de amostragem
f_nyquist = fs/2  # Frequência de Nyquist

# Armazenamento de dados
max_points = 1000  # Número de pontos para análise
times = deque(maxlen=max_points)
tensions = deque(maxlen=max_points)

# Inicialização com pontos iniciais
start_time = time.time()
for i in range(10):
    times.append(start_time + i)
    tensions.append(2.5)

# Criação da figura com subplots
plt.style.use('default')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
fig.suptitle('Análise de Sinais Senoidais', fontsize=14)

# Configuração do gráfico no domínio do tempo
line, = ax1.plot([], [], 'b-', label='Sinal', linewidth=2)
ax1.set_title('Domínio do Tempo', fontsize=12)
ax1.set_xlabel('Tempo (s)', fontsize=10)
ax1.set_ylabel('Tensão (V)', fontsize=10)
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.legend(fontsize=10)

# Configuração do gráfico no domínio da frequência
line_fft, = ax2.plot([], [], 'r-', label='FFT', linewidth=2)
ax2.set_title('Domínio da Frequência', fontsize=12)
ax2.set_xlabel('Frequência (Hz)', fontsize=10)
ax2.set_ylabel('Magnitude', fontsize=10)
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.legend(fontsize=10)

# Texto para informações
info_text = ax1.text(0.02, 0.98, '', transform=ax1.transAxes, 
                    verticalalignment='top', fontsize=10,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Limites dos eixos
ax1.set_ylim(0, 5)
ax1.set_xlim(start_time, start_time + 10)
ax2.set_xlim(0, fs)
ax2.set_ylim(0, 1000)  # Valor inicial para magnitude

def calculate_fft(signal):
    """Calcula a FFT do sinal"""
    fft = np.fft.fft(signal)
    magnitude = np.abs(fft)
    freqs = np.fft.fftfreq(len(signal), Ts)
    return freqs[:len(freqs)//2], magnitude[:len(magnitude)//2]

def update(frame):
    current_time = time.time()
    
    # Leitura dos dados seriais
    serial_data = serial.get_data()
    
    if serial_data is not None:
        valor = serial_data[0]
        tensao = pds.tensao(valor)
        
        # Atualização dos dados
        times.append(current_time)
        tensions.append(tensao)
        
        # Atualização do gráfico no domínio do tempo
        line.set_data(list(times), list(tensions))
        
        # Cálculo e atualização da FFT
        if len(tensions) > 100:  # Só calcula FFT com dados suficientes
            try:
                freqs, magnitude = calculate_fft(list(tensions))
                line_fft.set_data(freqs, magnitude)
                
                # Encontra a frequência dominante
                dominant_freq_idx = np.argmax(magnitude)
                dominant_freq = freqs[dominant_freq_idx]
                
                # Atualiza informações
                info_text.set_text(f'Frequência de Nyquist: {f_nyquist:.1f} Hz\n'
                                 f'Frequência Dominante: {dominant_freq:.1f} Hz\n'
                                 f'Tensão Atual: {tensao:.2f}V')
                
                # Ajuste do eixo de frequência
                ax2.set_ylim(0, max(magnitude) * 1.1)
            except Exception as e:
                print(f"Erro no cálculo da FFT: {e}")
        
        # Ajuste dos limites dos eixos do tempo
        if len(times) > 0:
            ax1.set_xlim(max(0, times[-1] - 10), times[-1])
            y_min = min(tensions) * 0.95
            y_max = max(tensions) * 1.05
            ax1.set_ylim(y_min, y_max)
    
    return line, line_fft, info_text

# Criação da animação com número máximo de frames
ani = FuncAnimation(fig, update, interval=20, blit=True, cache_frame_data=False)

# Ajuste do layout
plt.tight_layout()

# Mostra o gráfico
plt.show() 