import time
import random
import logging
import sys
import threading
import requests

# Cores
VERDE = '\033[32m'
VERMELHO = '\033[31m'
AMARELO = '\033[33m'
MAGENTA = '\033[35m'
CIANO = '\033[36m'
RESET = '\033[0m'

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
handler = logger.handlers[0]
handler.setFormatter(formatter)

class Robo:
    def __init__(self, hb_id='1', robo_id='1', host='localhost'):
        self.hb_id = hb_id
        self.robo_id = robo_id
        self.acoes = {}
        self.acoes_possuidas = {}
        self.recebeu_acoes = False
        self.conectado = False
        self.relogio = time.time()
        self.host = host
        time.sleep(5)
        self.solicita_lista()
        threading.Thread(target=self.realizar_operacao).start()

    def solicita_lista(self):
        logger.info(MAGENTA + f'Robo{self.robo_id} solicitando lista de ações ao HB{self.hb_id}...' + RESET)
        pedido_bv = f"LRobo,robo{self.robo_id}"
        requests.post(f'http://{self.host}/hb{self.hb_id}', data=pedido_bv)

    def handle_message(self, body):
        try:
            pedido = body.decode('utf-8')
            if "Lista" in pedido:
                logger.info(MAGENTA + f'Lista de ações recebida no Robo{self.robo_id} !' + RESET)
                label, acoes, hb_id = pedido.split(';')
                self.acoes = eval(acoes)
                logger.info(MAGENTA + f'Ações recebidas de {hb_id}: ' + RESET)
                for acao, info in self.acoes.items():
                    logger.info(MAGENTA + f'{acao}: {info}'+ RESET)
                self.recebeu_acoes = True
        except Exception as e:
            logger.info(VERMELHO + f'Erro em \'handle_message\' no Robo{self.robo_id}: {e}' + RESET)

    def realizar_operacao(self):
        try:
            while True:
                time.sleep(5)
                if self.recebeu_acoes == True:
                    if len(self.acoes) > 0:
                        nome_acao = random.choice(list(self.acoes.keys()))
                        operacao = random.choice(['compra', 'venda'])
                        quantidade_maxima_para_compra = self.acoes[nome_acao]['quantidade']
                        quantidade_maxima_para_venda = self.acoes_possuidas.get(nome_acao, 0)
                        if operacao == 'compra' and quantidade_maxima_para_compra > 0:
                            quantidade = random.randint(1, quantidade_maxima_para_compra)
                            self.acoes_possuidas[nome_acao] = self.acoes_possuidas.get(nome_acao, 0) + quantidade
                        elif operacao == 'venda' and quantidade_maxima_para_venda > 0:
                            quantidade = random.randint(1, quantidade_maxima_para_venda)
                            self.acoes_possuidas[nome_acao] -= quantidade
                        else:
                            continue
                        pedido = f"{nome_acao},{operacao},{quantidade},robo{self.robo_id}"
                        requests.post(f'http://{self.host}/hb{self.hb_id}', data=pedido)
                        logger.info(VERDE + f"Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao HB{self.hb_id} com sucesso !" + RESET)
                        self.solicita_lista()
        except Exception as e:
            logger.info(VERMELHO + f'Erro em \'realizar_operacao\' no Robo{self.robo_id}: {e}' + RESET)
        

if __name__ == "__main__":
    hb_id = sys.argv[1] if len(sys.argv) > 1 else '1'
    robo_id = sys.argv[2] if len(sys.argv) > 2 else '1'
    robo = Robo(hb_id=hb_id, robo_id=robo_id)

