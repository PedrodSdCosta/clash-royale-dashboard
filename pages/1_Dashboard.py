import os
import requests
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from clash_api import buscar_jogador, liberar_busca


# ============================================================
# CONFIGURAÇÃO DO PROXY
# ============================================================

load_dotenv()


def get_config(name):
    """
    Primeiro tenta ler dos Secrets do Streamlit.
    Se não encontrar, tenta variável de ambiente local.
    """
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name)


PROXY_API_URL = get_config("PROXY_API_URL")
PROXY_SECRET = get_config("PROXY_SECRET")


# ============================================================
# TÍTULO
# ============================================================

st.title("👑 Clash Royale - Dashboard de Jogador")

st.markdown(
    "Insira a **Tag do Jogador** para visualizar o perfil, "
    "tempo de conta e estatísticas."
)


# ============================================================
# CAMPO DE BUSCA
# ============================================================

with st.form("busca_jogador_dashboard"):
    player_tag_input = st.text_input(
        "Tag do Jogador:",
        value="#P9RV222GG",
        help="Exemplo: #P9RV222GG ou P9RV222GG"
    )

    buscar_dados = st.form_submit_button(
        "Buscar Dados",
        type="primary",
        use_container_width=True
    )


# ============================================================
# BUSCA
# ============================================================

