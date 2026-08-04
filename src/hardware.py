#!/usr/bin/env python3
"""
hardware.py — Abstração dos periféricos GPIO (Semana 2).

Biblioteca ÚNICA de GPIO: gpiozero (+ lgpio como backend).
Não usar RPi.GPIO neste projeto — conflito de driver na Aula 10.

Pinagem (BCM) — Freenove Projects Kit (FNK0054) + protoboard:

    Componente          Pino    Origem Freenove / doc
    ─────────────────────────────────────────────────
    Botão Morse         26      Botão S4 (Ch. 3 Buttons & LEDs)
    Botão Confirmar     16      Externo na protoboard
    Botão Cancelar      21      Externo na protoboard
    RGB LED Red         5       LED RGB da placa (Ch. 5 RGB LED)
    RGB LED Green       6       LED RGB da placa (Ch. 5 RGB LED)
    RGB LED Blue        13      LED RGB da placa (Ch. 5 RGB LED)
    Buzzer passivo      12      Conector Buzzer da placa Freenove

Referências:
    https://docs.freenove.com/projects/fnk0054/en/latest/fnk0054/codes/c%26py/3_Buttons_%26_LEDs.html
    https://docs.freenove.com/projects/fnk0054/en/latest/fnk0054/codes/c%26py/5_RGB_LED.html
"""

import threading
import time

from gpiozero import Button, RGBLED, TonalBuzzer
from gpiozero.tones import Tone

# ── Pinagem BCM (Freenove) ──────────────────────────────────────────
PIN_BOTAO_MORSE = 26
PIN_BOTAO_CONFIRMAR = 16
PIN_BOTAO_CANCELAR = 21
PIN_RGB_RED = 5
PIN_RGB_GREEN = 6
PIN_RGB_BLUE = 13
PIN_BUZZER = 12

DEBOUNCE_S = 0.05          # RNF2 — debounce de ~50ms
DURACAO_PISCA_S = 0.1
DURACAO_RESULTADO_S = 1.5

FREQ_SUCESSO_HZ = 880
FREQ_ERRO_HZ = 220
DURACAO_BIP_SUCESSO_S = 0.15
DURACAO_BIP_ERRO_S = 0.4


class HardwareMorse:
    """Periféricos GPIO da Semana 2: Morse + Confirmar + Cancelar + RGB + buzzer.

    Args:
        callback_toque: chamado com a duração (s) ao soltar o botão Morse.
        callback_confirmar: chamado ao pressionar Confirmar (opcional).
        callback_cancelar: chamado ao pressionar Cancelar (opcional).
    """

    def __init__(self, callback_toque, callback_confirmar=None, callback_cancelar=None):
        self._callback_toque = callback_toque
        self._callback_confirmar = callback_confirmar
        self._callback_cancelar = callback_cancelar
        self._inicio_toque = None

        self.botao_morse = Button(PIN_BOTAO_MORSE, bounce_time=DEBOUNCE_S)
        self.botao_confirmar = Button(PIN_BOTAO_CONFIRMAR, bounce_time=DEBOUNCE_S)
        self.botao_cancelar = Button(PIN_BOTAO_CANCELAR, bounce_time=DEBOUNCE_S)

        # Freenove RGB: cátodo comum → active_high=False (doc Ch. 5)
        self.rgb = RGBLED(
            red=PIN_RGB_RED, green=PIN_RGB_GREEN, blue=PIN_RGB_BLUE,
            active_high=False,
        )

        try:
            self.buzzer = TonalBuzzer(PIN_BUZZER)
        except Exception as exc:
            print(f"[HARDWARE] Buzzer indisponível ({exc}); seguindo sem áudio.")
            self.buzzer = None

        self.botao_morse.when_pressed = self._ao_pressionar_morse
        self.botao_morse.when_released = self._ao_soltar_morse
        self.botao_confirmar.when_pressed = self._ao_confirmar
        self.botao_cancelar.when_pressed = self._ao_cancelar

    # ── Callbacks internos ─────────────────────────────────────────
    def _ao_pressionar_morse(self):
        self._inicio_toque = time.monotonic()

    def _ao_soltar_morse(self):
        if self._inicio_toque is None:
            return
        duracao = time.monotonic() - self._inicio_toque
        self._inicio_toque = None
        self._callback_toque(duracao)

    def _ao_confirmar(self):
        if self._callback_confirmar:
            self._callback_confirmar()

    def _ao_cancelar(self):
        if self._callback_cancelar:
            self._callback_cancelar()

    # ── Feedback visual (RGB Freenove) ─────────────────────────────
    def piscar_ponto(self):
        """Verde — confirma ponto (.)."""
        self.rgb.color = (0, 1, 0)
        time.sleep(DURACAO_PISCA_S)
        self.rgb.off()

    def piscar_traco(self):
        """Vermelho — confirma traço (-)."""
        self.rgb.color = (1, 0, 0)
        time.sleep(DURACAO_PISCA_S)
        self.rgb.off()

    def piscar_erro(self):
        """Azul — sequência Morse inválida."""
        self.rgb.color = (0, 0, 1)
        time.sleep(DURACAO_PISCA_S * 3)
        self.rgb.off()

    def acender_sucesso(self):
        """Verde fixo — senha válida (RF2)."""
        self.rgb.color = (0, 1, 0)

    def acender_falha(self):
        """Vermelho fixo — senha inválida (RF2b)."""
        self.rgb.color = (1, 0, 0)

    def apagar_leds(self):
        self.rgb.off()

    # ── Buzzer (thread própria — RNF3 / RNF4) ──────────────────────
    def _tocar(self, freq_hz, duracao_s):
        if self.buzzer is None:
            return
        try:
            self.buzzer.play(Tone(frequency=freq_hz))
            time.sleep(duracao_s)
            self.buzzer.stop()
        except Exception as exc:
            print(f"[HARDWARE] Falha ao tocar buzzer: {exc}")

    def bip_sucesso(self):
        threading.Thread(
            target=self._tocar,
            args=(FREQ_SUCESSO_HZ, DURACAO_BIP_SUCESSO_S),
            daemon=True,
        ).start()

    def bip_erro(self):
        threading.Thread(
            target=self._tocar,
            args=(FREQ_ERRO_HZ, DURACAO_BIP_ERRO_S),
            daemon=True,
        ).start()

    def sinalizar_sucesso(self):
        self.acender_sucesso()
        self.bip_sucesso()

    def sinalizar_falha(self):
        self.acender_falha()
        self.bip_erro()

    # ── Encerramento limpo ─────────────────────────────────────────
    def cleanup(self):
        self.apagar_leds()
        if self.buzzer is not None:
            try:
                self.buzzer.close()
            except Exception:
                pass
        for botao in (self.botao_morse, self.botao_confirmar, self.botao_cancelar):
            try:
                botao.close()
            except Exception:
                pass
        self.rgb.close()
