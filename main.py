"""
=============================================================================
  GS2026.1 - Arquitetura e Organizacao de Computadores
  SISTEMA DE MONITORAMENTO DE MISSAO ESPACIAL
  Grupo: Guilherme Guimaraes - Lucas Pinheiro Barbosa - Filipe Gunther
=============================================================================
  Simula comunicacao SERIAL e PARALELA entre dispositivos embarcados,
  com processamento e interpretacao de dados binarios em tempo real.
=============================================================================
"""

import time
import random
import os
import sys
from datetime import datetime


# -----------------------------------------------------------------------------
# UTILITARIOS BINARIOS
# -----------------------------------------------------------------------------

def decimal_para_binario(valor: int, bits: int = 8) -> str:
    if valor < 0:
        valor = 0
    if valor > (2 ** bits - 1):
        valor = 2 ** bits - 1
    return format(valor, f'0{bits}b')


def binario_para_decimal(binario: str) -> int:
    return int(binario, 2)


def interpretar_alerta(byte_alerta: str) -> list:

    sistemas = [
        "Propulsao",
        "Oxigenio",
        "Energia solar",
        "Comunicacao",
        "Temperatura",
        "Radiacao",
        "Pressao",
        "Navegacao",
    ]
    alertas = []
    for i, bit in enumerate(byte_alerta):
        if bit == '1':
            alertas.append(sistemas[i])
    return alertas


def calcular_paridade(byte: str) -> int:
    """Calcula bit de paridade par para deteccao de erro."""
    return byte.count('1') % 2


# -----------------------------------------------------------------------------
# COMUNICACAO PARALELA
# Transmite 8 bits simultaneamente por 8 fios (barramento)
# -----------------------------------------------------------------------------

class ComunicacaoParalela:
    """
    Simula um barramento paralelo de 8 bits.
    Todos os bits sao transmitidos ao mesmo tempo em um unico pulso de clock.
    """

    def __init__(self):
        self.barramento = ['0'] * 8
        self.historico  = []

    def transmitir(self, valor: int, rotulo: str = "") -> str:

        byte = decimal_para_binario(valor, 8)
        self.barramento = list(byte)

        registro = {
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:12],
            "rotulo":    rotulo,
            "decimal":   valor,
            "binario":   byte,
            "paridade":  calcular_paridade(byte),
        }
        self.historico.append(registro)
        return byte

    @staticmethod
    def exibir_barramento(byte: str, rotulo: str) -> None:
        """Exibe visualmente o barramento paralelo."""
        print(f"\n  {'-'*44}")
        print(f"  TRANSMISSAO PARALELA -> {rotulo}")
        print(f"  {'-'*44}")
        print(f"  Fio:    D7  D6  D5  D4  D3  D2  D1  D0")
        fios = "   ".join(byte)
        print(f"  Bit:     {fios}")
        print(f"  {'-'*44}")
        print(f"  Todos os 8 bits enviados em 1 pulso de clock")
        print(f"  Paridade: {calcular_paridade(byte)} (paridade par)")
        print(f"  Decimal : {binario_para_decimal(byte)}")
        print(f"  {'-'*44}")


# -----------------------------------------------------------------------------
# COMUNICACAO SERIAL (UART)
# Transmite bits sequencialmente: start bit -> 8 bits de dados -> stop bit
# -----------------------------------------------------------------------------

class ComunicacaoSerial:
    """
    Simula UART (Universal Asynchronous Receiver-Transmitter).
    Frame: 1 start bit (0) + 8 bits de dados (LSB primeiro) + 1 stop bit (1)
    Velocidade simulada: 9600 bps
    """

    BAUD_RATE    = 9600
    DELAY_VISUAL = 0.08

    def __init__(self):
        self.historico = []
        self.erros     = 0

    def transmitir(self, valor: int, rotulo: str = "", visual: bool = True) -> dict:
        """
        Transmite um byte via UART, bit a bit, com start e stop bits.
        Retorna dicionario com todos os detalhes da transmissao.
        """
        byte     = decimal_para_binario(valor, 8)
        paridade = calcular_paridade(byte)

        dados_lsb = byte[::-1]
        frame     = ['0'] + list(dados_lsb) + [str(paridade)] + ['1']
        frame_str = ''.join(frame)

        if visual:
            self._exibir_serial(byte, frame, rotulo, valor, paridade)

        registro = {
            "timestamp":   datetime.now().strftime("%H:%M:%S.%f")[:12],
            "rotulo":      rotulo,
            "decimal":     valor,
            "binario":     byte,
            "frame":       frame_str,
            "paridade":    paridade,
            "bits_totais": len(frame),
        }
        self.historico.append(registro)
        return registro

    def _exibir_serial(self, byte: str, frame: list, rotulo: str,
                       valor: int, paridade: int) -> None:
        """Exibe a transmissao serial bit a bit com animacao visual."""
        print(f"\n  {'-'*52}")
        print(f"  TRANSMISSAO SERIAL (UART 9600 bps) -> {rotulo}")
        print(f"  {'-'*52}")
        print(f"  Frame: START + 8 bits (LSB->MSB) + PARIDADE + STOP")
        print(f"  Total: 11 bits por byte")
        print()

        labels = ["STA"] + [f"D{i}" for i in range(8)] + ["PAR"] + ["STO"]
        header = "  " + "  ".join(f"{l:>3}" for l in labels)
        print(header)

        linha_bits = "  " + "  ".join(f"{b:>3}" for b in frame)
        print(linha_bits)

        print()
        print(f"  Dados (MSB->LSB): {byte}  =  {valor} decimal")
        print(f"  Bit de paridade : {paridade} (paridade par)")
        print(f"  {'-'*52}")

        print(f"  Enviando bit a bit ", end="", flush=True)
        for bit in frame:
            print(f"[{bit}]", end="", flush=True)
            time.sleep(self.DELAY_VISUAL)
        print(" OK")
        print(f"  {'-'*52}")


