import time
import logging
import threading
from flask import Flask, request, jsonify
import sys
import requests
import random


logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
handler = logger.handlers[0]
handler.setFormatter(formatter)

app = Flask(__name__)

class BolsaDeValores:
    def __init__(self):
        self.relogio = time.time()
        self.acoes = {
            "A1": {'quantidade': 100, 'valor': 10},
            "A2": {'quantidade': 100, 'valor': 10},
            "A3": {'quantidade': 100, 'valor': 10},
            "A4": {'quantidade': 100, 'valor': 10},
            "A5": {'quantidade': 100, 'valor': 10},
            "A6": {'quantidade': 100, 'valor': 10},
            "A7": {'quantidade': 100, 'valor': 10},
            "A8": {'quantidade': 100, 'valor': 10}
        }
        self.thread_relogio = threading.Thread(target=self.atualizar_relogio_continuamente)
        self.thread_relogio.start()

        self.hb_urls = ['localhost:8080']

    def sincronizar_relogio(self):
        logger.info('Início da sincronização')
        hora_antes = time.time()

        # Obter a hora dos sistemas de HB
        horas_hb = [self.obter_hora_hb(url) for url in self.hb_urls]

        # Sincronizar os relógios
        self.relogio = sum(horas_hb + [hora_antes]) / (len(horas_hb) + 1)

        # Atualizar a hora nos sistemas HB
        for url in self.hb_urls:
            self.atualizar_hora_hb(url)

        hora_depois = time.time()

        logger.info(f'Hora antes da sincronização: {hora_antes}')
        logger.info(f'Hora depois da sincronização: {hora_depois}')

    def obter_hora_hb(self, hb_url):
        try:
            response = requests.get(f"http://{hb_url}/hora")
            response.raise_for_status()
            hora_hb = response.json()['hora']
            return hora_hb
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter a hora do HB: {e}")
            return 0

    def atualizar_hora_hb(self, hb_url):
        try:
            data = {'hora': self.relogio}
            response = requests.post(f"http://{hb_url}/hora", json=data)
            response.raise_for_status()
            logger.info(f"Hora atualizada no HB: {self.relogio}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao atualizar a hora do HB: {e}")

    def atualizar_relogio(self):
        ajuste = random.uniform(-2, 2)  # Gera um número aleatório entre -2 e 2
        self.relogio += ajuste
        logger.info(f"Relógio atualizado. Ajuste: {ajuste} - Relógio BV: {self.relogio}")
    
    def atualizar_relogio_continuamente(self):
        while True:
            self.atualizar_relogio()
            time.sleep(10)  # Aguardar 10 segundos antes de atualizar novamente

bolsa = BolsaDeValores()

@app.route('/comprar', methods=['POST'])
def comprar_acoes():
    requisicao = request.get_json()
    acao = requisicao.get('acao')
    quantidade = requisicao.get('quantidade')

    tempo_pedido = time.time()
    logger.info(f'Hora do pedido: {tempo_pedido}')

    diferenca_tempo = tempo_pedido - bolsa.relogio

    if diferenca_tempo > 1:
        bolsa.sincronizar_relogio()

    if acao in bolsa.acoes and bolsa.acoes[acao]['quantidade'] >= quantidade:
        bolsa.acoes[acao]['quantidade'] -= quantidade
        bolsa.acoes[acao]['valor'] += quantidade * 0.1
        return jsonify({
            'ação' : f'{acao}',
            'quantidade' : f'{quantidade}',
            'tempo' : f'{tempo_pedido}',
            'mensagem': 'Compra efetuada com sucesso.'
            })
    else:
        return jsonify({'mensagem': 'Falha na compra. Quantidade insuficiente.'})

@app.route('/vender', methods=['POST'])
def vender_acoes():
    requisicao = request.get_json()
    acao = requisicao.get('acao')
    quantidade = requisicao.get('quantidade')

    tempo_pedido = time.time()
    logger.info(f'Hora do pedido: {tempo_pedido}')

    diferenca_tempo = tempo_pedido - bolsa.relogio

    if diferenca_tempo > 1:
        bolsa.sincronizar_relogio()

    if acao in bolsa.acoes:
        bolsa.acoes[acao]['quantidade'] += quantidade
        bolsa.acoes[acao]['valor'] -= quantidade * 0.1
        return jsonify({
            'acao' : f'{acao}',
            'quantidade' : f"{bolsa.acoes[acao]['quantidade']}",
            'tempo' : f'{tempo_pedido}',
            'mensagem': 'Compra efetuada com sucesso.'
            })
    else:
        return jsonify({'mensagem': 'Falha na venda. Ação não encontrada.'})

@app.route('/acoes', methods=['GET'])
def listar_acoes():
    return jsonify(bolsa.acoes)

if __name__ == '__main__':
    app.run(port=5001)
