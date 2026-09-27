import re
import time
from urllib.parse import quote

import requests
import streamlit as st


CACHE_TTL_SECONDS = 60
SEARCH_COOLDOWN_SECONDS = 1.5
TAG_PATTERN = re.compile(r"^#[0289PYLQGRJCUV]+$")


def normalizar_tag(tag):
    """Normaliza uma TAG do Clash Royale para o formato #ABC123."""
    if not tag:
        return ""

    tag = str(tag).strip().upper().replace(" ", "")

    if not tag.startswith("#"):
        tag = "#" + tag

    return tag


def validar_tag(tag):
    """Valida formato e alfabeto usados nas TAGs da Supercell."""
    tag = normalizar_tag(tag)

    if not tag or tag == "#":
        return False, "Informe uma TAG válida."

    if not TAG_PATTERN.fullmatch(tag):
        return False, (
            "TAG inválida. Use apenas os caracteres válidos da TAG "
            "do Clash Royale, com ou sem #."
        )

    return True, None


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def _buscar_jogador_cache(proxy_api_url, proxy_secret, tag):
    """
    Consulta o proxy e mantém o resultado em cache por um curto período.
    O cache é compartilhado pelo processo do Streamlit para a mesma
    combinação de URL, credencial e TAG, reduzindo chamadas repetidas.
    """
    tag_codificada = quote(tag, safe="")
    url = f"{proxy_api_url.rstrip('/')}/v1/players/{tag_codificada}"

    headers = {
        "X-Proxy-Token": proxy_secret,
        "Accept": "application/json",
    }

    try:
        resposta = requests.get(url, headers=headers, timeout=15)
    except requests.exceptions.Timeout:
        return None, "O servidor demorou demais para responder.", 408
    except requests.exceptions.ConnectionError:
        return None, "Não foi possível conectar ao servidor proxy.", 503
    except requests.exceptions.RequestException as erro:
        return None, f"Erro de comunicação: {erro}", 500

    status = resposta.status_code

    if status == 200:
        try:
            return resposta.json(), None, status
        except ValueError:
            return None, "O servidor retornou uma resposta inválida.", 502

    if status == 401:
        return None, "Acesso não autorizado ao proxy.", status

    if status == 403:
        return None, "Acesso negado pelo proxy.", status

    if status == 404:
        return None, "Jogador não encontrado. Confira a TAG.", status

    if status == 429:
        retry_after = resposta.headers.get("Retry-After")
        if retry_after:
            return (
                None,
                f"Muitas consultas em pouco tempo. Tente novamente em {retry_after}s.",
                status,
            )
        return (
            None,
            "Muitas consultas em pouco tempo. Aguarde alguns instantes e tente novamente.",
            status,
        )

    if status >= 500:
        return None, f"O servidor apresentou erro {status}.", status

    return None, f"Erro HTTP {status}.", status


def buscar_jogador(tag, proxy_api_url, proxy_secret):
    """Valida a TAG e consulta o proxy usando cache temporário."""
    if not proxy_api_url:
        return None, (
            "PROXY_API_URL não foi encontrada nos Secrets do Streamlit "
            "ou nas variáveis de ambiente."
        ), None

    if not proxy_secret:
        return None, (
            "PROXY_SECRET não foi encontrado. Configure-o nos Secrets "
            "do Streamlit ou nas variáveis de ambiente."
        ), None

    tag = normalizar_tag(tag)
    valida, erro = validar_tag(tag)

    if not valida:
        return None, erro, 400

    return _buscar_jogador_cache(proxy_api_url, proxy_secret, tag)


def liberar_busca(chave="busca", segundos=SEARCH_COOLDOWN_SECONDS):
    """
    Evita disparos repetidos da mesma sessão em sequência.
    Retorna (permitido, segundos_restantes).
    """
    agora = time.monotonic()
    estado = f"_ultimo_clique_{chave}"
    ultimo = st.session_state.get(estado, 0.0)
    restante = segundos - (agora - ultimo)

    if restante > 0:
        return False, restante

    st.session_state[estado] = agora
    return True, 0.0
