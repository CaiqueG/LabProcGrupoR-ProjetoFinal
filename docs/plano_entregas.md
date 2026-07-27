# Plano de Entregas Semanais — Sistema de Presença por Código Morse

**Grupo R** — Caique Granja Maia, João Ricardo Rodrigues Ribeiro, Stephanie Pedrazza Grunwald  
**Disciplina:** Laboratório de Processadores  
**Repositório:** [github.com/JohneSs14/LabProcGrupoR](https://github.com/JohneSs14/LabProcGrupoR) *(criar repo público separado)*

---

## Visão Geral

O projeto foi desenvolvido de forma integral, mas as entregas serão organizadas de forma incremental, expondo progressivamente a motivação, os requisitos, a arquitetura, os testes e os resultados. Cada semana culmina em uma **Release no GitHub** e um **PDF entregue no Moodle**.

---

## Semana 1 — Estruturação do Projeto

**Release:** `v0.1.0`  
**Foco:** Motivação, requisitos, arquitetura proposta e organização do repositório.

### Estrutura do repositório a criar

```
ProjetoFinal/
├── src/
│   ├── app.py
│   ├── fsm.py
│   ├── morse_decoder.py
│   ├── hardware.py
│   ├── database.py
│   ├── lcd_driver.py
│   ├── lcd1602_driver.py
│   └── data/
│       └── alunos.json
├── tests/
│   └── test_morse_decoder.py
├── docs/
│   ├── relatorio.md
│   ├── plano_entregas.md        ← este arquivo
│   ├── diagramas/
│   │   ├── arquitetura_fisica.d2
│   │   ├── arquitetura_software.d2
│   │   └── fsm.d2
│   └── figuras/
├── README.md
├── LICENSE                      (GNU GPL v3)
├── .gitignore
└── requirements.txt
```

### Commits desta semana

| Commit | Conteúdo |
|---|---|
| `init: estrutura do repositório e LICENSE` | Pastas `src/`, `docs/`, `tests/`, `.gitignore`, `LICENSE` |
| `feat: módulo morse_decoder com testes unitários` | `src/morse_decoder.py` + `tests/test_morse_decoder.py` |
| `feat: abstração de hardware (botões, LEDs, buzzer)` | `src/hardware.py` |
| `feat: módulo de banco de dados (cadastro e histórico)` | `src/database.py` + `src/data/alunos.json` |
| `feat: driver LCD com fallback para console` | `src/lcd_driver.py` + `src/lcd1602_driver.py` |
| `feat: FSM não-bloqueante do sistema de presença` | `src/fsm.py` |
| `feat: servidor Flask e interface web` | `src/app.py` + `src/templates/` + `src/static/` |
| `docs: relatório inicial — motivação, requisitos e arquitetura` | `docs/relatorio.md` |
| `docs: diagramas de arquitetura (D2)` | `docs/diagramas/*.d2` |

### Conteúdo do `docs/relatorio.md` nesta semana

- [x] Motivação e justificativa
- [x] Objetivos (geral e específicos)
- [x] Requisitos funcionais (RF1–RF5)
- [x] Requisitos não funcionais (RNF1–RNF4)
- [x] Arquitetura proposta (física e software)
- [x] Ferramentas: Python 3, Flask, gpiozero, smbus2, RPi 3
- [x] Metodologia de desenvolvimento
- [ ] Testes planejados *(tabela com casos, sem resultados ainda)*
- [ ] Conclusões *(adiado para semana 4)*

### Checklist de entrega

- [ ] Repositório GitHub público criado
- [ ] Código em `src/`, testes em `tests/`, docs em `docs/`
- [ ] `README.md` com instruções de instalação e execução
- [ ] `LICENSE` (GNU GPL v3)
- [ ] `.gitignore` (Python + Flask)
- [ ] `docs/relatorio.md` com seções de motivação a metodologia
- [ ] Pelo menos 1 diagrama D2 (arquitetura física)
- [ ] Release `v0.1.0` criada no GitHub
- [ ] PDF exportado do relatório e enviado no Moodle

---

## Semana 2 — Avaliação por Pares

**Release:** `v0.2.0`  
**Foco:** Revisão do projeto de outro grupo via GitHub Issues + atualização com resultados dos primeiros testes.

### Atividades

#### A — Revisão do projeto de outro grupo (GitHub Issues)

Abrir Issues no repositório do grupo avaliado abordando:

| Issue sugerida | Aspecto avaliado |
|---|---|
| Requisito ambíguo ou incompleto | Especificação |
| Inconsistência entre requisito e diagrama | Arquitetura |
| Ausência de casos de teste para algum requisito | Testes |
| Sugestão de ferramenta ou biblioteca | Ferramentas |
| Melhoria na organização do repositório | Código |

> **Atenção:** a qualidade importa mais que a quantidade. Abrir Issues superficiais não resulta em nota melhor.

#### B — Atualização do próprio projeto

Executar os testes unitários e registrar os resultados:

```bash
python3 -m unittest tests/test_morse_decoder.py -v
```

Evidências esperadas:
- Print/log da execução dos 6 testes passando
- Identificar se algum teste falhou e documentar a causa

Commits desta semana:

| Commit | Conteúdo |
|---|---|
| `test: execução dos testes unitários — resultados semana 2` | Atualiza `docs/relatorio.md` com evidências |
| `docs: rastreabilidade requisitos ↔ testes` | Tabela RF/RNF → casos de teste |
| `fix: <correções apontadas pelas Issues recebidas>` | Ajustes no código/docs com base na revisão |

### Seções do `docs/relatorio.md` a completar

- [ ] Testes planejados *(expandir com casos de teste para cada RF/RNF)*
- [ ] Rastreabilidade: tabela mapeando RF → caso de teste → resultado
- [ ] Resultados dos testes unitários do `morse_decoder`

### Checklist de entrega

- [ ] Pelo menos 3 Issues abertas no repositório do grupo avaliado
- [ ] `docs/relatorio.md` atualizado com resultados de testes
- [ ] Tabela de rastreabilidade requisitos ↔ testes
- [ ] Release `v0.2.0` criada no GitHub
- [ ] PDF atualizado enviado no Moodle

---

## Semana 3 — Estruturação do Relatório

**Release:** `v0.3.0`  
**Foco:** Diagramas detalhados, evidências de testes com hardware, refinamento geral.

### Atividades

#### A — Diagramas D2 a finalizar

| Diagrama | Arquivo | Conteúdo |
|---|---|---|
| Arquitetura física | `docs/diagramas/arquitetura_fisica.d2` | RPi 3, botões, LEDs, buzzer, LCD, conexões BCM |
| Arquitetura de software | `docs/diagramas/arquitetura_software.d2` | Módulos Python e dependências entre eles |
| Máquina de estados (FSM) | `docs/diagramas/fsm.d2` | IDLE → DIGITANDO → AGUARDANDO → VALIDANDO |
| Diagrama de sequência | `docs/diagramas/sequencia.d2` | Fluxo de um registro de presença bem-sucedido |

#### B — Testes com hardware real

Executar no Raspberry Pi e registrar evidências (logs ou fotos):

| Caso de teste | Procedimento | Evidência esperada |
|---|---|---|
| CT-RF1: dígito Morse válido (ex.: "1" = `.----`) | Pressionar 1 curto + 4 longos, aguardar 1s | LCD exibe "Senha: 1___" |
| CT-RF1: dígito Morse inválido (5 símbolos sem mapeamento) | Digitar `.-.-.' | LCD exibe "Sequência inválida" |
| CT-RF2: senha válida | Digitar senha de aluno cadastrado + confirmar | LED verde acende, buzzer toca melodia, presença registrada em CSV |
| CT-RF2: senha inválida | Digitar senha não cadastrada + confirmar | LED vermelho acende, buzzer toca bipe de erro |
| CT-RF3: cancelar | Pressionar botão cancelar durante digitação | Buffer zerado, LCD volta a "Digite a senha em Morse" |
| CT-RNF1: tempo de resposta web | Medir com DevTools o tempo de atualização do /status | < 1s |
| CT-RNF2: debounce | Pressionar botão muito rápido repetidamente | Apenas 1 evento registrado |
| CT-RNF3: non-blocking | Digitar enquanto Flask serve /status | Nenhum travamento observado |
| CT-RNF4: LCD ausente | Desconectar LCD e rodar | Sistema continua, mensagens no console |

Commits desta semana:

| Commit | Conteúdo |
|---|---|
| `docs: diagramas D2 finalizados (FSM, sequência, arquitetura)` | Arquivos `.d2` e figuras exportadas |
| `docs: evidências de testes com hardware — semana 3` | Logs, fotos ou prints no relatório |
| `docs: relatório estruturado completo (exceto conclusões)` | Todas as seções preenchidas |

### Seções do `docs/relatorio.md` a completar

- [ ] Diagramas inseridos (figuras exportadas do D2)
- [ ] Resultados dos testes com hardware (CT-RF1 a CT-RNF4)
- [ ] Seção de ferramentas detalhada (versões das bibliotecas)

### Checklist de entrega

- [ ] Todos os diagramas D2 criados e exportados como PNG/SVG
- [ ] Evidências dos testes com hardware registradas no relatório
- [ ] Release `v0.3.0` criada no GitHub
- [ ] PDF atualizado enviado no Moodle

---

## Semana 4 — Entrega Final e Apresentação

**Release:** `v1.0.0`  
**Foco:** Relatório completo, release final e apresentação de até 10 minutos.

### Relatório final — seções a completar

- [ ] **Conclusões:** os objetivos foram cumpridos? Todos os requisitos satisfeitos? Dificuldades encontradas (conflito RPi.GPIO/gpiozero da Aula 10, pinos UART GPIO14/15, etc.). Direções futuras.
- [ ] Revisão geral de referências ABNT (citações diretas e indiretas)
- [ ] Verificar limite de 20 páginas (excluindo referências e anexos)

### Commits desta semana

| Commit | Conteúdo |
|---|---|
| `docs: conclusões e lições aprendidas` | Seção final do relatório |
| `docs: referências ABNT revisadas` | Formatação correta |
| `chore: limpeza final — remover arquivos temporários` | `.gitignore`, `__pycache__`, etc. |
| `release: v1.0.0` | Tag da entrega final |

### Estrutura da apresentação (10 minutos)

| Tempo | Conteúdo |
|---|---|
| 0–1 min | Motivação: por que um sistema de presença por Morse? |
| 1–3 min | Solução proposta e arquitetura do sistema |
| 3–6 min | Demonstração ao vivo (digitar senha em Morse, ver resultado no LCD e na web) |
| 6–8 min | Resultados dos testes e rastreabilidade com requisitos |
| 8–10 min | Dificuldades encontradas e trabalhos futuros |

> **Ponto extra:** apresentação integralmente em inglês.

### Checklist de entrega final

- [ ] `src/` com código final limpo e documentado (docstrings Google style)
- [ ] `tests/` com testes unitários passando
- [ ] `docs/relatorio.md` completo (todas as seções)
- [ ] `docs/diagramas/` com todos os arquivos D2 e figuras exportadas
- [ ] `README.md` atualizado com instrução de como rodar os testes
- [ ] Apenas branch `main` no repositório
- [ ] Release `v1.0.0` criada no GitHub com o PDF anexado
- [ ] PDF final enviado no Moodle
- [ ] Apresentação preparada

---

## Requisitos Funcionais e Não Funcionais (referência rápida)

### Funcionais

| ID | Descrição |
|---|---|
| RF1 | O sistema deve decodificar dígitos (0–9) em código Morse numérico ITU (5 símbolos/dígito), fechando automaticamente o dígito após pausa ≥ 1s ou por botão Confirmar |
| RF2 | O sistema deve validar uma senha de 4 dígitos contra um cadastro local e registrar a presença (nome, data, hora) em arquivo CSV se a senha for válida |
| RF3 | O sistema deve permitir cancelamento a qualquer momento, zerando o buffer de entrada |
| RF4 | O sistema deve fornecer feedback multimodal: LED verde/vermelho, bipe no buzzer e mensagem no LCD |
| RF5 | O sistema deve expor uma interface web acessível na rede local com status em tempo real e histórico das últimas 10 presenças |

### Não Funcionais

| ID | Descrição |
|---|---|
| RNF1 | Tempo de resposta da interface web < 1s (polling a cada 1s via AJAX) |
| RNF2 | Debounce de 50ms nos botões; sequência Morse inválida descartada sem travar o sistema |
| RNF3 | Sistema não-bloqueante: botões via callbacks (gpiozero), buzzer em thread separada, Flask em thread separada da FSM |
| RNF4 | Resiliência de hardware: ausência de LCD ou buzzer não impede o funcionamento do sistema |

---

## Rastreabilidade Requisitos ↔ Testes

| Requisito | Caso de Teste | Tipo | Status |
|---|---|---|---|
| RF1 | CT-RF1a: dígito "1" (.----) → senha "1___" | Hardware | Semana 3 |
| RF1 | CT-RF1b: sequência inválida → "Sequência inválida" | Hardware | Semana 3 |
| RF1 | CT-RF1c: 10 dígitos 0–9 decodificados corretamente | Unitário | Semana 1 ✅ |
| RF1 | CT-RF1d: senha de 4 dígitos completa | Unitário | Semana 1 ✅ |
| RF1 | CT-RF1e: timeout não fecha antes do prazo | Unitário | Semana 1 ✅ |
| RF2 | CT-RF2a: senha válida → presença registrada no CSV | Hardware | Semana 3 |
| RF2 | CT-RF2b: senha inválida → LED vermelho + bipe erro | Hardware | Semana 3 |
| RF3 | CT-RF3: cancelar limpa buffer e senha | Unitário | Semana 1 ✅ |
| RF3 | CT-RF3b: botão cancelar durante digitação | Hardware | Semana 3 |
| RF4 | CT-RF4: LED verde + melodia no sucesso | Hardware | Semana 3 |
| RF5 | CT-RF5: /status retorna JSON com campos corretos | Hardware | Semana 3 |
| RNF1 | CT-RNF1: latência /status < 1s | Hardware | Semana 3 |
| RNF2 | CT-RNF2: sequência incompleta → ERRO sem travar | Unitário | Semana 1 ✅ |
| RNF2 | CT-RNF2b: toques extras após senha completa ignorados | Unitário | Semana 1 ✅ |
| RNF3 | CT-RNF3: digitação simultânea ao Flask | Hardware | Semana 3 |
| RNF4 | CT-RNF4: sistema funciona sem LCD conectado | Hardware | Semana 3 |
