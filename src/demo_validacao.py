#!/usr/bin/env python3
"""
demo_validacao.py — Demonstração Semana 2: Morse + LCD + DB + buzzer.

Incorpora as lições da Semana 1:
  - Botão Cancelar físico para limpar buffer a qualquer momento.
  - Timeout NÃO descarta dígito incompleto; só fecha após 5 símbolos + pausa ≥ 1s.
  - Confirmar não apaga símbolos parciais — só valida senha completa (ou fecha
    dígito já com 5 símbolos sem esperar o gap).

Hardware (Freenove FNK0054 + protoboard):
    Botão Morse (S4)  -> GPIO 26
    Botão Confirmar   -> GPIO 16  (protoboard)
    Botão Cancelar    -> GPIO 21  (protoboard)
    RGB LED           -> GPIO 5/6/13
    Buzzer            -> GPIO 12
    LCD 1602 I2C      -> SDA=GPIO2, SCL=GPIO3  (opcional — fallback console)

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

            # Não fecha no 5º símbolo: espera pausa ≥ 1s (intervalo entre dígitos)
            if len(buf) == SYMBOLS_PER_DIGIT:
                lcd.mostrar(f"Senha:{_mascara_senha(decoder.senha)}", f"Buf: {buf} ...")
                print("  5 simbolos — aguarde ~1s (ou Confirmar).", flush=True)
            else:
                lcd.mostrar(f"Senha:{_mascara_senha(decoder.senha)}", f"Buf: {buf}")

    def ao_confirmar():
        with lock:
            # Fecha dígito com 5 símbolos sem esperar o gap (atalho)
            if len(decoder.buffer_simbolos) == SYMBOLS_PER_DIGIT:
                _apos_digito(decoder.fechar_digito_se_completo())

            # Buffer incompleto: NÃO apaga (lição S1) — só avisa
            if decoder.buffer_simbolos:
                lcd.mostrar("Digito incompleto", f"Buf: {decoder.buffer_simbolos}")
                print(
                    f"  Digito incompleto [{decoder.buffer_simbolos}] — "
                    "continue ou Cancelar.",
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

            time.sleep(DURACAO_RESULTADO_S)
            decoder.limpar()
            hw.apagar_leds()
            _mostrar_idle()

    def ao_cancelar():
        """Única forma de descartar digitação em andamento (RF3 / lição S1)."""
        with lock:
            decoder.limpar()
            hw.apagar_leds()
            print("  ✗ Cancelado — buffer limpo.", flush=True)
            lcd.mostrar("Cancelado", "Digite a senha")
            time.sleep(0.4)
            _mostrar_idle()

    def loop_timeout():
        """Fecha só dígito completo após pausa ≥ 1s; incompleto fica intacto."""
        while not parar.is_set():
            time.sleep(POLL_INTERVAL_S)
            with lock:
                resultado = decoder.verificar_timeout()
                if resultado is not None:
                    _apos_digito(resultado)

    hw = HardwareMorse(
        callback_toque=ao_receber_toque,
        callback_confirmar=ao_confirmar,
        callback_cancelar=ao_cancelar,
    )
    t = threading.Thread(target=loop_timeout, daemon=True)
    t.start()

    _mostrar_idle()
    print("=" * 56)
    print("  Demo Validação — Semana 2")
    print("  Morse S4=GPIO26 | Confirmar=GPIO16 | Cancelar=GPIO21")
    print("  RGB 5/6/13 | Buzzer=GPIO12 | LCD I2C (opcional)")
    print("  Timeout: so fecha apos 5 simbolos + pausa 1s")
    print("  Cancelar = unica forma de limpar buffer parcial")
    print("  Senhas teste: 1234, 5678, 0192")
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
