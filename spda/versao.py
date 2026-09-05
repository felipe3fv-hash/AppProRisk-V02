"""Identificação do motor de cálculo.

A versão é impressa em todo laudo emitido. Ela existe para que um laudo
questionado anos depois possa ser reproduzido exatamente com o mesmo motor.
Regra: qualquer alteração em `tabelas.py`, `probabilidades.py`, `perdas.py`,
`eventos.py` ou `analise.py` OBRIGA incremento de MINOR (ou MAJOR).
"""

VERSAO_MOTOR = "2.0.0"
NORMA_APLICADA = "ABNT NBR 5419-2:2026 (2ª edição, 10.03.2026)"
NOME_PRODUTO = "SPDA Risk Pro"

__all__ = ["VERSAO_MOTOR", "NORMA_APLICADA", "NOME_PRODUTO"]
