import numpy as np


class Processamento:


    def __init__(self, delta=0.00488,vin=12,tensao_base=5):
        
        self.delta = delta
        self.vin = vin
        self.tensao_base = tensao_base

    def tensao(self,valor):

        self.amostra = valor*self.delta

        tensao_saida = (self.amostra*self.vin)/self.tensao_base

        return tensao_saida



