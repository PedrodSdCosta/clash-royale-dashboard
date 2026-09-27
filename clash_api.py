import re
import time
from urllib.parse import quote

import requests
import streamlit as st


CACHE_TTL_SECONDS = 60
SEARCH_COOLDOWN_SECONDS = 1.5
TAG_PATTERN = re.compile(r"^#[0289PYLQGRJCUV]+$")


class ClashApiError(Exception):
    def __init__(self, mensagem, status=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


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
    Consulta o proxy e mantém somente respostas bem-sucedidas em cache.
    Exceções não ficam cacheadas, evitando "prender" respostas 429/5xx.
    """
    tag_codificada = quote(tag, safe="")
    url = f"{proxy_api_url.rstrip('/')}/v1/players/{tag_codificada}"

    headers = {
        "X-Proxy-Token": proxy_secret,
        "Accept": "application/json",
    }

    try:
        resposta = requests.get(url, headers=headers, timeout=15)
    except requests.exceptions.Timeout as erro:
        raise ClashApiError(
            "O servidor demorou demais para responder.",
            408,
        ) from erro
    except requests.exceptions.ConnectionError as erro:
        raise ClashApiError(
            "Não foi possível conectar ao servidor proxy.",
            503,
        ) from erro
    except requests.exceptions.RequestException as erro:
        raise ClashApiError(
            f"Erro de comunicação: {erro}",
            500,
        ) from erro

    status = resposta.status_code

    if status == 200:
        try:
            return resposta.json()
        except ValueError as erro:
            raise ClashApiError(
                "O servidor retornou uma resposta inválida.",
                502,
            ) from erro

    if status == 401:
        raise ClashApiError("Acesso não autorizado ao proxy.", status)

    if status == 403:
        raise ClashApiError("Acesso negado pelo proxy.", status)

    if status == 404:
        raise ClashApiError(
            "Jogador não encontrado. Confira a TAG.",
            status,
        )

    if status == 429:
        retry_after = resposta.headers.get("Retry-After")

        if retry_after:
            mensagem = (
                "Muitas consultas em pouco tempo. "
                f"Tente novamente em {retry_after}s."
            )
        else:
            mensagem = (
                "Muitas consultas em pouco tempo. "
                "Aguarde alguns instantes e tente novamente."
            )

        raise ClashApiError(mensagem, status)

    if status >= 500:
        raise ClashApiError(
            f"O servidor apresentou erro {status}.",
            status,
        )

    raise ClashApiError(f"Erro HTTP {status}.", status)


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

    try:
        data = _buscar_jogador_cache(
            proxy_api_url,
            proxy_secret,
            tag,
        )
        return data, None, 200
    except ClashApiError as erro:
        return None, erro.mensagem, erro.status


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
