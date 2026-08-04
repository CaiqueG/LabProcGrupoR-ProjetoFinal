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
    Botão Limpa         20      Externo na protoboard (apaga último dígito)
    Botão Cancelar      21      Externo na protoboard (zera senha + buffer)
    RGB LED Red         5       LED RGB da placa (Ch. 5 RGB LED)
    RGB LED Green       6       LED RGB da placa (Ch. 5 RGB LED)
    RGB LED Blue        13      LED RGB da placa (Ch. 5 RGB LED)
    Buzzer              12      Conector Buzzer da placa Freenove

Buzzer: usa gpiozero.Buzzer (liga/desliga). Evita TonalBuzzer, que no
Freenove gera "tone is out of device's range" e pode deixar o pino
zumbindo sem parar.
"""

import threading
import time

from gpiozero import Button, RGBLED, Buzzer

# ── Pinagem BCM (Freenove) ──────────────────────────────────────────
PIN_BOTAO_MORSE = 26
PIN_BOTAO_CONFIRMAR = 16
PIN_BOTAO_LIMPA = 20
PIN_BOTAO_CANCELAR = 21
PIN_RGB_RED = 5
PIN_RGB_GREEN = 6
PIN_RGB_BLUE = 13
PIN_BUZZER = 12

DEBOUNCE_S = 0.05          # RNF2 — debounce de ~50ms
DURACAO_PISCA_S = 0.1
DURACAO_RESULTADO_S = 1.5

# Três bipes curtos de sucesso (liga/desliga — sempre termina em off)
N_BIPES_SUCESSO = 3
DURACAO_BIP_SUCESSO_S = 0.12
PAUSA_ENTRE_BIPES_S = 0.10
DURACAO_BIP_ERRO_S = 0.40


class HardwareMorse:
    """Periféricos GPIO: Morse + Confirmar + Limpa + Cancelar + RGB + buzzer.

    Args:
        callback_toque: chamado com a duração (s) ao soltar o botão Morse.
        callback_confirmar: chamado ao pressionar Confirmar (opcional).
        callback_limpar: chamado ao pressionar Limpa — último dígito (opcional).
        callback_cancelar: chamado ao pressionar Cancelar — zera tudo (opcional).
    """

    def __init__(
        self,
        callback_toque,
        callback_confirmar=None,
        callback_limpar=None,
        callback_cancelar=None,
    ):
        self._callback_toque = callback_toque
        self._callback_confirmar = callback_confirmar
        self._callback_limpar = callback_limpar
        self._callback_cancelar = callback_cancelar
        self._inicio_toque = None
        self._buzzer_lock = threading.Lock()

        self.botao_morse = Button(PIN_BOTAO_MORSE, bounce_time=DEBOUNCE_S)
        self.botao_confirmar = Button(PIN_BOTAO_CONFIRMAR, bounce_time=DEBOUNCE_S)
        self.botao_limpar = Button(PIN_BOTAO_LIMPA, bounce_time=DEBOUNCE_S)
        self.botao_cancelar = Button(PIN_BOTAO_CANCELAR, bounce_time=DEBOUNCE_S)

        # Freenove RGB: cátodo comum → active_high=False (doc Ch. 5)
        self.rgb = RGBLED(
            red=PIN_RGB_RED, green=PIN_RGB_GREEN, blue=PIN_RGB_BLUE,
            active_high=False,
        )

        try:
            self.buzzer = Buzzer(PIN_BUZZER)
            self.buzzer.off()
        except Exception as exc:
            print(f"[HARDWARE] Buzzer indisponível ({exc}); seguindo sem áudio.")
            self.buzzer = None

        self.botao_morse.when_pressed = self._ao_pressionar_morse
        self.botao_morse.when_released = self._ao_soltar_morse
        self.botao_confirmar.when_pressed = self._ao_confirmar
        self.botao_limpar.when_pressed = self._ao_limpar
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

    def _ao_limpar(self):
        if self._callback_limpar:
            self._callback_limpar()

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

    # ── Buzzer (liga/desliga — RNF3 / RNF4) ────────────────────────
    def parar_buzzer(self):
        """Garante que o buzzer fica desligado."""
        if self.buzzer is None:
            return
        try:
            self.buzzer.off()
        except Exception:
            pass

    def _bipes(self, n, ligado_s, pausa_s):
        if self.buzzer is None:
            return
        with self._buzzer_lock:
            try:
                for i in range(n):
                    self.buzzer.on()
                    time.sleep(ligado_s)
                    self.buzzer.off()
                    if i < n - 1 and pausa_s > 0:
                        time.sleep(pausa_s)
            except Exception as exc:
                print(f"[HARDWARE] Falha ao tocar buzzer: {exc}")
            finally:
                self.parar_buzzer()

    def bip_sucesso(self):
        """Três bipes curtos — senha correta (síncrono, sempre desliga)."""
        self._bipes(N_BIPES_SUCESSO, DURACAO_BIP_SUCESSO_S, PAUSA_ENTRE_BIPES_S)

    def bip_erro(self):
        """Um bip longo — senha inválida."""
        self._bipes(1, DURACAO_BIP_ERRO_S, 0.0)

    def sinalizar_sucesso(self):
        self.acender_sucesso()
        self.bip_sucesso()

    def sinalizar_falha(self):
        self.acender_falha()
        self.bip_erro()

    # ── Encerramento limpo ─────────────────────────────────────────
    def cleanup(self):
        self.apagar_leds()
        self.parar_buzzer()
        if self.buzzer is not None:
            try:
                self.buzzer.close()
            except Exception:
                pass
            self.buzzer = None
        for botao in (
            self.botao_morse,
            self.botao_confirmar,
            self.botao_limpar,
            self.botao_cancelar,
        ):
            try:
                botao.close()
            except Exception:
                pass
        self.rgb.close()
