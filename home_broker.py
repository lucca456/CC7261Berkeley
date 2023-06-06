from flask import Flask, jsonify, request
import requests
import time
import sys
import logging
import threading


logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
handler = logger.handlers[0]
handler.setFormatter(formatter)

app = Flask(__name__)

class HomeBroker:
    def __init__(self, host='localhost:8080', bv_host='localhost:5001', hb_id=0):
        self.host = host
        self.bv_host = bv_host
        self.hb_id = hb_id
        self.robo_id = 'robo1'
        self.acoes = {}
        self.relogio = time.time()
        self.tempo_pedido = 0  # variável para armazenar o tempo de processamento do pedido

    def obter_hora_atual(self):
        self.relogio = time.time()

    def atualizar_hora(self, nova_hora):
        self.relogio = nova_hora
        self.tempo_pedido = nova_hora  # atualizar o tempo do pedido com a nova hora

    def get_acoes(self):
        try:
            response = requests.get(f"http://{self.bv_host}/acoes")
            response.raise_for_status()
            self.acoes = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter a lista de ações: {e}")

    def comprar_acao(self, acao, quantidade):
        try:
            data = {'acao': acao, 'quantidade': quantidade}
            response = requests.post(f"http://{self.bv_host}/comprar", json=data)
            response.raise_for_status()
            mensagem = response.json()
            logger.info(mensagem)
            # Registrar o resultado da operação no log
            logger.info(f"Compra realizada - Ação: {acao} - Quantidade: {quantidade}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao realizar compra de ação: {e}")
        return mensagem

    def vender_acao(self, acao, quantidade):
        try:
            data = {'acao': acao, 'quantidade': quantidade}
            response = requests.post(f"http://{self.bv_host}/vender", json=data)
            response.raise_for_status()
            mensagem = response.json()['mensagem']
            logger.info(mensagem)
            # Registrar o resultado da operação no log
            logger.info(f"Venda realizada - Ação: {acao} - Quantidade: {quantidade}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao realizar venda de ação: {e}")

    def analisar_pedido(self, pedido):
        acao = pedido.get('acao')
        quantidade = pedido.get('quantidade')
        if pedido.get('tipo') == 'compra':
            self.comprar_acao(acao, quantidade)
        elif pedido.get('tipo') == 'venda':
            self.vender_acao(acao, quantidade)
        else:
            logger.error(f"Tipo de pedido inválido: {pedido}")

    def sincronizar_relogio(self):
        try:
            response = requests.post(f"http://{self.bv_host}/sincronizar", json={'relogio': self.relogio})
            response.raise_for_status()
            relogio_bv = response.json().get('relogio')
            self.atualizar_hora(relogio_bv)
            # Registrar no log o início e fim da sincronização
            logger.info(f"Início da sincronização - Relógio HB: {self.relogio}")
            logger.info(f"Fim da sincronização - Relógio HB: {self.relogio}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao sincronizar relógio com a BV: {e}")

    def atualizar_informacoes_acoes(self):
        try:
            response = requests.post(f"http://{self.bv_host}/atualizar_acoes", json={'acoes': self.acoes})
            response.raise_for_status()
            acoes_atualizadas = response.json().get('acoes')
            self.acoes = acoes_atualizadas
            logger.info("Informações das ações atualizadas com sucesso")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao atualizar informações das ações: {e}")

hb = HomeBroker()

@app.route('/acoes', methods=['GET'])
def listar_acoes():
    hb.get_acoes()
    return jsonify(hb.acoes)

@app.route('/comprar', methods=['POST'])
def comprar_acao():
    requisicao = request.get_json()
    acao = requisicao.get('acao')
    quantidade = requisicao.get('quantidade')
    return hb.comprar_acao(acao, quantidade)

@app.route('/vender', methods=['POST'])
def vender_acao():
    requisicao = request.get_json()
    acao = requisicao.get('acao')
    quantidade = requisicao.get('quantidade')
    return hb.vender_acao(acao, quantidade)

@app.route('/sincronizar', methods=['POST'])
def sincronizar_relogio_hb():
    requisicao = request.get_json()
    nova_hora = requisicao.get('hora')  # Alteração do nome da variável para corresponder à nova estrutura
    hb.atualizar_hora(nova_hora)  # Atualize o relógio do HB com o valor recebido
    return ''

@app.route('/atualizar_acoes', methods=['POST'])
def atualizar_acoes():
    requisicao = request.get_json()
    acoes_atualizadas = requisicao.get('acoes')
    # Atualize as informações das ações do HB de acordo com as ações atualizadas da BV
    hb.acoes = acoes_atualizadas
    return ''

@app.route('/pedido', methods=['POST'])
def analisar_pedido():
    requisicao = request.get_json()
    pedido = requisicao.get('pedido')
    return hb.analisar_pedido(pedido)


if __name__ == "__main__":
    app.run(host='localhost', port=8080)
