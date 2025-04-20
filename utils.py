import requests
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin

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

def fetch_documents(cnpj: str) -> dict:
    '''
    Consulta documentos via JSON e, se falhar, faz fallback no HTML.
    Retorna dict {nome_arquivo: conteudo_xml}.
    '''
    session = requests.Session()
    resultado = {}

    # 1. Tenta JSON via endpoint
    json_headers = HEADERS.copy()
    json_headers['Accept'] = 'application/json, text/javascript'
    payload = {'cnpjFundo': cnpj}
    r_json = session.post(JSON_URL, headers=json_headers, data=payload,
                          verify=False, timeout=15)
    if r_json.ok:
        try:
            j = r_json.json()
            for row in j.get('data', []):
                doc_id = row.get('idDocumento') or row.get('IDDOCUMENTO')
                nome = row.get('nmArquivo') or row.get('nomeArquivo') or f'documento_{doc_id}.xml'
                download_url = BASE_DOWNLOAD_URL.format(doc_id)
                r = session.get(download_url, headers=HEADERS,
                                 verify=False, timeout=15)
                r.raise_for_status()
                resultado[nome] = r.text
            if resultado:
                return resultado
        except ValueError:
            pass

    # 2. Fallback: página HTML
    resp = session.get(BASE_URL.format(cnpj), headers=HEADERS,
                       verify=False, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'lxml')

    # busca links diretos para download de XML
    for a in soup.select('a[href*="downloadDocumentoCVM"][href$=".xml"]'):
        href = a['href']
        doc_id = ''.join(filter(str.isdigit, href))
        nome = a.text.strip() or f'documento_{doc_id}.xml'
        download_url = urljoin(resp.url, href)
        r = session.get(download_url, headers=HEADERS,
                         verify=False, timeout=15)
        r.raise_for_status()
        resultado[nome] = r.text

    return resultado
