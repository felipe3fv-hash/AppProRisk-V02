"""Smoke test da interface: o script roda de ponta a ponta sem exceção.

Usa o AppTest do próprio Streamlit — nenhum navegador envolvido. Garante que
uma alteração no modelo não quebre silenciosamente a tela.
"""

import time

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")
AppTest = st_testing.AppTest

from spda.modelo import (  # noqa: E402
    Estrutura,
    Identificacao,
    LinhaEletrica,
    Projeto,
    SistemaInterno,
    Trecho,
    ZonaEstudo,
)


def _app(projeto=None):
    at = AppTest.from_file("app.py", default_timeout=90)
    at.session_state["usuario"] = "teste"
    at.session_state["inicio_sessao"] = time.time()
    if projeto is not None:
        at.session_state["projeto"] = projeto
    return at.run()


def _projeto_completo() -> Projeto:
    return Projeto(
        identificacao=Identificacao(obra="Teste", responsavel_tecnico="Eng.", crea="PE-1"),
        municipio="Petrolina", uf="PE", n_g=6.0, pessoas_total=20.0,
        p_b_chave="III", p_eb_chave="II", sistema_critico=True,
        estrutura=Estrutura(comprimento_m=40, largura_m=20, altura_m=10),
        linhas=[LinhaEletrica(id_linha="L1", trechos=[Trecho(comprimento_m=300)])],
        zonas=[ZonaEstudo(
            id_zona="Z1", ocupacao="comercial", pessoas_na_zona=20.0,
            sistemas_internos=[SistemaInterno(id_sistema="S1", uw_kv=2.5, ids_linhas=["L1"])],
        )],
    )


def test_app_carrega_sem_excecao_com_projeto_vazio():
    at = _app()
    assert not at.exception
    assert any("Análise de risco" in h.value for h in at.title)


def test_app_bloqueia_laudo_com_projeto_incompleto():
    at = _app()
    assert not at.exception
    assert any("impedem a emissão" in e.value for e in at.error)


def test_app_calcula_com_projeto_valido():
    at = _app(_projeto_completo())
    assert not at.exception
    rotulos = " ".join(m.label for m in at.metric)
    assert "R1" in rotulos and "R3" in rotulos and "R4" in rotulos


def test_app_nao_bloqueia_projeto_valido():
    at = _app(_projeto_completo())
    assert not at.exception
    assert not any("impedem a emissão" in e.value for e in at.error)


def test_app_exige_login_sem_sessao():
    at = AppTest.from_file("app.py", default_timeout=90).run()
    assert not at.exception
    # O st.stop() do login impede que o título da aplicação seja renderizado.
    assert not at.title


def test_tela_de_primeiro_acesso_sem_usuarios_configurados():
    """Sem segredos, o app oferece a geração da credencial em vez de travar."""
    at = AppTest.from_file("app.py", default_timeout=90)
    at.secrets["usuarios"] = {}
    at = at.run()
    assert not at.exception
    assert any("Primeiro acesso" in w.value for w in at.warning)


def test_tela_de_primeiro_acesso_gera_credencial_valida():
    from spda.auth import verificar

    at = AppTest.from_file("app.py", default_timeout=90)
    at.secrets["usuarios"] = {}
    at = at.run()
    at.text_input[0].set_value("mariz")
    at.text_input[1].set_value("uma-senha-bem-longa")
    at.text_input[2].set_value("uma-senha-bem-longa")
    at = at.button[0].click().run()
    assert not at.exception
    bloco = "\n".join(c.value for c in at.code)
    assert "[usuarios]" in bloco and "pbkdf2_sha256$" in bloco
    linha_hash = bloco.split('"')[1]
    assert verificar("uma-senha-bem-longa", linha_hash)
    assert not verificar("outra-senha-qualquer", linha_hash)


def test_primeiro_acesso_recusa_senha_curta_e_senhas_diferentes():
    at = AppTest.from_file("app.py", default_timeout=90)
    at.secrets["usuarios"] = {}
    at = at.run()
    at.text_input[1].set_value("curta")
    at.text_input[2].set_value("curta")
    at = at.button[0].click().run()
    assert any("10 caracteres" in e.value for e in at.error)

    at = AppTest.from_file("app.py", default_timeout=90)
    at.secrets["usuarios"] = {}
    at = at.run()
    at.text_input[1].set_value("uma-senha-bem-longa")
    at.text_input[2].set_value("outra-senha-bem-longa")
    at = at.button[0].click().run()
    assert any("não são iguais" in e.value for e in at.error)


def test_login_normal_reaparece_quando_ha_usuarios():
    from spda.auth import gerar_hash

    at = AppTest.from_file("app.py", default_timeout=90)
    at.secrets["usuarios"] = {"mariz": gerar_hash("uma-senha-bem-longa")}
    at = at.run()
    assert not at.exception
    assert not any("Primeiro acesso" in w.value for w in at.warning)