# -----------------------------------------------------------------------------
# SENSORES DA NAVE
# -----------------------------------------------------------------------------

class SensoresDaNave:
    """
    Gera leituras simuladas dos sensores da missao espacial.
    Cada leitura e um valor inteiro de 0 a 255 (8 bits).
    """

    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
        self.ciclo = 0

    def ler(self) -> dict:
        """Retorna leituras de todos os sensores no ciclo atual."""
        self.ciclo += 1

        temperatura = random.randint(18, 35)
        energia     = random.randint(60, 100)
        pressao     = random.randint(95, 105)
        radiacao    = random.randint(0, 15)

        alerta = 0
        if temperatura > 30:
            alerta |= 0b00010000
        if energia < 70:
            alerta |= 0b00000100
        if radiacao > 10:
            alerta |= 0b00100000
        if self.ciclo % 7 == 0:
            alerta |= 0b00000001

        return {
            "ciclo":       self.ciclo,
            "temperatura": temperatura,
            "energia":     energia,
            "pressao":     pressao,
            "radiacao":    radiacao,
            "alerta":      alerta,
            "timestamp":   datetime.now().strftime("%H:%M:%S"),
        }


# -----------------------------------------------------------------------------
# SISTEMA DE MONITORAMENTO PRINCIPAL
# -----------------------------------------------------------------------------

