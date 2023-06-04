import random
import time
from home_broker import *
class Robo:
    def init(self, home_broker):
        self.home_broker = home_broker
        self.intervalo = 10  # Intervalo entre as operações em segundos

    def operar(self):
        while True:
            try:
                # Sincronizar relógio
                self.home_broker.sincronizar_relogio()

                # Obter a lista de ações
                acoes = self.home_broker.obter_acoes()
                if acoes is not None:
                    # Escolher uma ação aleatória
                    acao = random.choice(list(acoes.keys()))

                    # Decidir se vai comprar ou vender
                    if random.choice(['compra', 'venda']) == 'compra':
                        # Comprar uma quantidade aleatória da ação
                        quantidade = random.randint(1, 10)
                        self.home_broker.comprar_acao(acao, quantidade)
                    else:
                        # Vender uma quantidade aleatória da ação
                        quantidade = random.randint(1, 10)
                        self.home_broker.vender_acao(acao, quantidade)

                # Esperar um intervalo antes da próxima operação
                time.sleep(self.intervalo)

            except Exception as e:
                print(f"Erro ao operar: {e}")
                
if __name__ == "_main_":
    robo = Robo()
    robo.operar()