if buscar_dados:

    if not PROXY_API_URL:
        st.error(
            "Erro: PROXY_API_URL não encontrada nos Secrets do Streamlit."
        )

    elif not PROXY_SECRET:
        st.error(
            "Erro: PROXY_SECRET não encontrada nos Secrets do Streamlit."
        )

    else:

        permitido, restante = liberar_busca("dashboard")

        if not permitido:
            st.warning(
                f"Aguarde {restante:.1f}s antes de realizar outra busca."
            )
            st.stop()

        with st.spinner("Buscando dados na API do Clash Royale..."):

            data, erro_busca, status_busca = buscar_jogador(
                player_tag_input,
                PROXY_API_URL,
                PROXY_SECRET,
            )

            if erro_busca:
                if status_busca == 429:
                    st.warning(erro_busca)
                else:
                    st.error(erro_busca)
                st.stop()

            try:


                # ====================================================
                # 1. TEMPO DE CONTA
                # ====================================================

                years_played = "Não identificado"

                badges = data.get("badges", [])

                for badge in badges:

                    badge_name = badge.get("name", "")

                    if (
                        "Years" in badge_name
                        or "years" in badge_name
                        or "Played" in badge_name
                    ):

                        val = badge.get(
                            "progress",
                            badge.get("level", 0)
                        )

                        if val > 100:

                            anos = val // 365
                            meses = (val % 365) // 30

                            years_played = (
                                f"{anos}a {meses}m ({val}d)"
                            )

                        else:

                            years_played = f"{val} anos"

                        break


                if years_played == "Não identificado":

                    achievements = data.get(
                        "achievements",
                        []
                    )

                    for ach in achievements:

                        ach_name = ach.get("name", "")

                        if (
                            "Years" in ach_name
                            or "Poker" in ach_name
                        ):

                            val = ach.get("value", 0)

                            if val > 100:

                                anos = val // 365

                                years_played = (
                                    f"{anos} anos"
                                )

                            else:

                                years_played = (
                                    f"{val} anos"
                                )

                            break


                # ====================================================
                # 2. CABEÇALHO DO JOGADOR
                # ====================================================

                st.divider()

                st.header(
                    f"🎮 {data.get('name')} "
                    f"({data.get('tag')})"
                )


                clan_name = (
                    data["clan"]["name"]
                    if "clan" in data
                    else "Sem Clã"
                )


                st.caption(
                    f"🛡️ Clã: **{clan_name}** | "
                    f"Nível do Rei: "
                    f"**{data.get('expLevel')}** | "
                    f"⏳ Tempo de Jogo: "
                    f"**{years_played}**"
                )


                # ====================================================
                # 3. ESTATÍSTICAS
                # ====================================================

                wins = data.get("wins", 0)

                losses = data.get("losses", 0)

                battle_count = data.get(
                    "battleCount",
                    wins + losses
                )


                winrate = (
                    wins / battle_count * 100
                    if battle_count > 0
                    else 0.0
                )


                col1, col2, col3, col4, col5, col6 = (
                    st.columns(6)
                )


                col1.metric(
                    "Troféus Atuais",
                    data.get("trophies", 0)
                )


                col2.metric(
                    "Recorde Troféus",
                    data.get("bestTrophies", 0)
                )


                col3.metric(
                    "Vitórias",
                    wins
                )


                col4.metric(
                    "Derrotas 💔",
                    losses
                )


                col5.metric(
                    "Winrate",
                    f"{winrate:.1f}%"
                )


                col6.metric(
                    "Tempo de Conta",
                    years_played
                )


                st.divider()


                # ====================================================
                # 4. DECK ATUAL
                # ====================================================

                st.subheader(
                    "⚔️ Deck Batalha Atual"
                )


                with st.popover(
                    "ℹ️ Como os níveis das cartas "
                    "são calculados?"
                ):

                    st.markdown(
                        """
Dentro do Clash Royale, cada raridade de carta começa
em um nível base diferente na API:

* ⚪ **Comum:** Nível inicial 1
* 🟠 **Rara:** Nível inicial 3
* 🟣 **Épica:** Nível inicial 6
* 🟡 **Lendária:** Nível inicial 9
* 🔴 **Campeão:** Nível inicial 11

Nosso sistema converte o nível interno da API para o
**Nível de Batalha Real (1 ao 15)**.
                        """
                    )


                current_deck = data.get(
                    "currentDeck",
                    []
                )


                if current_deck:

                    cols = st.columns(8)


                    for idx, card in enumerate(
                        current_deck
                    ):

                        with cols[idx]:

                            icon_url = (
                                card
                                .get("iconUrls", {})
                                .get("medium", "")
                            )


                            if icon_url:

                                st.image(
                                    icon_url,
                                    use_container_width=True
                                )


                            raw_level = card.get(
                                "level",
                                1
                            )


                            max_level = card.get(
                                "maxLevel",
                                15
                            )


                            real_level = (
                                15
                                - (
                                    max_level
                                    - raw_level
                                )
                            )


                            min_level = (
                                max_level - 14
                            )


                            rarity_map = {

                                1: "⚪ Comum",

                                3: "🟠 Rara",

                                6: "🟣 Épica",

                                9: "🟡 Lendária",

                                11: "🔴 Campeão"

                            }


                            rarity_label = (
                                rarity_map.get(
                                    min_level,
                                    "Carta"
                                )
                            )


                            st.markdown(
                                f"**{card.get('name')}**"
                            )


                            if real_level == 15:

                                st.markdown(
                                    "👑 **Nível 15** "
                                    "*(Elite)*"
                                )

                            else:

                                st.markdown(
                                    f"⭐ **Nível "
                                    f"{real_level}**"
                                )


                            st.caption(
                                rarity_label
                            )

                else:

                    st.info(
                        "Nenhum deck atual encontrado "
                        "para este jogador."
                    )


                st.divider()


                # ====================================================
                # 5. BADGES
                # ====================================================

                with st.expander(
                    "🏅 Ver Badges / "
                    "Insígnias do Jogador"
                ):

                    if badges:

                        badge_data = [

                            {

                                "Nome":
                                    b.get("name"),

                                "Nível / Progresso":
                                    b.get(
                                        "progress",
                                        b.get(
                                            "level",
                                            0
                                        )
                                    ),

                                "Max":
                                    b.get(
                                        "max",
                                        "-"
                                    )

                            }

                            for b in badges

                        ]


                        st.dataframe(

                            pd.DataFrame(
                                badge_data
                            ),

                            use_container_width=True

                        )


                # ====================================================
                # 6. TODAS AS CARTAS
                # ====================================================

                with st.expander(
                    "📚 Ver todas as cartas "
                    "da coleção do jogador"
                ):

                    cards_data = []


                    for card in data.get(
                        "cards",
                        []
                    ):

                        cards_data.append(
                            {

                                "Nome da Carta":
                                    card.get(
                                        "name"
                                    ),

                                "Nível":
                                    card.get(
                                        "level"
                                    ),

                                "Nível Máximo":
                                    card.get(
                                        "maxLevel"
                                    ),

                                "Contagem de Cartas":
                                    card.get(
                                        "count",
                                        0
                                    )

                            }
                        )


                    df_cards = pd.DataFrame(
                        cards_data
                    )


                    st.dataframe(
                        df_cards,
                        use_container_width=True
                    )


            # ========================================================
            # TRATAMENTO DE ERROS
            # ========================================================

            except Exception as e:

                st.error(
                    f"Ocorreu um erro inesperado: {e}"
                )
