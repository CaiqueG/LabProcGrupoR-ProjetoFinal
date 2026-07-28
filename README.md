# Sistema de Presença por Código Morse — Raspberry Pi 3

**Grupo R** — Laboratório de Processadores — Escola Politécnica da USP

| Integrante | NUSP |
|---|---|
| Caique Granja Maia | 12555572 |
| João Ricardo Rodrigues Ribeiro | 14582802 |
| Stephanie Pedrazza Grunwald | 11233522 |

Sistema embarcado para controle de presença em sala de aula: cada aluno digita uma senha numérica de 4 dígitos em **código Morse** usando um botão físico. O sistema decodifica, valida contra uma base local, registra a presença com data/hora, sinaliza por LEDs/buzzer/LCD e exibe o resultado em uma interface web acessível pela rede local.

---

## Hardware necessário

| Componente | Pino BCM | Observação |
|---|---|---|
| Botão Morse (entrada principal) | GPIO 26 | Botão S4 da placa Freenove |
| Botão Confirmar | GPIO 18 | Botão externo na protoboard |
| Botão Cancelar | GPIO 23 | Botão externo na protoboard |
| LED Verde | GPIO 17 | LED da placa Freenove |
| LED Vermelho | GPIO 27 | LED externo na protoboard |
| Buzzer passivo | GPIO 12 | Conector Buzzer da placa Freenove |
| Display LCD 1602 (I2C) | SDA=GPIO 2, SCL=GPIO 3 | Conector I2C da placa Freenove |

> LCD e buzzer são opcionais: se não estiverem conectados, o sistema continua funcionando. O LCD cai em modo console e o buzzer é ignorado com aviso no log.

---

## Instalação

```bash
# No Raspberry Pi OS
sudo apt-get update
sudo apt-get install -y python3-pip i2c-tools

# Habilitar barramento I2C (se ainda não estiver ativo)
sudo raspi-config nonint do_i2c 0

# Clonar o repositório e instalar dependências
git clone https://github.com/CaiqueG/LabProcGrupoR-ProjetoFinal.git
cd LabProcGrupoR-ProjetoFinal
pip3 install -r requirements.txt --break-system-packages
```

Verifique se o LCD está visível no barramento (opcional):

```bash
i2cdetect -y 1
```

---

## Como rodar

```bash
python3 src/app.py
```

Acesse a interface web em `http://<ip-do-raspberry>:5000`.  
Para encerrar: `Ctrl+C` — o programa libera os pinos GPIO antes de sair.

---

## Como usar

1. **Digitar a senha**: pressione o botão Morse — toque **curto** (< 0,3s) = ponto `.`, toque **longo** (≥ 0,3s) = traço `-`. Cada dígito é formado por exatamente 5 símbolos. Uma pausa ≥ 1s fecha automaticamente o dígito atual.
2. **Cancelar** a qualquer momento com o botão Cancelar.
3. **Confirmar** após os 4 dígitos: valida a senha, registra a presença e sinaliza o resultado.

### Tabela Morse numérica (ITU-R M.1677)

| Dígito | Código | Dígito | Código |
|---|---|---|---|
| 0 | `----- ` | 5 | `.....` |
| 1 | `.----` | 6 | `-....` |
| 2 | `..---` | 7 | `--...` |
| 3 | `...--` | 8 | `---..` |
| 4 | `....-` | 9 | `----.` |

### Senhas de teste incluídas (`src/data/alunos.json`)

| Senha | Aluno |
|---|---|
| 1234 | Caique Granja Maia |
| 5678 | Joao Ricardo Rodrigues Ribeiro |
| 0192 | Stephanie Pedrazza Grunwald |

Edite `src/data/alunos.json` para cadastrar a turma real.

---

## Rodando os testes (sem hardware)

A lógica de decodificação Morse é testável sem Raspberry Pi:

```bash
python3 -m unittest tests/test_morse_decoder.py -v
```

---

## Documentação

O relatório completo do projeto (motivação, requisitos, arquitetura, testes e conclusões) está em [`docs/relatorio.md`](docs/relatorio.md).
