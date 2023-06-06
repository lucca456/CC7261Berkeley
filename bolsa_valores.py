import time
import logging
import random
import threading
from flask import Flask, request, jsonify
import sys
import requests

# Cores
VERDE = '\033[32m'
VERMELHO = '\033[31m'
AMARELO = '\033[33m'
MAGENTA = '\033[35m'
CIANO = '\033[36m'
RESET = '\033[0m'

logging.basicConfig(filename='log_bv.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

app = Flask(__name__)

class BolsaDeValores:
    def __init__(self):
        self.relogio = time.time()
        self.acoes = {
            "A1": {'quantidade': 10, 'valor': 10},
            "A2": {'quantidade': 10, 'valor': 10},
            "A3": {'quantidade': 10, 'valor': 10},
            "A4": {'quantidade': 10, 'valor': 10},
            "A5": {'quantidade': 10, 'valor': 10},
            "A6": {'quantidade': 10, 'valor': 10},
            "A7": {'quantidade': 10, 'valor': 10},
            "A8": {'quantidade': 10, 'valor': 10}
        }

    def sincronizar_relogio(self):
        logging.info('Início da sincronização')
        hora_antes = time.time()

        # Obter a hora dos sistemas de HB
        hora_hb1 = self.obter_hora_hb('localhost:8080')
        hora_hb2 = self.obter_hora_hb('localhost:8081')

        # Sincronizar os relógios
        self.relogio = (hora_hb1 + hora_hb2 + hora_antes) / 3

        hora_depois = time.time()

        logging.info(f'Hora antes da sincronização: {hora_antes}')
        logging.info(f'Hora depois da sincronização: {hora_depois}')
        
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

bolsa = BolsaDeValores()

@app.route('/comprar', methods=['POST'])
def comprar_acoes():
    requisicao = request.get_json()
    acao = requisicao.get('acao')
    quantidade = requisicao.get('quantidade')

    tempo_pedido = time.time()
    logging.info(f'Hora do pedido: {tempo_pedido}')

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
    logging.info(f'Hora do pedido: {tempo_pedido}')

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