class SistemaMissaoEspacial:
    """
    Integra sensores, comunicacao serial, comunicacao paralela
    e processamento binario em um unico sistema de monitoramento.
    """

    def __init__(self):
        self.serial   = ComunicacaoSerial()
        self.paralela = ComunicacaoParalela()
        self.sensores = SensoresDaNave()
        self.log      = []

    @staticmethod
    def cabecalho() -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
        print()
        print("  +======================================================+")
        print("  |   SISTEMA DE MONITORAMENTO -- MISSAO ESPACIAL        |")
        print("  |       GS2026.1 - Arquitetura de Computadores         |")
        print("  +======================================================+")
        print()

    @staticmethod
    def exibir_painel(dados: dict) -> None:
        """Painel de status da missao com valores e representacao binaria."""
        print(f"  +-----------------------------------------------------+")
        print(f"  |  PAINEL DA MISSAO -- Ciclo {dados['ciclo']:03d} -- {dados['timestamp']}    |")
        print(f"  +------------------+----------+-----------------------+")
        print(f"  | Sensor           | Valor    | Binario (8 bits)      |")
        print(f"  +------------------+----------+-----------------------+")

        campos = [
            ("Temperatura (C)",  dados["temperatura"]),
            ("Energia (%)",      dados["energia"]),
            ("Pressao (kPa)",    dados["pressao"]),
            ("Radiacao (mSv)",   dados["radiacao"]),
        ]
        for nome, valor in campos:
            bin_str = decimal_para_binario(valor)
            print(f"  | {nome:<16} | {valor:<8} | {bin_str}              |")

        print(f"  +------------------+----------+-----------------------+")
        bin_alerta = decimal_para_binario(dados["alerta"])
        print(f"  | Byte de Alerta   | {dados['alerta']:<8} | {bin_alerta}              |")
        print(f"  +-----------------------------------------------------+")

        alertas = interpretar_alerta(bin_alerta)
        if alertas:
            print(f"\n  [ALERTA] Sistemas com falha: {', '.join(alertas)}")
        else:
            print(f"\n  [OK] Todos os sistemas operando normalmente")

    @staticmethod
    def exibir_tabela_binaria(dados: dict) -> None:

        print(f"\n  {'-'*54}")
        print(f"  TABELA DE REPRESENTACAO BINARIA -- CICLO {dados['ciclo']:03d}")
        print(f"  {'-'*54}")
        print(f"  {'Informacao':<20} {'Decimal':>8}   {'Binario (8 bits)':<20}")
        print(f"  {'-'*54}")

        itens = [
            ("Temperatura",    dados["temperatura"]),
            ("Energia",        dados["energia"]),
            ("Pressao",        dados["pressao"]),
            ("Radiacao",       dados["radiacao"]),
            ("Byte de Alerta", dados["alerta"]),
        ]
        for nome, val in itens:
            b = decimal_para_binario(val)
            print(f"  {nome:<20} {val:>8}   {b}")
        print(f"  {'-'*54}")

    def ciclo_transmissao(self, dados: dict) -> None:

        print(f"\n  {'='*54}")
        print(f"  INICIANDO TRANSMISSAO -- CICLO {dados['ciclo']:03d}")
        print(f"  {'='*54}")

        byte_temp = self.paralela.transmitir(dados["temperatura"], "TEMPERATURA")
        self.paralela.exibir_barramento(byte_temp, f"Temperatura = {dados['temperatura']}C")
        time.sleep(0.5)

        self.serial.transmitir(dados["energia"], f"ENERGIA = {dados['energia']}%")
        time.sleep(0.3)

        byte_alerta = self.paralela.transmitir(dados["alerta"], "ALERTA")
        self.paralela.exibir_barramento(byte_alerta, f"Byte de Alerta = {dados['alerta']}")
        time.sleep(0.5)

        self.serial.transmitir(dados["pressao"], f"PRESSAO = {dados['pressao']} kPa")
        time.sleep(0.3)

        print(f"\n  {'-'*54}")
        print(f"  RESUMO DO CICLO {dados['ciclo']:03d}")
        print(f"  {'-'*54}")
        print(f"  Transmissoes paralelas: 2  (2 pulsos de clock = 16 bits)")
        print(f"  Transmissoes seriais  : 2  (11 bits cada = 22 bits total)")
        print(f"  Total de bits trafegados: 38 bits neste ciclo")
        print(f"  {'-'*54}")

        self.log.append(dados)

    def executar(self, ciclos: int = 3) -> None:
        """Executa N ciclos completos de monitoramento e transmissao."""
        self.cabecalho()

        print("  Inicializando sistema de monitoramento...")
        print("  Verificando subsistemas:")
        time.sleep(0.4)
        for sub in [
            "Comunicacao paralela (barramento 8 bits)",
            "Comunicacao serial (UART 9600 bps)",
            "Processamento binario",
            "Sensores embarcados",
        ]:
            print(f"    [OK] {sub}")
            time.sleep(0.2)

        print(f"\n  Sistema pronto. Iniciando {ciclos} ciclo(s) de monitoramento...\n")
        time.sleep(1)

        for c in range(ciclos):
            dados = self.sensores.ler()
            self.cabecalho()
            self.exibir_painel(dados)
            self.exibir_tabela_binaria(dados)
            self.ciclo_transmissao(dados)

            if c < ciclos - 1:
                print(f"\n  Proximo ciclo em 3 segundos... (Ctrl+C para encerrar)\n")
                time.sleep(3)

        self._relatorio_final()

    def _relatorio_final(self) -> None:

        print(f"\n\n  {'='*54}")
        print(f"  RELATORIO FINAL DA MISSAO")
        print(f"  {'='*54}")
        print(f"  Ciclos executados      : {len(self.log)}")
        print(f"  Transmissoes paralelas : {len(self.paralela.historico)}")
        print(f"  Transmissoes seriais   : {len(self.serial.historico)}")

        if self.log:
            temps = [d["temperatura"] for d in self.log]
            energ = [d["energia"]     for d in self.log]
            print(f"  Temperatura media      : {sum(temps)/len(temps):.1f} C")
            print(f"  Energia media          : {sum(energ)/len(energ):.1f} %")

        alertas_totais = sum(1 for d in self.log if d["alerta"] > 0)
        print(f"  Ciclos com alerta      : {alertas_totais}/{len(self.log)}")
        print(f"  Erros de transmissao   : {self.serial.erros}")
        print(f"  {'='*54}")
        print(f"  Missao concluida.")
        print(f"  {'='*54}\n")


# -----------------------------------------------------------------------------
# PONTO DE ENTRADA
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    num_ciclos = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    sistema = SistemaMissaoEspacial()
    try:
        sistema.executar(ciclos=num_ciclos)
    except KeyboardInterrupt:
        print("\n\n  Missao interrompida pelo operador.\n")
