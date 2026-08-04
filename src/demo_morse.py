#!/usr/bin/env python3
import sys
import os
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from morse_decoder import MorseDecoder, ERRO, SYMBOLS_PER_DIGIT
from hardware import HardwareMorse

POLL_INTERVAL_S = 0.1


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

        buf = decoder.buffer_simbolos
        print(f"  Buffer atual: [{buf}]", flush=True)
        if len(buf) == SYMBOLS_PER_DIGIT:
            print("  5 simbolos — aguarde ~1s para fechar o digito.", flush=True)

    def loop_timeout():
        while not parar.is_set():
            time.sleep(POLL_INTERVAL_S)
            resultado = decoder.verificar_timeout()
            if resultado == ERRO:
                print("  ✗ Sequência inválida — buffer limpo.\n", flush=True)
                hw.piscar_erro()
            elif resultado is not None:
                senha_parcial.append(resultado)
                print(
                    f"  ✓ Dígito: {resultado}  |  Senha: "
                    f"{''.join(senha_parcial)}{'_' * (4 - len(senha_parcial))}\n",
                    flush=True,
                )

    hw = HardwareMorse(callback_toque=ao_receber_toque)
    parar = threading.Event()
    t = threading.Thread(target=loop_timeout, daemon=True)
    t.start()

    print("=" * 50)
    print("  Demo Morse — timeout revisado (S2)")
    print("  Botão S4 GPIO 26 | RGB: G6 R5 B13")
    print("  Curto = .  |  Longo = -")
    print("  Pausa < 5 simbolos: buffer preservado")
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
