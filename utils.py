import requests
from bs4 import BeautifulSoup
import urllib3

# Desabilita warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/100.0.4896.127 Safari/537.36'
}

BASE_URL = (
    'https://fnet.bmfbovespa.com.br/fnet/publico/'
    'abrirGerenciadorDocumentosCVM?cnpjFundo={}'
)


def fetch_documents(cnpj: str) -> dict:
    """
    Consulta a página de documentos do fundo e retorna um dicionário
    {nome_arquivo: conteúdo_xml}.
    """
    url = BASE_URL.format(cnpj)
    session = requests.Session()
    resp = session.get(url, headers=HEADERS, verify=False, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'lxml')
    links = soup.select('a[href*="downloadDocumentoCVM"][href$=".xml"]')
    resultado = {}

    for a in links:
        href = a['href']
        nome = href.split('=')[-1]
        download_url = requests.compat.urljoin(resp.url, href)
        r = session.get(download_url, headers=HEADERS, verify=False, timeout=15)
        r.raise_for_status()
        resultado[nome] = r.text

    return resultado
