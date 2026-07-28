#!/usr/bin/env python3
"""
hardware.py — Abstração do botão Morse e LEDs (Semana 1).

Responsabilidades desta versão:
    - Botão Morse (GPIO 17): detecta pressão e soltura, mede duração do toque.
    - LED Verde  (GPIO 23): pisca ao registrar ponto (.).
    - LED Vermelho (GPIO 24): pisca ao registrar traço (-).

Semanas seguintes adicionarão: botão Confirmar, botão Cancelar, buzzer.

Pinagem (BCM) — Freenove Projects Kit for Raspberry Pi:
    Botão Morse  -> GPIO 26       (botão S4 da placa Freenove)
    RGB LED Red  -> GPIO 5        (LED RGB da placa Freenove — traço)
    RGB LED Green-> GPIO 6        (LED RGB da placa Freenove — ponto)
    RGB LED Blue -> GPIO 13       (LED RGB da placa Freenove — erro)

Referência: https://docs.freenove.com/projects/fnk0054/en/latest/fnk0054/c%26py.html
"""

import time
from gpiozero import Button, RGBLED

PIN_BOTAO_MORSE = 26
PIN_RGB_RED     = 5
PIN_RGB_GREEN   = 6
PIN_RGB_BLUE    = 13

DEBOUNCE_S       = 0.05   # RNF2 — debounce de ~50ms
DURACAO_PISCA_S  = 0.1    # duração do pisca de confirmação do LED


class HardwareMorse:
    """Abstração do botão Morse e LED RGB para a Semana 1.

    Args:
        callback_toque: função chamada com a duração do toque (float, em
            segundos) sempre que o botão for pressionado e solto.
    """

    def __init__(self, callback_toque):
        self._callback_toque = callback_toque
        self._inicio_toque   = None

        self.botao = Button(PIN_BOTAO_MORSE, bounce_time=DEBOUNCE_S)
        self.rgb   = RGBLED(red=PIN_RGB_RED, green=PIN_RGB_GREEN,
                            blue=PIN_RGB_BLUE, active_high=False)

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

    # ── Feedback visual (RGB) ──────────────────────────────────────
    def piscar_ponto(self):
        """RGB verde pisca — confirma ponto (.)."""
        self.rgb.color = (0, 1, 0)
        time.sleep(DURACAO_PISCA_S)
        self.rgb.off()

    def piscar_traco(self):
        """RGB vermelho pisca — confirma traço (-)."""
        self.rgb.color = (1, 0, 0)
        time.sleep(DURACAO_PISCA_S)
        self.rgb.off()

    def piscar_erro(self):
        """RGB azul pisca — sinaliza sequência inválida."""
        self.rgb.color = (0, 0, 1)
        time.sleep(DURACAO_PISCA_S * 3)
        self.rgb.off()

    def apagar_leds(self):
        self.rgb.off()

    # ── Encerramento limpo ─────────────────────────────────────────
    def cleanup(self):
        """Libera os recursos GPIO."""
        self.apagar_leds()
        self.botao.close()
        self.rgb.close()
