import time
import random
import logging
import sys
import threading
import requests

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
handler = logger.handlers[0]
handler.setFormatter(formatter)

class Robo:
    def __init__(self, hb_url='http://localhost:8080'):
        self.hb_url = hb_url

    def tomar_decisao_compra_venda(self):
        try:
            acoes = self.get_acoes_disponiveis()
            if acoes:
                acao = random.choice(acoes)
                quantidade = random.randint(1, acoes[acao]['quantidade'])
                if random.choice([True, False]):  # Decisão aleatória de comprar ou vender
                    self.realizar_compra(acao, quantidade)
                else:
                    self.realizar_venda(acao, quantidade)
        except Exception as e:
            logger.error(f"Erro ao tomar decisão de compra/venda: {e}")

    def get_acoes_disponiveis(self):
        try:
            response = requests.get(f"{self.hb_url}/acoes")
            response.raise_for_status()
            acoes = response.json()
            return acoes
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter a lista de ações disponíveis: {e}")
            return {}

    def realizar_compra(self, acao, quantidade):
        try:
            data = {'acao': acao, 'quantidade': quantidade}
            response = requests.post(f"{self.hb_url}/comprar", json=data)
            response.raise_for_status()
            mensagem = response.json()['mensagem']
            logger.info(mensagem)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao realizar compra de ação: {e}")

    def realizar_venda(self, acao, quantidade):
        try:
            data = {'acao': acao, 'quantidade': quantidade}
            response = requests.post(f"{self.hb_url}/vender", json=data)
            response.raise_for_status()
            mensagem = response.json()['mensagem']
            logger.info(mensagem)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao realizar venda de ação: {e}")

if __name__ == "__main__":
    robo = Robo()

    while True:
        try:
            robo.tomar_decisao_compra_venda()
            time.sleep(1)  # Aguardar 1 segundo entre cada operação
        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuário")
            break
