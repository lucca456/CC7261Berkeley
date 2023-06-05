from flask import Flask, jsonify, request
import requests
import time
import sys
import logging
import random
import threading

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

app = Flask(__name__)

class HomeBroker:
    def __init__(self, host='localhost:5001', hb_id=0):
        self.host = host
        self.hb_id = hb_id
        self.robo_id = 'robo1'
        self.acoes = {}
        self.relogio = time.time()
        threading.Thread(target=self.start_consuming).start()

    def start_consuming(self):
        while True:
            try:
                logger.info(AMARELO + f'[...] HB{self.hb_id} aguardando mensagens...' + RESET)
                response = requests.get(f'http://{self.host}/hb{self.hb_id}')
                response.raise_for_status()
                self.handle_message(response.text)
            except Exception as e:
                logger.info(VERMELHO + f'[!] Erro em \'start_consuming\' no HB{self.hb_id}: {e}' + RESET)
                time.sleep(5)  # tente novamente após um atraso

    def solicita_lista(self):
        logger.info(MAGENTA + f'[*] HB{self.hb_id} solicitando lista de ações a BV...' + RESET)
        pedido_bv = f"Lista,hb{self.hb_id}"
        requests.post(f'http://{self.host}/exchange_bv/bv', data=pedido_bv)

    def repassa_lista(self):
        lista_acoes = f"Lista;{self.acoes};hb{self.hb_id}"
        requests.post(f'http://{self.host}/exchange_robos/{self.robo_id}', data=lista_acoes)
        logger.info(MAGENTA + f'[*] Lista de ações enviada pelo HB{self.hb_id} ao {self.robo_id} !' + RESET)

    def handle_message(self, message):
        try:
            pedido = message
            if "Lista" in pedido:
                logger.info(MAGENTA + f'[*] Lista de ações recebida da BV no HB{self.hb_id} !' + RESET)
                label, acoes = pedido.split(';')
                self.acoes = eval(acoes)
                self.repassa_lista()
            elif "LRobo" in pedido:
                label, robo_id = pedido.split(',')
                logger.info(MAGENTA + f'[*] {robo_id} solicitou a lista de ações .' + RESET)
                self.robo_id = robo_id
                self.solicita_lista()
            elif "Sincronizar" in pedido:
                logger.info(CIANO + '[#] Iniciando sincronização com a BV...' + RESET)
                label, tempo_bv = pedido.split(',')
                self.sincronizar_relogio(tempo_bv)
            elif pedido:
                nome_acao, operacao, quantidade, robo_id = pedido.split(',')
                quantidade = int(quantidade)
                self.realiza_operacao(nome_acao, operacao, quantidade, robo_id)
        except Exception as e:
            logger.info(VERMELHO + f'[!] Erro em \'handle_message\' no HB{self.hb_id}: {e}' + RESET)

    def realiza_operacao(self, nome_acao, operacao, quantidade, robo_id):
        if operacao == 'Venda':
            self.vende_acao(nome_acao, quantidade, robo_id)
        elif operacao == 'Compra':
            self.compra_acao(nome_acao, quantidade, robo_id)

    def compra_acao(self, nome_acao, quantidade, robo_id):
        logger.info(CIANO + f'[#] {robo_id} solicitando a compra de {quantidade} ações de {nome_acao}...' + RESET)
        pedido_bv = f"Compra,{nome_acao},{quantidade},hb{self.hb_id}"
        requests.post(f'http://{self.host}/exchange_bv/bv', data=pedido_bv)

    def vende_acao(self, nome_acao, quantidade, robo_id):
        logger.info(CIANO + f'[#] {robo_id} solicitando a venda de {quantidade} ações de {nome_acao}...' + RESET)
        pedido_bv = f"Venda,{nome_acao},{quantidade},hb{self.hb_id}"
        requests.post(f'http://{self.host}/exchange_bv/bv', data=pedido_bv)

    def sincronizar_relogio(self, tempo_bv):
        self.relogio = time.time() - float(tempo_bv)
        logger.info(CIANO + f'[#] Relógio sincronizado com a BV!' + RESET)

hb1 = HomeBroker(hb_id=1)
hb2 = HomeBroker(hb_id=2)

@app.route('/hb1', methods=['POST'])
def hb1_route():
    hb1.handle_message(request.data.decode())
    return 'OK', 200

@app.route('/hb2', methods=['POST'])
def hb2_route():
    hb2.handle_message(request.data.decode())
    return 'OK', 200

if __name__ == "__main__":
    app.run(host='localhost', port=5001)
