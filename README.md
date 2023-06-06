# Relatório do Projeto - Sistema Distribuído para Compra e Venda de Ações
## 1. INTRODUÇÃO
Este relatório detalha um projeto que visa simular um sistema distribuído responsável pela compra e venda de ações numa bolsa de valores. O sistema é composto por três componentes principais: Bolsa de Valores (BV), Home Broker (HB) e Robôs. A BV controla a lista de ações disponíveis, a quantidade de ações para compra/venda e o valor atual de cada ação. Os sistemas de HB são responsáveis por enviar ordens de compra/venda para a BV. Os Robôs, vinculados a um HB, fazem pedidos de compra ou venda de ações, baseados em alguma estratégia de tomada de decisão.

## 2. ESTRUTURA
### 2.1 BOLSA DE VALORES
A Bolsa de Valores (BV) é um servidor central que mantém e gerencia a lista de ações disponíveis, a quantidade dessas ações para compra/venda e o valor atual de cada ação. A BV também é responsável por iniciar um processo de sincronização usando o algoritmo de Berkeley, caso detecte que a hora em que um pedido foi emitido está fora de sincronia com seu relógio local.

### 2.2 HOME BROKER
Os sistemas de Home Broker (HB) atuam como intermediários entre a BV e os robôs. Eles são responsáveis por enviar pedidos de compra/venda para a BV. Cada HB pode ter vários robôs associados, e cada robô pode emitir ordens de compra ou venda de ações por meio do HB ao qual está vinculado.

### 2.3 ROBO
Os robôs são sistemas autônomos que tomam decisões sobre quando comprar ou vender ações. Eles estão vinculados a um HB e enviam seus pedidos de compra/venda através dele. A decisão de comprar ou vender é tomada com base em uma estratégia aleatória neste projeto.

### 2.4 COMUNICAÇÃO
A comunicação entre os componentes do sistema é realizada através de solicitações HTTP. As mensagens de compra/venda enviadas pelos robôs aos HBs contêm a hora do sistema de HB. A BV analisa o tempo em que a mensagem foi enviada para decidir se aceita o pedido ou se inicia o processo de sincronização.

### 2.5 ERROS E LOGS
O sistema possui mecanismos para lidar com erros e fazer logs. No caso de uma exceção durante a execução, ela é capturada e um log de erro é gerado. Além disso, o sistema mantém registros de suas ações, incluindo o início da sincronização, a hora dos processos antes e depois da sincronização, etc.

## 3. TESTES
Para executar o projeto em um ambiente local, siga as etapas abaixo:

Garanta que você tenha Python instalado em sua máquina.
Clone o repositório do projeto.
Navegue até a pasta do projeto.
Execute o script da Bolsa de Valores (bv.py).
Em um novo terminal, execute o script do Home Broker (hb.py).
Em outro terminal, execute o script do robô (robo.py).
Observe o comportamento do sistema através das mensagens de log exibidas no console.

Para parar os scripts, você pode usar as seguintes opções:

Pressione Ctrl + C no terminal onde o script está sendo executado.
Use a função exit() no script para encerrar a execução programaticamente.
Use o método sys.exit() para parar até mesmo programas multi-threaded.

## 4. CONCLUSÃO
Este sistema distribuído para compra e venda de ações é um projeto interessante que permite explorar várias técnicas e conceitos em sistemas distribuídos. Ele inclui comunicação entre diferentes sistemas, sincronização de relógios usando o algoritmo de Berkeley, e a implementação de um sistema autônomo (robôs) que toma decisões de compra/venda.

O projeto também inclui a implementação de um sistema de registro e tratamento de erros, que é crucial para qualquer sistema distribuído. A capacidade de rastrear e lidar com erros é vital para a manutenção e depuração do sistema.

A execução do projeto em um ambiente local permite aos usuários explorar o funcionamento do sistema de uma forma mais concreta, podendo assim entender melhor como os componentes interagem e como as decisões são tomadas.

Este projeto serve como uma excelente base para futuros projetos relacionados à simulação de bolsas de valores e a sistemas distribuídos em geral. Ele pode ser expandido e adaptado para incluir mais funcionalidades e para simular cenários mais complexos.

## INTEGRANTES
Lucca Bonsi Guarreschi / 22.120.016-5  
João Vitor de Souza Lisboa / 22.120.082-7
