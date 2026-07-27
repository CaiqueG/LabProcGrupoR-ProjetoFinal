#!/usr/bin/env python3
"""
hardware.py — Abstração do botão Morse e LEDs (Semana 1).

Responsabilidades desta versão:
    - Botão Morse (GPIO 17): detecta pressão e soltura, mede duração do toque.
    - LED Verde  (GPIO 23): pisca ao registrar ponto (.).
    - LED Vermelho (GPIO 24): pisca ao registrar traço (-).

Semanas seguintes adicionarão: botão Confirmar, botão Cancelar, buzzer.

Pinagem (BCM):
    Botão Morse  -> GPIO 17
    LED Verde    -> GPIO 23
    LED Vermelho -> GPIO 24
"""

import time
from gpiozero import Button, LED

PIN_BOTAO_MORSE  = 17
PIN_LED_VERDE    = 23
PIN_LED_VERMELHO = 24

DEBOUNCE_S       = 0.05   # RNF2 — debounce de ~50ms
DURACAO_PISCA_S  = 0.1    # duração do pisca de confirmação do LED


class HardwareMorse:
    """Abstração do botão Morse e LEDs para a Semana 1.

    Args:
        callback_toque: função chamada com a duração do toque (float, em
            segundos) sempre que o botão for pressionado e solto.
    """

    def __init__(self, callback_toque):
        self._callback_toque = callback_toque
        self._inicio_toque   = None

        self.botao     = Button(PIN_BOTAO_MORSE, bounce_time=DEBOUNCE_S)
        self.led_verde = LED(PIN_LED_VERDE)
        self.led_verm  = LED(PIN_LED_VERMELHO)

        self.botao.when_pressed  = self._ao_pressionar
        self.botao.when_released = self._ao_soltar

    # ── Callbacks internos ─────────────────────────────────────────
    def _ao_pressionar(self):
        self._inicio_toque = time.monotonic()

    def _ao_soltar(self):
        if self._inicio_toque is None:
            return
        duracao = time.monotonic() - self._inicio_toque
        self._inicio_toque = None
        self._callback_toque(duracao)

    # ── Feedback visual ────────────────────────────────────────────
    def piscar_ponto(self):
        """LED verde pisca brevemente — confirma registro de ponto (.)."""
        self.led_verde.on()
        time.sleep(DURACAO_PISCA_S)
        self.led_verde.off()

    def piscar_traco(self):
        """LED vermelho pisca brevemente — confirma registro de traço (-)."""
        self.led_verm.on()
        time.sleep(DURACAO_PISCA_S)
        self.led_verm.off()

    def apagar_leds(self):
        self.led_verde.off()
        self.led_verm.off()

    # ── Encerramento limpo ─────────────────────────────────────────
    def cleanup(self):
        """Libera os recursos GPIO."""
        self.apagar_leds()
        self.botao.close()
        self.led_verde.close()
        self.led_verm.close()
