import os
import html
import streamlit as st

from clash_api import buscar_jogador, liberar_busca, normalizar_tag
from card_roles import ROLE_LABELS, resumo_de_roles
from counter_engine import cobertura_respostas, classificar_ameacas, respostas_para_ameaca, identificar_vulnerabilidades


# ============================================================
# CONFIGURAÇÃO DO PROXY
# ============================================================

def get_config(nome, padrao=None):
    """
    Procura primeiro em st.secrets e depois nas variáveis de ambiente.
    """

    try:
        if nome in st.secrets:
            return st.secrets[nome]
    except Exception:
        pass

    return os.getenv(nome, padrao)


PROXY_API_URL = get_config("PROXY_API_URL")
PROXY_SECRET = get_config("PROXY_SECRET")


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        opacity: 0.70;
        margin-bottom: 2rem;
    }

    .player-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .player-name {
        text-align: center;
        font-size: 1.7rem;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .player-tag {
        text-align: center;
        opacity: 0.65;
        margin-bottom: 12px;
    }

    .deck-title {
        font-size: 1.3rem;
        font-weight: 700;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 12px;
    }

    .card-name {
        font-size: 0.78rem;
        text-align: center;
        font-weight: 600;
        min-height: 35px;
    }

    .card-level {
        text-align: center;
        font-size: 0.72rem;
        opacity: .75;
    }

    .comparison-title {
        text-align:center;
        font-weight:800;
        font-size:1.4rem;
        margin-top:25px;
        margin-bottom:15px;
    }

    .matchup-board {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 16px;
        overflow: hidden;
        margin: 10px 0 18px 0;
    }

    .matchup-head,
    .matchup-row {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(120px, .8fr) minmax(0, 1fr);
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
    }

    .matchup-head {
        font-weight: 800;
        background: rgba(128,128,128,0.08);
        font-size: 1rem;
    }

    .matchup-row {
        border-top: 1px solid rgba(128,128,128,0.14);
    }

    .matchup-value-left {
        text-align: left;
        font-weight: 800;
        font-size: 1.05rem;
    }

    .matchup-label {
        text-align: center;
        opacity: .72;
        font-size: .82rem;
        font-weight: 700;
    }

    .matchup-value-right {
        text-align: right;
        font-weight: 800;
        font-size: 1.05rem;
    }

    .matchup-note {
        text-align: center;
        opacity: .68;
        font-size: .78rem;
        margin-top: -8px;
        margin-bottom: 14px;
    }


    .profile-stats-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin: 10px 0 16px 0;
    }

    .profile-stat {
        border: 1px solid rgba(128,128,128,0.18);
        border-radius: 12px;
        padding: 10px 12px;
        min-width: 0;
    }

    .profile-stat-label {
        font-size: .78rem;
        opacity: .72;
        font-weight: 700;
        margin-bottom: 3px;
    }

    .profile-stat-value {
        font-size: 1.35rem;
        font-weight: 800;
        line-height: 1.15;
    }

    .profile-details {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin: 8px 0 6px 0;
    }

    .profile-detail {
        border: 1px solid rgba(128,128,128,0.16);
        border-radius: 12px;
        padding: 10px 12px;
        font-size: 1rem;
        font-weight: 700;
        line-height: 1.25;
    }

    .deck-grid {
        display: grid;
        grid-template-columns: repeat(8, minmax(0, 1fr));
        gap: 10px;
        align-items: start;
        margin-top: 10px;
    }

    .deck-card {
        text-align: center;
        min-width: 0;
    }

    .deck-card a {
        display: block;
        text-decoration: none;
    }

    .deck-card img {
        width: 100%;
        max-width: 118px;
        height: auto;
        display: block;
        margin: 0 auto;
        border-radius: 10px;
    }

    .deck-card-name {
        margin-top: 5px;
        font-size: .72rem;
        font-weight: 700;
        line-height: 1.15;
        overflow-wrap: anywhere;
    }

    .deck-card-level {
        margin-top: 2px;
        font-size: .66rem;
        opacity: .72;
        line-height: 1.1;
    }

    .deck-zoom-note {
        text-align: center;
        font-size: .72rem;
        opacity: .62;
        margin: 8px 0 4px 0;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-left: .8rem;
            padding-right: .8rem;
        }

        .main-title {
            font-size: 1.75rem;
        }

        .subtitle {
            font-size: .9rem;
            margin-bottom: 1rem;
        }

        .matchup-board {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }

        .matchup-head,
        .matchup-row {
            grid-template-columns: minmax(150px, 1fr) 92px minmax(150px, 1fr);
            gap: 6px;
            padding: 8px 8px;
            min-width: 430px;
        }

        .matchup-head {
            font-size: .88rem;
        }

        .matchup-value-left,
        .matchup-value-right {
            font-size: .92rem;
        }

        .matchup-label {
            font-size: .69rem;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.55rem;
        }

        .profile-stats-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 8px;
        }

        .profile-stat {
            padding: 9px 10px;
        }

        .profile-stat-label {
            font-size: .72rem;
        }

        .profile-stat-value {
            font-size: 1.25rem;
        }

        .profile-details {
            grid-template-columns: 1fr;
            gap: 8px;
        }

        .profile-detail {
            font-size: 1.05rem;
            padding: 10px 12px;
        }

        .deck-grid {
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 8px 6px;
        }

        .deck-card img {
            width: 100%;
            max-width: 82px;
            border-radius: 8px;
        }

        .deck-card-name {
            font-size: .64rem;
        }

        .deck-card-level {
            font-size: .60rem;
        }

        div[data-testid="stDataFrame"] {
            overflow-x: auto;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def obter_nome_arena(jogador):
    arena = jogador.get("arena")

    if isinstance(arena, dict):
        return arena.get("name", "Não informado")

    return "Não informado"


def obter_nome_cla(jogador):
    cla = jogador.get("clan")

    if isinstance(cla, dict):
        return cla.get("name", "Sem clã")

    return "Sem clã"


def calcular_taxa_vitoria(jogador):
    wins = jogador.get("wins", 0) or 0
    losses = jogador.get("losses", 0) or 0

    total = wins + losses

    if total == 0:
        return 0

    return (wins / total) * 100


def calcular_elixir_medio(deck):
    if not deck:
        return 0

    custos = []

    for carta in deck:
        custo = carta.get("elixirCost")

        if isinstance(custo, (int, float)):
            custos.append(custo)

    if not custos:
        return 0

    return sum(custos) / len(custos)


def obter_custos_deck(deck):
    custos = []

    for carta in deck or []:
        custo = carta.get("elixirCost")

        if isinstance(custo, (int, float)):
            custos.append(custo)

    return custos


def analisar_deck(deck):
    """
    Métricas calculadas apenas com os dados oficiais retornados no deck.
    """

    custos = obter_custos_deck(deck)

    if not custos:
        return {
            "elixir_medio": 0,
            "ciclo_4": 0,
            "menor_custo": 0,
            "maior_custo": 0,
            "cartas_leves": 0,
            "cartas_pesadas": 0,
        }

    custos_ordenados = sorted(custos)

    return {
        "elixir_medio": sum(custos) / len(custos),
        "ciclo_4": sum(custos_ordenados[:4]),
        "menor_custo": min(custos),
        "maior_custo": max(custos),
        "cartas_leves": sum(1 for custo in custos if custo <= 3),
        "cartas_pesadas": sum(1 for custo in custos if custo >= 5),
    }


def cartas_em_comum(deck1, deck2):
    nomes1 = {
        carta.get("name")
        for carta in deck1 or []
        if carta.get("name")
    }

    nomes2 = {
        carta.get("name")
        for carta in deck2 or []
        if carta.get("name")
    }

    return sorted(nomes1.intersection(nomes2))


def mostrar_snapshot_matchup(j1, j2):
    """
    Quadro compacto para leitura rápida do confronto, pensado também para celular.
    """

    deck1 = j1.get("currentDeck", [])
    deck2 = j2.get("currentDeck", [])

    nome1 = html.escape(str(j1.get("name", "Jogador 1")))
    nome2 = html.escape(str(j2.get("name", "Jogador 2")))

    analise1 = analisar_deck(deck1)
    analise2 = analisar_deck(deck2)

    cobertura1 = cobertura_respostas(deck1, deck2)
    cobertura2 = cobertura_respostas(deck2, deck1)

    vulnerabilidades1 = identificar_vulnerabilidades(deck1, deck2)
    vulnerabilidades2 = identificar_vulnerabilidades(deck2, deck1)

    roles1 = resumo_de_roles(deck1)
    roles2 = resumo_de_roles(deck2)

    linhas = [
        (
            numero(j1.get("trophies", 0)),
            "🏆 Troféus",
            numero(j2.get("trophies", 0))
        ),
        (
            f"{calcular_taxa_vitoria(j1):.1f}%",
            "📊 Winrate",
            f"{calcular_taxa_vitoria(j2):.1f}%"
        ),
        (
            f"{analise1['elixir_medio']:.1f}",
            "💧 Elixir médio",
            f"{analise2['elixir_medio']:.1f}"
        ),
        (
            f"{analise1['ciclo_4']:.0f}",
            "🔄 Ciclo 4",
            f"{analise2['ciclo_4']:.0f}"
        ),
        (
            f"{cobertura1['cobertas']}/{cobertura1['total']}",
            "🛡️ Ameaças cobertas",
            f"{cobertura2['cobertas']}/{cobertura2['total']}"
        ),
        (
            str(len(vulnerabilidades1)),
            "⚠️ Vulnerabilidades",
            str(len(vulnerabilidades2))
        ),
        (
            f"{roles1['cobertura']:.0f}%",
            "🧩 Base classificada",
            f"{roles2['cobertura']:.0f}%"
        ),
    ]

    html_linhas = "".join(
        f"""
        <div class="matchup-row">
            <div class="matchup-value-left">{html.escape(str(valor1))}</div>
            <div class="matchup-label">{rotulo}</div>
            <div class="matchup-value-right">{html.escape(str(valor2))}</div>
        </div>
        """
        for valor1, rotulo, valor2 in linhas
    )

    st.markdown(
        f"""
        <div class="matchup-board">
            <div class="matchup-head">
                <div>{nome1}</div>
                <div style="text-align:center;">VS</div>
                <div style="text-align:right;">{nome2}</div>
            </div>
            {html_linhas}
        </div>
        <div class="matchup-note">
            Visão rápida; abra as abas abaixo para ver a explicação de cada indicador.
        </div>
        """,
        unsafe_allow_html=True
    )


def mostrar_funcoes_decks(j1, j2):
    deck1 = j1.get("currentDeck", [])
    deck2 = j2.get("currentDeck", [])

    nome1 = j1.get("name", "Jogador 1")
    nome2 = j2.get("name", "Jogador 2")

    resumo1 = resumo_de_roles(deck1)
    resumo2 = resumo_de_roles(deck2)

    st.markdown(
        '<div class="comparison-title">🧩 Funções dos Decks</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Classificação tática inicial baseada em uma base explícita de funções das cartas."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {nome1}")
        st.progress(min(resumo1["cobertura"] / 100, 1.0))
        st.caption(
            f"Cobertura da base: {resumo1['classificadas']}/{resumo1['total']} cartas "
            f"({resumo1['cobertura']:.0f}%)"
        )

        if resumo1["contagem"]:
            for role, quantidade in sorted(
                resumo1["contagem"].items(),
                key=lambda item: (-item[1], ROLE_LABELS.get(item[0], item[0]))
            ):
                st.write(f"{ROLE_LABELS.get(role, role)}: **{quantidade}**")

        if resumo1["nao_classificadas"]:
            st.warning(
                "Não classificadas: "
                + ", ".join(resumo1["nao_classificadas"])
            )

    with col2:
        st.markdown(f"### {nome2}")
        st.progress(min(resumo2["cobertura"] / 100, 1.0))
        st.caption(
            f"Cobertura da base: {resumo2['classificadas']}/{resumo2['total']} cartas "
            f"({resumo2['cobertura']:.0f}%)"
        )

        if resumo2["contagem"]:
            for role, quantidade in sorted(
                resumo2["contagem"].items(),
                key=lambda item: (-item[1], ROLE_LABELS.get(item[0], item[0]))
            ):
                st.write(f"{ROLE_LABELS.get(role, role)}: **{quantidade}**")

        if resumo2["nao_classificadas"]:
            st.warning(
                "Não classificadas: "
                + ", ".join(resumo2["nao_classificadas"])
            )

    roles_chave = [
        "win_condition",
        "anti_air",
        "splash",
        "building",
        "reset",
        "small_spell",
        "big_spell",
        "swarm",
        "tank_killer",
    ]

    st.markdown("#### ⚔️ Comparação de cobertura tática")

    for role in roles_chave:
        q1 = resumo1["contagem"].get(role, 0)
        q2 = resumo2["contagem"].get(role, 0)

        esquerda, centro, direita = st.columns([2, 1, 2])

        with esquerda:
            st.metric(ROLE_LABELS.get(role, role), q1)

        with centro:
            st.markdown(
                "<div style='text-align:center; padding-top:32px;'>↔️</div>",
                unsafe_allow_html=True
            )

        with direita:
            st.metric(ROLE_LABELS.get(role, role), q2)

    with st.expander("ℹ️ Sobre esta classificação"):
        st.markdown(
            """
Esta é uma **base inicial e auditável**. Cada carta possui uma ou mais funções táticas
definidas explicitamente. Quando uma carta ainda não está cadastrada, o sistema mostra
isso em vez de adivinhar.

A próxima etapa será usar essas funções para montar regras de interação, por exemplo:
**anti-aéreo vs unidade aérea**, **small spell vs swarm**, **reset vs inferno** e
**building vs building-target**, formando a base do analisador de counters.
            """
        )


def gerar_orientacoes_estrategicas(deck_proprio, deck_adversario, nome_adversario):
    """
    Gera orientações curtas a partir das heurísticas já existentes.
    Não prevê resultado de partida e não substitui leitura de ciclo/timing.
    """

    orientacoes = []

    vulnerabilidades = identificar_vulnerabilidades(
        deck_proprio,
        deck_adversario
    )

    roles_proprio = resumo_de_roles(deck_proprio)["contagem"]
    roles_adversario = resumo_de_roles(deck_adversario)["contagem"]

    analise_propria = analisar_deck(deck_proprio)
    analise_adversaria = analisar_deck(deck_adversario)

    # 1) Vulnerabilidades altas e moderadas
    for item in vulnerabilidades:
        if item["level"] == "alta":
            orientacoes.append(
                {
                    "tipo": "erro",
                    "titulo": f"Priorize {item['threat']}",
                    "texto": (
                        "A base atual não encontrou uma resposta natural no seu deck "
                        f"para {item['threat']} de {nome_adversario}."
                    ),
                }
            )

        elif item["responses"]:
            resposta = item["responses"][0]
            orientacoes.append(
                {
                    "tipo": "aviso",
                    "titulo": f"Preserve {resposta['defender']}",
                    "texto": (
                        f"Ela é a única resposta natural mapeada contra "
                        f"{item['threat']} neste confronto."
                    ),
                }
            )

    # 2) Cobertura aérea
    anti_air = roles_proprio.get("anti_air", 0)
    air_adv = roles_adversario.get("air", 0)

    if air_adv > 0 and anti_air <= 1:
        orientacoes.append(
            {
                "tipo": "aviso",
                "titulo": "Cobertura aérea curta",
                "texto": (
                    f"O adversário tem {air_adv} carta(s) aérea(s) classificada(s), "
                    f"enquanto seu deck tem {anti_air} resposta(s) anti-aérea(s) mapeada(s)."
                ),
            }
        )

    # 3) Enxames
    swarm_adv = roles_adversario.get("swarm", 0)
    resposta_swarm = (
        roles_proprio.get("splash", 0)
        + roles_proprio.get("small_spell", 0)
    )

    if swarm_adv > 0 and resposta_swarm <= 1:
        orientacoes.append(
            {
                "tipo": "aviso",
                "titulo": "Pouca cobertura contra enxames",
                "texto": (
                    f"{nome_adversario} tem {swarm_adv} carta(s) de enxame classificada(s) "
                    "e seu deck possui poucas respostas de splash/feitiço leve."
                ),
            }
        )

    # 4) Tanques
    tanks_adv = roles_adversario.get("tank", 0)
    tank_killers = roles_proprio.get("tank_killer", 0)

    if tanks_adv > 0 and tank_killers == 0:
        orientacoes.append(
            {
                "tipo": "aviso",
                "titulo": "Sem mata-tanque dedicado",
                "texto": (
                    f"{nome_adversario} possui {tanks_adv} tanque(s) classificado(s) "
                    "e seu deck não tem mata-tanque mapeado."
                ),
            }
        )

    # 5) Ciclo / rotação
    diferenca_ciclo = (
        analise_adversaria["ciclo_4"]
        - analise_propria["ciclo_4"]
    )

    if diferenca_ciclo >= 2:
        orientacoes.append(
            {
                "tipo": "info",
                "titulo": "Rotação estrutural mais barata",
                "texto": (
                    f"Suas 4 cartas mais baratas somam {analise_propria['ciclo_4']:.0f} "
                    f"de elixir contra {analise_adversaria['ciclo_4']:.0f} do adversário."
                ),
            }
        )
    elif diferenca_ciclo <= -2:
        orientacoes.append(
            {
                "tipo": "info",
                "titulo": "Adversário tem rotação estrutural mais barata",
                "texto": (
                    f"As 4 cartas mais baratas de {nome_adversario} somam "
                    f"{analise_adversaria['ciclo_4']:.0f} de elixir contra "
                    f"{analise_propria['ciclo_4']:.0f} do seu deck."
                ),
            }
        )

    # Remove duplicações de títulos e limita o resumo.
    unicas = []
    titulos = set()

    prioridade = {
        "erro": 0,
        "aviso": 1,
        "info": 2,
    }

    for item in sorted(
        orientacoes,
        key=lambda x: prioridade.get(x["tipo"], 9)
    ):
        if item["titulo"] in titulos:
            continue

        titulos.add(item["titulo"])
        unicas.append(item)

    if not unicas:
        unicas.append(
            {
                "tipo": "sucesso",
                "titulo": "Sem alerta estrutural relevante",
                "texto": (
                    "Com a base atual, não apareceu uma vulnerabilidade forte o bastante "
                    "para virar orientação prioritária."
                ),
            }
        )

    return unicas[:4]


def mostrar_resumo_estrategico(j1, j2):
    deck1 = j1.get("currentDeck", [])
    deck2 = j2.get("currentDeck", [])

    nome1 = j1.get("name", "Jogador 1")
    nome2 = j2.get("name", "Jogador 2")

    orientacoes1 = gerar_orientacoes_estrategicas(
        deck1,
        deck2,
        nome2
    )

    orientacoes2 = gerar_orientacoes_estrategicas(
        deck2,
        deck1,
        nome1
    )

    st.markdown(
        '<div class="comparison-title">🧭 Resumo Estratégico do Confronto</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Síntese prática das análises estruturais do matchup. "
        "Não é previsão de vitória."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {nome1}")

        for item in orientacoes1:
            mensagem = f"**{item['titulo']}** — {item['texto']}"

            if item["tipo"] == "erro":
                st.error(mensagem)
            elif item["tipo"] == "aviso":
                st.warning(mensagem)
            elif item["tipo"] == "sucesso":
                st.success(mensagem)
            else:
                st.info(mensagem)

    with col2:
        st.markdown(f"### {nome2}")

        for item in orientacoes2:
            mensagem = f"**{item['titulo']}** — {item['texto']}"

            if item["tipo"] == "erro":
                st.error(mensagem)
            elif item["tipo"] == "aviso":
                st.warning(mensagem)
            elif item["tipo"] == "sucesso":
                st.success(mensagem)
            else:
                st.info(mensagem)

    with st.expander("ℹ️ Como este resumo é montado?"):
        st.markdown(
            """
O resumo combina as regras que já existem no app:

- vulnerabilidades sem resposta ou com resposta única;
- cobertura anti-aérea;
- cobertura contra enxames;
- presença de mata-tanque;
- custo estrutural das quatro cartas mais baratas.

As frases são geradas por **regras determinísticas**, não por um modelo que inventa
conselhos livremente. Conforme ampliarmos a base de cartas e interações, o resumo
também ficará mais preciso.
            """
        )


def mostrar_vulnerabilidades_matchup(j1, j2):
    deck1 = j1.get("currentDeck", [])
    deck2 = j2.get("currentDeck", [])

    nome1 = j1.get("name", "Jogador 1")
    nome2 = j2.get("name", "Jogador 2")

    vulnerabilidades1 = identificar_vulnerabilidades(
        deck1,
        deck2
    )

    vulnerabilidades2 = identificar_vulnerabilidades(
        deck2,
        deck1
    )

    st.markdown(
        '<div class="comparison-title">⚠️ Vulnerabilidades do Matchup</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Mostra ameaças adversárias para as quais o deck tem poucas ou nenhuma "
        "resposta natural mapeada."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {nome1}")

        if not vulnerabilidades1:
            st.success(
                "Nenhuma vulnerabilidade relevante foi detectada com a base atual."
            )

        for item in vulnerabilidades1:
            if item["level"] == "alta":
                st.error(
                    f"🔴 {item['threat']} — nenhuma resposta natural mapeada"
                )
            else:
                st.warning(
                    f"🟠 {item['threat']} — apenas 1 resposta natural mapeada"
                )

                if item["responses"]:
                    resposta = item["responses"][0]
                    st.caption(
                        f"Resposta disponível: {resposta['defender']} — "
                        f"{resposta['label']}"
                    )

    with col2:
        st.markdown(f"### {nome2}")

        if not vulnerabilidades2:
            st.success(
                "Nenhuma vulnerabilidade relevante foi detectada com a base atual."
            )

        for item in vulnerabilidades2:
            if item["level"] == "alta":
                st.error(
                    f"🔴 {item['threat']} — nenhuma resposta natural mapeada"
                )
            else:
                st.warning(
                    f"🟠 {item['threat']} — apenas 1 resposta natural mapeada"
                )

                if item["responses"]:
                    resposta = item["responses"][0]
                    st.caption(
                        f"Resposta disponível: {resposta['defender']} — "
                        f"{resposta['label']}"
                    )

    with st.expander("ℹ️ Como esta seção funciona?"):
        st.markdown(
            """
O sistema considera as principais ameaças do deck adversário e verifica quantas
**respostas naturais** existem no seu deck:

- 🔴 **Alta vulnerabilidade:** nenhuma resposta natural mapeada;
- 🟠 **Vulnerabilidade moderada:** apenas uma resposta natural mapeada;
- quando existem **duas ou mais respostas**, a ameaça não aparece nesta lista.

Isso é uma **heurística de matchup**, não uma previsão de vitória. Interações reais
dependem de nível, evolução, posicionamento, timing, suporte e habilidade do jogador.
            """
        )


def mostrar_principais_ameacas(j1, j2):
    deck1 = j1.get("currentDeck", [])
    deck2 = j2.get("currentDeck", [])

    nome1 = j1.get("name", "Jogador 1")
    nome2 = j2.get("name", "Jogador 2")

    ameacas1 = classificar_ameacas(deck1)[:4]
    ameacas2 = classificar_ameacas(deck2)[:4]

    st.markdown(
        '<div class="comparison-title">🚨 Principais Ameaças</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Prioridade heurística das cartas ofensivas/estratégicas do deck e "
        "as respostas naturais encontradas no deck adversário."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {nome1}")

        if not ameacas1:
            st.caption("Nenhuma ameaça classificada com a base atual.")

        for ameaca in ameacas1:
            st.markdown(f"**{ameaca['name']}**")

            respostas = respostas_para_ameaca(
                deck2,
                ameaca["name"]
            )

            if respostas:
                st.caption(f"Respostas de {nome2}:")
                for resposta in respostas[:3]:
                    st.write(
                        f"• {resposta['defender']} — {resposta['label']}"
                    )
            else:
                st.warning(
                    f"Nenhuma resposta natural mapeada no deck de {nome2}."
                )

    with col2:
        st.markdown(f"### {nome2}")

        if not ameacas2:
            st.caption("Nenhuma ameaça classificada com a base atual.")

        for ameaca in ameacas2:
            st.markdown(f"**{ameaca['name']}**")

            respostas = respostas_para_ameaca(
                deck1,
                ameaca["name"]
            )

            if respostas:
                st.caption(f"Respostas de {nome1}:")
                for resposta in respostas[:3]:
                    st.write(
                        f"• {resposta['defender']} — {resposta['label']}"
                    )
            else:
                st.warning(
                    f"Nenhuma resposta natural mapeada no deck de {nome1}."
                )

    with st.expander("ℹ️ Como as ameaças são priorizadas?"):
        st.markdown(
            """
A prioridade considera funções como **condição de vitória, tanque, foco em
construções, pressão, mata-tanque, unidade aérea e enxame**.

A pontuação serve apenas para ordenar as cartas mais relevantes visualmente.
Ela **não é uma nota de força da carta** e não prevê quem venceria a partida.
            """
        )


def mostrar_respostas_naturais(j1, j2):
    deck1 = j1.get("currentDeck", [])
    deck2 = j2.get("currentDeck", [])

    nome1 = j1.get("name", "Jogador 1")
    nome2 = j2.get("name", "Jogador 2")

    cobertura1 = cobertura_respostas(deck1, deck2)
    cobertura2 = cobertura_respostas(deck2, deck1)

    st.markdown(
        '<div class="comparison-title">🛡️ Respostas Naturais</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Heurística inicial baseada nas funções das cartas. "
        "Não representa counter garantido nem previsão de vitória."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {nome1}")
        st.metric(
            "Ameaças adversárias cobertas",
            f"{cobertura1['cobertas']}/{cobertura1['total']}"
        )
        st.progress(min(cobertura1["percentual"] / 100, 1.0))

        if cobertura1["detalhes"]:
            for item in cobertura1["detalhes"]:
                st.markdown(f"**Contra {item['attacker']}**")

                for resposta in item["responses"][:3]:
                    st.write(
                        f"• {resposta['defender']} — {resposta['label']}"
                    )
        else:
            st.caption(
                "Nenhuma interação foi identificada com a base atual."
            )

    with col2:
        st.markdown(f"### {nome2}")
        st.metric(
            "Ameaças adversárias cobertas",
            f"{cobertura2['cobertas']}/{cobertura2['total']}"
        )
        st.progress(min(cobertura2["percentual"] / 100, 1.0))

        if cobertura2["detalhes"]:
            for item in cobertura2["detalhes"]:
                st.markdown(f"**Contra {item['attacker']}**")

                for resposta in item["responses"][:3]:
                    st.write(
                        f"• {resposta['defender']} — {resposta['label']}"
                    )
        else:
            st.caption(
                "Nenhuma interação foi identificada com a base atual."
            )

    with st.expander("ℹ️ Limitações desta análise"):
        st.markdown(
            """
As regras desta versão consideram apenas funções gerais, como:

- anti-aéreo × unidade aérea;
- feitiço leve ou splash × enxame;
- mata-tanque × tanque;
- construção × unidade focada em construções;
- reset × mecânica Inferno.

O resultado real também depende de **nível, evolução, posicionamento, timing,
suporte de outras cartas, torre e habilidade do jogador**. Por isso esta seção
usa o termo **resposta natural**, e não "counter garantido".
            """
        )


def mostrar_inteligencia_decks(j1, j2):
    deck1 = j1.get("currentDeck", [])
    deck2 = j2.get("currentDeck", [])

    nome1 = j1.get("name", "Jogador 1")
    nome2 = j2.get("name", "Jogador 2")

    analise1 = analisar_deck(deck1)
    analise2 = analisar_deck(deck2)

    st.markdown(
        '<div class="comparison-title">🧠 Inteligência de Deck</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Métricas calculadas a partir dos custos de elixir dos decks atuais."
    )

    metricas = [
        (
            "💧 Elixir médio",
            f"{analise1['elixir_medio']:.1f}",
            f"{analise2['elixir_medio']:.1f}"
        ),
        (
            "🔄 4 cartas mais baratas",
            f"{analise1['ciclo_4']:.0f} elixir",
            f"{analise2['ciclo_4']:.0f} elixir"
        ),
        (
            "🪶 Cartas leves (≤3)",
            str(analise1["cartas_leves"]),
            str(analise2["cartas_leves"])
        ),
        (
            "🧱 Cartas pesadas (≥5)",
            str(analise1["cartas_pesadas"]),
            str(analise2["cartas_pesadas"])
        ),
        (
            "⬇️ Menor custo",
            f"{analise1['menor_custo']:.0f}",
            f"{analise2['menor_custo']:.0f}"
        ),
        (
            "⬆️ Maior custo",
            f"{analise1['maior_custo']:.0f}",
            f"{analise2['maior_custo']:.0f}"
        ),
    ]

    cab1, cab2, cab3 = st.columns([2, 1, 2])

    with cab1:
        st.markdown(f"### {nome1}")

    with cab2:
        st.markdown("### VS")

    with cab3:
        st.markdown(f"### {nome2}")

    for titulo, valor1, valor2 in metricas:
        col1, centro, col2 = st.columns([2, 1, 2])

        with col1:
            st.metric(titulo, valor1)

        with centro:
            st.markdown(
                "<div style='text-align:center; padding-top:32px;'>↔️</div>",
                unsafe_allow_html=True
            )

        with col2:
            st.metric(titulo, valor2)

    comuns = cartas_em_comum(deck1, deck2)

    st.markdown("#### 🃏 Cartas presentes nos dois decks")

    if comuns:
        st.write(" • ".join(comuns))
    else:
        st.caption("Os dois decks não possuem cartas em comum.")

    with st.expander("ℹ️ Como interpretar estas métricas?"):
        st.markdown(
            """
- **Elixir médio:** média do custo das 8 cartas do deck.
- **4 cartas mais baratas:** soma das quatro cartas de menor custo; serve como indicador simples de quão barato é o núcleo de rotação.
- **Cartas leves:** cartas de custo 3 ou menos.
- **Cartas pesadas:** cartas de custo 5 ou mais.
- **Menor/Maior custo:** extremos de custo dentro do deck.

Essas métricas ainda não medem matchup ou counters. Essa será a próxima camada, usando uma base de funções e interações entre cartas.
            """
        )


def obter_url_imagem(carta):
    """
    A API normalmente fornece iconUrls.medium.
    """

    icon_urls = carta.get("iconUrls", {})

    if not isinstance(icon_urls, dict):
        return None

    return (
        icon_urls.get("medium")
        or icon_urls.get("evolutionMedium")
    )


def numero(valor):
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


# ============================================================
# EXIBIÇÃO DO PERFIL
# ============================================================

def mostrar_perfil(jogador):

    nome = html.escape(str(jogador.get("name", "Jogador")))
    tag = html.escape(str(jogador.get("tag", "")))
    trofeus = jogador.get("trophies", 0)
    melhor = jogador.get("bestTrophies", 0)
    nivel = html.escape(str(jogador.get("expLevel", "-")))
    wins = jogador.get("wins", 0)
    losses = jogador.get("losses", 0)
    battles = jogador.get("battleCount", 0)

    arena = html.escape(str(obter_nome_arena(jogador)))
    cla = html.escape(str(obter_nome_cla(jogador)))
    winrate = calcular_taxa_vitoria(jogador)

    st.markdown(
        f"""
        <div class="player-card">
            <div class="player-name">{nome}</div>
            <div class="player-tag">{tag}</div>
        </div>

        <div class="profile-stats-grid">
            <div class="profile-stat">
                <div class="profile-stat-label">🏆 Troféus</div>
                <div class="profile-stat-value">{numero(trofeus)}</div>
            </div>
            <div class="profile-stat">
                <div class="profile-stat-label">⚔️ Vitórias</div>
                <div class="profile-stat-value">{numero(wins)}</div>
            </div>
            <div class="profile-stat">
                <div class="profile-stat-label">🎮 Batalhas</div>
                <div class="profile-stat-value">{numero(battles)}</div>
            </div>
            <div class="profile-stat">
                <div class="profile-stat-label">🏅 Recorde</div>
                <div class="profile-stat-value">{numero(melhor)}</div>
            </div>
            <div class="profile-stat">
                <div class="profile-stat-label">💀 Derrotas</div>
                <div class="profile-stat-value">{numero(losses)}</div>
            </div>
            <div class="profile-stat">
                <div class="profile-stat-label">📊 Taxa de vitória</div>
                <div class="profile-stat-value">{winrate:.1f}%</div>
            </div>
        </div>

        <div class="profile-details">
            <div class="profile-detail">👑 Nível: {nivel}</div>
            <div class="profile-detail">🏟️ Arena: {arena}</div>
            <div class="profile-detail">🛡️ Clã: {cla}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# EXIBIÇÃO DO DECK
# ============================================================

def mostrar_deck(jogador):

    deck = jogador.get("currentDeck", [])

    if not deck:
        st.warning("Deck atual não disponível.")
        return

    elixir = calcular_elixir_medio(deck)

    st.markdown(
        '<div class="deck-title">🃏 Deck atual</div>',
        unsafe_allow_html=True
    )

    cards_html = []

    for carta in deck:
        imagem = obter_url_imagem(carta)
        nome = html.escape(str(carta.get("name", "Carta")))
        nivel = html.escape(str(carta.get("level", "?")))
        max_level = carta.get("maxLevel")

        texto_nivel = f"Nível {nivel}"

        if max_level:
            texto_nivel += f" / {html.escape(str(max_level))}"

        if imagem:
            imagem_segura = html.escape(str(imagem), quote=True)
            imagem_html = (
                f'<a href="{imagem_segura}" target="_blank" '
                f'title="Abrir {nome} ampliada">'
                f'<img src="{imagem_segura}" alt="{nome}">'
                f'</a>'
            )
        else:
            imagem_html = '<div style="height:88px;"></div>'

        cards_html.append(
            f"""
            <div class="deck-card">
                {imagem_html}
                <div class="deck-card-name">{nome}</div>
                <div class="deck-card-level">{texto_nivel}</div>
            </div>
            """
        )

    st.html(
        f"""
        <div class="deck-grid">
            {''.join(cards_html)}
        </div>
        <div class="deck-zoom-note">
            🔎 Toque ou clique em uma carta para abrir a imagem ampliada.
        </div>
        """
    )

    st.metric(
        "💧 Elixir médio",
        f"{elixir:.1f}"
    )


# ============================================================
# COMPARAÇÕES
# ============================================================

def vencedor_visual(valor1, valor2):

    if valor1 > valor2:
        return "⬅️"

    if valor2 > valor1:
        return "➡️"

    return "🤝"


def mostrar_comparacao(j1, j2):

    st.markdown(
        '<div class="comparison-title">📊 Comparação direta</div>',
        unsafe_allow_html=True
    )

    dados = [
        (
            "Troféus",
            j1.get("trophies", 0),
            j2.get("trophies", 0)
        ),
        (
            "Recorde de troféus",
            j1.get("bestTrophies", 0),
            j2.get("bestTrophies", 0)
        ),
        (
            "Vitórias",
            j1.get("wins", 0),
            j2.get("wins", 0)
        ),
        (
            "Nível",
            j1.get("expLevel", 0),
            j2.get("expLevel", 0)
        ),
        (
            "Taxa de vitória",
            calcular_taxa_vitoria(j1),
            calcular_taxa_vitoria(j2)
        ),
    ]

    nome1 = j1.get("name", "Jogador 1")
    nome2 = j2.get("name", "Jogador 2")

    col_nome1, col_indicador, col_nome2 = st.columns(
        [2, 1, 2]
    )

    with col_nome1:
        st.markdown(f"### {nome1}")

    with col_indicador:
        st.markdown("### VS")

    with col_nome2:
        st.markdown(f"### {nome2}")

    for titulo, valor1, valor2 in dados:

        c1, meio, c2 = st.columns([2, 1, 2])

        if titulo == "Taxa de vitória":

            texto1 = f"{valor1:.1f}%"
            texto2 = f"{valor2:.1f}%"

        else:

            texto1 = numero(valor1)
            texto2 = numero(valor2)

        with c1:
            st.metric(titulo, texto1)

        with meio:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    font-size:1.6rem;
                    padding-top:32px;
                ">
                    {vencedor_visual(valor1, valor2)}
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.metric(titulo, texto2)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    '<div class="main-title">⚔️ Jogador X Jogador</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Compare dois jogadores de Clash Royale e seus decks lado a lado.
        <br><span style="font-size:.72rem; opacity:.55;">UI móvel v2</span>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FORMULÁRIO
# ============================================================

with st.form("comparacao_jogadores"):

    coluna1, coluna2 = st.columns(2)

    with coluna1:

        tag1 = st.text_input(
            "TAG do Jogador 1",
            placeholder="#P9RV222GG",
        )

    with coluna2:

        tag2 = st.text_input(
            "TAG do Jogador 2",
            placeholder="#XXXXXXXXX",
        )

    comparar = st.form_submit_button(
        "⚔️ COMPARAR JOGADORES",
        use_container_width=True,
        type="primary",
    )


# ============================================================
# PROCESSAMENTO
# ============================================================

if comparar:

    if not tag1 or not tag2:

        st.warning(
            "Informe as duas TAGs para realizar a comparação."
        )

        st.stop()

    tag1_normalizada = normalizar_tag(tag1)
    tag2_normalizada = normalizar_tag(tag2)

    if tag1_normalizada == tag2_normalizada:

        st.warning(
            "Informe duas TAGs diferentes para realizar a comparação."
        )

        st.stop()

    permitido, restante = liberar_busca("comparacao")

    if not permitido:
        st.warning(
            f"Aguarde {restante:.1f}s antes de realizar outra comparação."
        )
        st.stop()

    with st.spinner("Buscando os dois jogadores..."):

        jogador1, erro1, status1 = buscar_jogador(
            tag1_normalizada,
            PROXY_API_URL,
            PROXY_SECRET,
        )
        jogador2, erro2, status2 = buscar_jogador(
            tag2_normalizada,
            PROXY_API_URL,
            PROXY_SECRET,
        )

    if erro1:

        st.error(
            f"Erro ao consultar Jogador 1: {erro1}"
        )

    if erro2:

        st.error(
            f"Erro ao consultar Jogador 2: {erro2}"
        )

    if erro1 or erro2:
        st.stop()

    # ========================================================
    # VISUALIZAÇÃO EM ABAS
    # ========================================================

    st.divider()

    nome1 = jogador1.get("name", "Jogador 1")
    nome2 = jogador2.get("name", "Jogador 2")

    aba_jogador1, aba_jogador2, aba_comparacao = st.tabs(
        [
            f"👤 {nome1}",
            f"👤 {nome2}",
            "⚔️ Comparação"
        ]
    )

    # --------------------------------------------------------
    # ABA JOGADOR 1
    # --------------------------------------------------------

    with aba_jogador1:

        mostrar_perfil(jogador1)

        st.divider()

        mostrar_deck(jogador1)

    # --------------------------------------------------------
    # ABA JOGADOR 2
    # --------------------------------------------------------

    with aba_jogador2:

        mostrar_perfil(jogador2)

        st.divider()

        mostrar_deck(jogador2)

    # --------------------------------------------------------
    # ABA COMPARAÇÃO
    # --------------------------------------------------------

    with aba_comparacao:

        st.markdown(
            """
            <div style="
                text-align:center;
                font-size:1.15rem;
                font-weight:700;
                margin-bottom:12px;
                opacity:.85;
            ">
                Painel de matchup
            </div>
            """,
            unsafe_allow_html=True
        )

        mostrar_snapshot_matchup(
            jogador1,
            jogador2
        )

        aba_resumo, aba_estrategia, aba_cobertura, aba_decks = st.tabs(
            [
                "📊 Resumo",
                "🧭 Estratégia",
                "🧩 Cobertura",
                "🃏 Decks"
            ]
        )

        # ====================================================
        # RESUMO
        # ====================================================

        with aba_resumo:

            mostrar_comparacao(
                jogador1,
                jogador2
            )

            st.divider()

            mostrar_inteligencia_decks(
                jogador1,
                jogador2
            )

        # ====================================================
        # ESTRATÉGIA
        # ====================================================

        with aba_estrategia:

            mostrar_resumo_estrategico(
                jogador1,
                jogador2
            )

            st.divider()

            mostrar_vulnerabilidades_matchup(
                jogador1,
                jogador2
            )

            st.divider()

            mostrar_principais_ameacas(
                jogador1,
                jogador2
            )

        # ====================================================
        # COBERTURA TÁTICA
        # ====================================================

        with aba_cobertura:

            mostrar_funcoes_decks(
                jogador1,
                jogador2
            )

            st.divider()

            mostrar_respostas_naturais(
                jogador1,
                jogador2
            )

        # ====================================================
        # DECK X DECK
        # ====================================================

        with aba_decks:

            st.markdown(
                """
                <div style="
                    text-align:center;
                    font-size:1.5rem;
                    font-weight:800;
                    margin-bottom:20px;
                ">
                    🃏 Deck X Deck
                </div>
                """,
                unsafe_allow_html=True
            )

            coluna_deck1, coluna_deck2 = st.columns(
                2,
                gap="large"
            )

            with coluna_deck1:

                st.markdown(
                    f"### {nome1}"
                )

                mostrar_deck(jogador1)

            with coluna_deck2:

                st.markdown(
                    f"### {nome2}"
                )

                mostrar_deck(jogador2)

            st.caption(
                "Use as abas Resumo, Estratégia e Cobertura para interpretar "
                "as diferenças estruturais entre os dois decks."
            )
