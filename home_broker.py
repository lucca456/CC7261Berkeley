import socket
import json
import time
import random

class HomeBroker:
    def __init__(self, host="localhost", port=12345):
        self.host = host
        self.port = port
        self.relogio = time.time()

    def conectar(self):
        try:
            self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cliente.connect((self.host, self.port))
        except Exception as e:
            print(f"Erro ao conectar: {e}")

    def desconectar(self):
        try:
            self.cliente.close()
        except Exception as e:
            print(f"Erro ao desconectar: {e}")

    def sincronizar_relogio(self):
        try:
            self.cliente.sendall(json.dumps({"action": "get_time"}).encode())
            data = self.cliente.recv(1024)
            self.relogio = json.loads(data.decode())
        except Exception as e:
            print(f"Erro ao sincronizar o relógio: {e}")
    
    def obter_acoes(self):
        try:
            self.cliente.sendall(json.dumps({"action": "get_all_stocks"}).encode())
            data = self.cliente.recv(1024)
            return json.loads(data.decode())
        except Exception as e:
            print(f"Erro ao obter ações: {e}")
            return None

    def comprar_acao(self, nome, quantidade):
        try:
            self.cliente.sendall(json.dumps({"action": "process_order", "stock": nome, "type": "compra", "quantity": quantidade}).encode())
            data = self.cliente.recv(1024)
            return json.loads(data.decode())
        except Exception as e:
            print(f"Erro ao comprar ação: {e}")
            return None

    def vender_acao(self, nome, quantidade):
        try:
            self.cliente.sendall(json.dumps({"action": "process_order", "stock": nome, "type": "venda", "quantity": quantidade}).encode())
            data = self.cliente.recv(1024)
            return json.loads(data.decode())
        except Exception as e:
            print(f"Erro ao vender ação: {e}")
            return None

    def atualizar_relogio(self):
        self.relogio += random.randint(-2, 2)