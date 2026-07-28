#!/usr/bin/env python3
"""
demo_morse.py — Demonstração interativa do decodificador Morse (Semana 1).

Executa no Raspberry Pi com botão e LEDs conectados.
Não depende de LCD, buzzer, banco de dados nem Flask.

Hardware necessário (todos já na placa Freenove — nenhum fio extra):
    Botão Morse  -> GPIO 26  (botão S4)
    RGB LED Red  -> GPIO 5   (traço = vermelho)
    RGB LED Green-> GPIO 6   (ponto  = verde)
    RGB LED Blue -> GPIO 13  (erro   = azul)

Como usar:
    python3 src/demo_morse.py

Fluxo:
    1. Pressione o botão Morse:
       - Toque curto (< 0,3s) = ponto  '.'  -> LED verde pisca
       - Toque longo (>= 0,3s) = traço '-'  -> LED vermelho pisca
    2. Após 5 símbolos, o dígito decodificado é exibido no terminal.
    3. Após 1s sem tocar, o dígito atual é fechado automaticamente.
    4. Sequência inválida -> mensagem de erro, buffer limpo.
    5. Ctrl+C encerra o programa.
"""

import sys
import os
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from morse_decoder import MorseDecoder, ERRO, DIGIT_GAP_TIMEOUT
from hardware import HardwareMorse

POLL_INTERVAL_S = 0.1   # intervalo de verificação de timeout


def main():
    decoder = MorseDecoder()
    senha_parcial = []

    def ao_receber_toque(duracao):
        simbolo = decoder.registrar_toque(duracao)
        if simbolo is None:
            return

        if simbolo == ".":
            print(f"  . (ponto  — {duracao:.2f}s)", flush=True)
            hw.piscar_ponto()
        else:
            print(f"  - (traço  — {duracao:.2f}s)", flush=True)
            hw.piscar_traco()

        print(f"  Buffer atual: [{decoder.buffer_simbolos}]", flush=True)

        if len(decoder.buffer_simbolos) == 5:
            _fechar_digito()

    def _fechar_digito():
        resultado = decoder.fechar_digito_se_completo()
        if resultado == ERRO:
            print("  ✗ Sequência inválida — buffer limpo.\n", flush=True)
            hw.piscar_erro()
        else:
            senha_parcial.append(resultado)
            print(f"  ✓ Dígito: {resultado}  |  Senha até agora: "
                  f"{''.join(senha_parcial)}{'_' * (4 - len(senha_parcial))}\n",
                  flush=True)

    def loop_timeout():
        while not parar.is_set():
            time.sleep(POLL_INTERVAL_S)
            resultado = decoder.verificar_timeout()
            if resultado == ERRO:
                print("  ✗ Sequência inválida (timeout) — buffer limpo.\n",
                      flush=True)
                hw.piscar_erro()
            elif resultado is not None:
                senha_parcial.append(resultado)
                print(f"  ✓ Dígito (timeout): {resultado}  |  Senha: "
                      f"{''.join(senha_parcial)}{'_' * (4 - len(senha_parcial))}\n",
                      flush=True)

    hw    = HardwareMorse(callback_toque=ao_receber_toque)
    parar = threading.Event()
    t     = threading.Thread(target=loop_timeout, daemon=True)
    t.start()

    print("=" * 50)
    print("  Demo Morse — Semana 1")
    print("  Botão S4 GPIO 26 | RGB: verde=GPIO6  vermelho=GPIO5  azul=GPIO13")
    print("  Toque curto = .  |  Toque longo = -")
    print("  Ctrl+C para encerrar")
    print("=" * 50 + "\n")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nEncerrando...")
    finally:
        parar.set()
        hw.cleanup()
        print("GPIO liberado. Até mais!")


if __name__ == "__main__":
    main()
