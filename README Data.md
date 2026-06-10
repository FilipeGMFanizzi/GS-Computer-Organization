# Mission Control AI - Sistema de Monitoramento de Missão Espacial

GS2026.1 - Arquitetura e Organização de Computadores
FIAP - Pensamento Computacional e Automação com Python

---

## Integrantes

- Filipe Gunther - RM: 571131
- Lucas Pinheiro Barbosa - RM: 573497
- Guilherme Guimarães - RM: 572957

---

## Sobre o projeto

Projeto feito para a Global Solution 2026.1. O sistema simula o monitoramento de uma missão espacial, lendo dados de sensores e transmitindo essas informações usando comunicação serial (UART) e paralela, representando tudo em binário.

---

## O que o sistema faz

Ele lê valores simulados de sensores como temperatura, energia, pressão e radiação, converte esses valores pra binário de 8 bits e simula duas formas de transmissão: a paralela, que manda os 8 bits de uma vez só num único pulso de clock, e a serial no padrão UART a 9600 bps, que envia bit a bit com start bit, dados, paridade e stop bit.

Também tem um sistema de alertas que acende flags no byte de alerta dependendo dos valores lidos, e no final exibe um relatório com as estatísticas da missão.

---

## Como rodar

Precisa ter Python 3.8 ou superior instalado.

```bash
# roda com 3 ciclos por padrão
python main.py

# ou passa o número de ciclos que quiser
python main.py 5
```

Ctrl+C encerra o programa a qualquer momento.

---

## Conceitos aplicados

- Conversão decimal para binário e vice-versa
- Comunicação paralela via barramento de 8 bits
- Protocolo UART para comunicação serial assíncrona
- Bit de paridade para detecção de erros
- Operações bitwise para controle de flags de alerta
