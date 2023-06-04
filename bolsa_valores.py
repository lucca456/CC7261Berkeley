import time
import random
import socket
import threading
import json

class BolsaDeValores:
    def __init__(self, host="localhost", port=12345):
        self.relogio = time.time()
        self.acoes = {
            "A1": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2)},
            "A2": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2)},
            "A3": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2)},
            "A4": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2)},
        }
        self.host = host
        self.port = port
        self.conexoes = []

    def obtem_acao(self, nome):
        if nome in self.acoes:
            return self.acoes[nome]

    def lista_acoes(self):
        return self.acoes

    def processa_pedido(self, nome, tipo, quantidade):
        if nome in self.acoes and self.acoes[nome]["quantidade"] >= quantidade:
            if tipo == "compra":
                self.acoes[nome]["quantidade"] -= quantidade
            elif tipo == "venda":
                self.acoes[nome]["quantidade"] += quantidade
            return True
        else:
            return False

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Servidor iniciado em {self.host}:{self.port}. Aguardando conexões...")
            
            # Inicia a sincronização dos relógios em um thread separado
            threading.Thread(target=self.sync_clocks).start()
            
            while True:
                conn, addr = s.accept()
                self.conexoes.append(conn)
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()


    def handle_client(self, conn, addr):
        print(f"Conexão estabelecida com {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            request = json.loads(data.decode())
            if request["action"] == "get_time":
                conn.sendall(json.dumps(self.relogio).encode())
            elif request["action"] == "set_time":
                self.relogio = request["time"]
            elif request["action"] == "get_stock":
                conn.sendall(json.dumps(self.obtem_acao(request["stock"])).encode())
            elif request["action"] == "get_all_stocks":
                conn.sendall(json.dumps(self.lista_acoes()).encode())
            elif request["action"] == "process_order":
                result = self.processa_pedido(request["stock"], request["type"], request["quantity"])
                conn.sendall(json.dumps(result).encode())

    def sync_clocks(self):
        while True:
            time.sleep(10)  # Ajuste este valor para determinar a frequência de sincronização dos relógios
            times = []
            for conn in self.conexoes:
                conn.sendall(json.dumps({"action": "get_time"}).encode())
                data = conn.recv(1024)
                if data:
                    client_time = json.loads(data.decode())
                    times.append(client_time)

            if times:
                avg_time = sum(times) / len(times)
                self.relogio = avg_time

                for conn in self.conexoes:
                    conn.sendall(json.dumps({"action": "set_time", "time": avg_time}).encode())

if __name__ == "__main__":
    bolsa = BolsaDeValores()
    bolsa.run()
