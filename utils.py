import requests
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin

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

BASE_DOWNLOAD_URL = (
    'https://fnet.bmfbovespa.com.br/fnet/publico/'
    'downloadDocumentoCVM?idDocumento={}'
)

def fetch_documents(cnpj: str) -> dict:
    '''
    Consulta a página de documentos do fundo e retorna um dicionário
    {nome_arquivo: conteúdo_xml}.
    '''
    url = BASE_URL.format(cnpj)
    session = requests.Session()
    resp = session.get(url, headers=HEADERS, verify=False, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'lxml')
    resultado = {}

    # Tenta extrair da tabela de documentos
    table = soup.find('table', id='tblDocumentosEnviados')
    if table:
        rows = table.find_all('tr')[1:]
        for tr in rows:
            a = tr.find('a', href=True) or tr.find('a', onclick=True)
            if not a:
                continue
            href = a.get('href') or a.get('onclick')
            if 'downloadDocumentoCVM' in href:
                # extrai todos os dígitos para identificar o documento
                doc_id = ''.join(filter(str.isdigit, href))
                download_url = BASE_DOWNLOAD_URL.format(doc_id)
                nome = a.text.strip() or f'documento_{doc_id}'
            else:
                download_url = urljoin(resp.url, href)
                nome = a.text.strip() or href.split('=')[-1]

            r = session.get(download_url, headers=HEADERS, verify=False, timeout=15)
            r.raise_for_status()
            resultado[nome] = r.text
    else:
        # Fallback: busca links diretos para arquivos XML
        links = soup.select("a[href*='.xml']")
        for a in links:
            href = a['href']
            nome = a.text.strip() or href.split('=')[-1]
            download_url = urljoin(resp.url, href)
            r = session.get(download_url, headers=HEADERS, verify=False, timeout=15)
            r.raise_for_status()
            resultado[nome] = r.text

    return resultado
