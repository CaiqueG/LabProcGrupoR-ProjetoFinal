#!/usr/bin/env python3
"""
demo_validacao.py — Demonstração Semana 2: Morse + LCD + DB + buzzer.

  - Botão Limpa (GPIO 20): apaga só o dígito mais recente da senha.
  - Timeout NÃO descarta dígito incompleto; só fecha após 5 símbolos + pausa ≥ 1s.
  - Confirmar valida senha completa (ou fecha dígito com 5 símbolos sem esperar o gap).

Hardware (Freenove FNK0054 + protoboard):
    Botão Morse (S4)  -> GPIO 26
    Botão Confirmar   -> GPIO 16  (protoboard)
    Botão Limpa       -> GPIO 20  (protoboard)
    RGB LED           -> GPIO 5/6/13
    Buzzer            -> GPIO 12
    LCD 1602 I2C      -> SDA=GPIO2, SCL=GPIO3  (opcional — fallback console)

Senha rápida de teste (só pontos): 5555 = ..... ..... ..... .....

Como usar:
    python3 src/demo_validacao.py
"""

import os
import sys
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from morse_decoder import MorseDecoder, ERRO, MAX_DIGITS, SYMBOLS_PER_DIGIT
from hardware import HardwareMorse, DURACAO_RESULTADO_S
from database import validar_senha, registrar_presenca
from lcd_driver import LCDDisplay

POLL_INTERVAL_S = 0.1


def _mascara_senha(senha):
    return senha + "_" * (MAX_DIGITS - len(senha))


def main():
    decoder = MorseDecoder()
    lcd = LCDDisplay()
    lock = threading.Lock()
    parar = threading.Event()

    def _mostrar_idle():
        lcd.mostrar("Digite a senha", "em Morse")

    def _mostrar_senha():
        if decoder.senha_completa():
            lcd.mostrar(f"Senha:{decoder.senha}", "Confirme ->")
        elif decoder.senha:
            lcd.mostrar(f"Senha:{_mascara_senha(decoder.senha)}", "Proximo digito")
        else:
            _mostrar_idle()

    def _apos_digito(resultado):
        """Atualiza LCD/terminal depois de fechar um dígito (timeout ou Confirmar)."""
        if resultado == ERRO:
            print("  ✗ Sequência inválida — buffer limpo.", flush=True)
            lcd.mostrar("Seq. invalida", "Tente de novo")
            hw.piscar_erro()
            time.sleep(0.5)
            lcd.mostrar(f"Senha:{_mascara_senha(decoder.senha)}", "Continue...")
            return

        print(
            f"  ✓ Dígito: {resultado}  |  Senha: {_mascara_senha(decoder.senha)}",
            flush=True,
        )
        if decoder.senha_completa():
            lcd.mostrar(f"Senha:{decoder.senha}", "Confirme ->")
            print("  Senha completa — pressione Confirmar.", flush=True)
        else:
            lcd.mostrar(f"Senha:{_mascara_senha(decoder.senha)}", "Proximo digito")

    def ao_receber_toque(duracao):
        with lock:
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
            print(f"  Buffer: [{buf}]  Senha: {_mascara_senha(decoder.senha)}", flush=True)

            if len(buf) == SYMBOLS_PER_DIGIT:
                lcd.mostrar(f"Senha:{_mascara_senha(decoder.senha)}", f"Buf: {buf} ...")
                print("  5 simbolos — aguarde ~1s (ou Confirmar).", flush=True)
            else:
                lcd.mostrar(f"Senha:{_mascara_senha(decoder.senha)}", f"Buf: {buf}")

    def ao_confirmar():
        with lock:
            if len(decoder.buffer_simbolos) == SYMBOLS_PER_DIGIT:
                _apos_digito(decoder.fechar_digito_se_completo())

            if decoder.buffer_simbolos:
                lcd.mostrar("Digito incompleto", f"Buf: {decoder.buffer_simbolos}")
                print(
                    f"  Digito incompleto [{decoder.buffer_simbolos}] — "
                    "continue ou Limpa.",
                    flush=True,
                )
                return

            if not decoder.senha_completa():
                lcd.mostrar("Faltam digitos", _mascara_senha(decoder.senha))
                print("  Ainda faltam dígitos.", flush=True)
                return

            senha = decoder.senha
            nome = validar_senha(senha)
            if nome:
                registrar_presenca(nome)
                print(f"  ✓ Presença: {nome} (senha {senha})", flush=True)
                lcd.mostrar("Presenca OK", nome[:16])
                hw.sinalizar_sucesso()
            else:
                print(f"  ✗ Senha inválida: {senha}", flush=True)
                lcd.mostrar("Senha invalida", senha)
                hw.sinalizar_falha()

        # Fora do lock: espera o feedback e reinicia
        time.sleep(DURACAO_RESULTADO_S)
        with lock:
            decoder.limpar()
            hw.apagar_leds()
            hw.parar_buzzer()
            _mostrar_idle()

    def ao_limpar():
        """Apaga só o último dígito já guardado na senha (GPIO 20).
        Ex.: senha 55__ → Limpa → 5___
        """
        with lock:
            removido = decoder.apagar_ultimo_digito()
            hw.apagar_leds()
            if removido is None:
                print("  Limpa: nada a apagar.", flush=True)
                lcd.mostrar("Nada a apagar", "")
                time.sleep(0.3)
                _mostrar_idle()
                return
            print(
                f"  Limpa: removeu '{removido}'  |  Senha: {_mascara_senha(decoder.senha)}",
                flush=True,
            )
            lcd.mostrar("Apagou digito", f"Senha:{_mascara_senha(decoder.senha)}")
            time.sleep(0.3)
            _mostrar_senha()

    def loop_timeout():
        while not parar.is_set():
            time.sleep(POLL_INTERVAL_S)
            with lock:
                resultado = decoder.verificar_timeout()
                if resultado is not None:
                    _apos_digito(resultado)

    hw = HardwareMorse(
        callback_toque=ao_receber_toque,
        callback_confirmar=ao_confirmar,
        callback_cancelar=ao_limpar,
    )
    t = threading.Thread(target=loop_timeout, daemon=True)
    t.start()

    _mostrar_idle()
    print("=" * 56)
    print("  Demo Validação — Semana 2")
    print("  Morse S4=GPIO26 | Confirmar=GPIO16 | Limpa=GPIO20")
    print("  RGB 5/6/13 | Buzzer=GPIO12 | LCD I2C (opcional)")
    print("  Limpa = apaga so o ultimo digito (ex: 55 -> 5)")
    print("  Sucesso = 3 bipes curtos (nao infinito)")
    print("  Senhas: 1234, 5678, 0192 | teste: 5555 (..... x4)")
    print("  Ctrl+C para encerrar")
    print("=" * 56 + "\n")

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
