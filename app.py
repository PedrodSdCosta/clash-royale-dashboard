# FORCE_REDEPLOY_MOBILE_UI_V2
import streamlit as st


st.set_page_config(
    page_title="Clash Royale Dashboard",
    page_icon="👑",
    layout="wide"
)


dashboard_page = st.Page(
    "pages/1_Dashboard.py",
    title="Dashboard",
    icon="👑",
    default=True,
)

comparison_page = st.Page(
    "pages/2_Jogador_vs_Jogador.py",
    title="Jogador vs Jogador",
    icon="⚔️",
)

navigation = st.navigation(
    [dashboard_page, comparison_page],
    position="hidden",
)


# Navegação superior explícita.
# Agora os destinos estão registrados pelo st.navigation antes dos links.
col_dashboard, col_comparison = st.columns(2)

with col_dashboard:
    st.page_link(
        dashboard_page,
        label="Dashboard",
        use_container_width=True,
    )

with col_comparison:
    st.page_link(
        comparison_page,
        label="Jogador vs Jogador",
        use_container_width=True,
    )

st.divider()

navigation.run()
