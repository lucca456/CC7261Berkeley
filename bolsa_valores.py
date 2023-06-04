import time
import logging
import random
import threading
import requests
from flask import Flask, request, jsonify
import sys

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

class BolsaDeValores:
    def __init__(self):
        self.relogio = time.time()
        self.acoes = {
            "A1": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "A2": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "A3": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "A4": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "A5": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "A6": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "A7": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "A8": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0}
        }
        threading.Thread(target=self.start_consuming).start()

    def start_consuming(self):
        logger.info(AMARELO + f'[...] BV aguardando mensagens...' + RESET)
        while True:
            time.sleep(10)
            self.atualizar_relogio()

    def enviar_acoes(self, hb_id):
        logger.info(MAGENTA + f'[*] Lista de ações enviada da BV ao {hb_id}' + RESET)
        try:
            response = requests.post(f'http://{hb_id}/acoes', json=self.acoes)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.info(VERMELHO + f'[!] Falha ao enviar ações para {hb_id}: {e}' + RESET)

    @app.route('/pedido', methods=['POST'])
    def handle_message(self):
        try:
            pedido = request.get_json()
            if "Sincronizar" in pedido:
                label, tempo_hb, hb_id = pedido.split(',')
                self.sincronizar_relogio(tempo_hb, hb_id)
            elif "Lista" in pedido:
                label, hb_id = pedido.split(',')
                self.enviar_acoes(hb_id)
            elif pedido:
                nome_acao, operacao, quantidade, relogio_hb, hb_id = pedido.split(',')
                quantidade = int(quantidade)
                relogio_hb = float(relogio_hb)
                hb_id = str(hb_id)
                if relogio_hb > self.relogio + 2 or relogio_hb < self.relogio - 2:
                    logger.info(CIANO + f'[#] Sincronizar enviado da BV ao {hb_id} .' + RESET)
                    try:
                        response = requests.post(f'http://{hb_id}/sincronizar', json={'tempo': self.relogio})
                        response.raise_for_status()
                    except requests.exceptions.RequestException as e:
                        logger.info(VERMELHO + f'[!] Falha ao enviar sincronização para {hb_id}: {e}' + RESET)
                self.processar_pedido(nome_acao, operacao, quantidade, hb_id)
        except Exception as e:
            logger.info(VERMELHO + f'[!] Erro em \'handle_message\' no BV: {e}' + RESET)
            return jsonify({'status': 'error', 'message': f'Erro em \'handle_message\' no BV: {e}'}), 400

    def processar_pedido(self, nome_acao, operacao, quantidade, hb_id):
        try:
            if nome_acao not in self.acoes:
                return logger.info(VERMELHO + f'[$] A ação {nome_acao} não existe !' + RESET)
            if operacao not in ['compra', 'venda']:
                return logger.info(VERMELHO + f'[$] A operação {operacao} é inválida. As operações válidas são \'compra\' e \'venda\' !' + RESET)
            acao = self.acoes[nome_acao]
            if operacao == 'compra':
                if quantidade > acao['quantidade']:
                    return logger.info(VERMELHO + f"[$] A quantidade a ser comprada {quantidade} é maior do que a quantidade disponível {acao['quantidade']} para {nome_acao} !" + RESET)
                acao['quantidade'] -= quantidade
                acao['disponivel_para_venda'] += quantidade
                acao['valor'] = round(acao['valor'] * 1.01, 2)
            elif operacao == 'venda':
                if quantidade > acao['disponivel_para_venda']:
                    return logger.info(VERMELHO + f"[$] A quantidade a ser vendida {quantidade} é maior do que a quantidade disponível para venda {acao['disponivel_para_venda']} para {nome_acao} !" + RESET)
                acao['disponivel_para_venda'] -= quantidade
                acao['quantidade'] += quantidade
                acao['valor'] = round(acao['valor'] * 0.99, 2)
            logger.info(VERDE + f"[#] Pedido de {operacao} de {quantidade} ações de {nome_acao} processado com sucesso !" + RESET)
        except Exception as e:
            logger.info(VERMELHO + f'[!] Erro em \'processar_pedido\' no BV: {e}' + RESET)

    def sincronizar_relogio(self, tempo_hb, hb_id):
        try:
            logger.info(CIANO + f'[#] Sincronização recebida da {hb_id} .' + RESET)
            self.relogio = (self.relogio + float(tempo_hb)) / 2
            logger.info(CIANO + f'[#] Sincronização efetuada com sucesso com o {hb_id} .' + RESET)
        except Exception as e:
            logger.info(VERMELHO + f'[!] Erro em \'sincronizar_relogio\' no BV: {e}' + RESET)

    def atualizar_relogio(self):
        try:
            self.relogio = time.time()
            logger.info(VERDE + f"[#] Relógio da BV atualizado para: {self.relogio}" + RESET)
        except Exception as e:
            logger.info(VERMELHO + f'[!] Erro em \'atualizar_relogio\' no BV: {e}' + RESET)

    def start_consuming(self):
        logger.info(AMARELO + f'[...] BV aguardando mensagens...' + RESET)
        while True:
            time.sleep(10)
            self.atualizar_relogio()

    def enviar_acoes(self, hb_id):
        logger.info(MAGENTA + f'[*] Lista de ações enviada da BV ao {hb_id}' + RESET)
        try:
            response = requests.post(f'http://{hb_id}/acoes', json=self.acoes)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.info(VERMELHO + f'[!] Falha ao enviar ações para {hb_id}: {e}' + RESET)

if __name__ == '__main__':
    BolsaDeValores()
    app.run(port=5001)

