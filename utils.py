import requests
import urllib3
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Desabilita warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URLs base
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/100.0.4896.127 Safari/537.36'
}
BASE_URL = (
    'https://fnet.bmfbovespa.com.br/fnet/publico/'
    'abrirGerenciadorDocumentosCVM?cnpjFundo={}'
)
JSON_URL = (
    'https://fnet.bmfbovespa.com.br/fnet/publico/'
    'listarDocumentosEnviadosCVM'
)
BASE_DOWNLOAD_URL = (
    'https://fnet.bmfbovespa.com.br/fnet/publico/'
    'downloadDocumentoCVM?idDocumento={}'
)

def fetch_document_links(cnpj: str) -> dict:
    """
    Consulta o endpoint JSON ou HTML e retorna dict {nome_arquivo: url_download}.
    """
    session = requests.Session()
    links = {}

    # Tenta JSON via endpoint
    json_headers = HEADERS.copy()
    json_headers['Accept'] = 'application/json, text/javascript'
    payload = {'cnpjFundo': cnpj}
    resp = session.post(JSON_URL, headers=json_headers, data=payload,
                        verify=False, timeout=15)
    if resp.ok:
        try:
            data = resp.json().get('data', [])
            for item in data:
                doc_id = item.get('idDocumento') or item.get('IDDOCUMENTO')
                nome = item.get('nmArquivo') or item.get('nomeArquivo') or f'documento_{doc_id}.xml'
                links[nome] = BASE_DOWNLOAD_URL.format(doc_id)
            if links:
                return links
        except ValueError:
            pass

    # Fallback HTML
    resp = session.get(BASE_URL.format(cnpj), headers=HEADERS,
                       verify=False, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'lxml')
    for a in soup.select('a[href*="downloadDocumentoCVM"][href$=".xml"]'):
        href = a['href']
        doc_id = ''.join(filter(str.isdigit, href))
        nome = a.get_text(strip=True) or f'documento_{doc_id}.xml'
        links[nome] = urljoin(resp.url, href)

    return links
