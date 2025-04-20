import streamlit as st
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import pandas as pd

# Função para obter links de arquivos XML a partir do CNPJ do fundo
def get_xml_links(cnpj: str) -> list:
    url = f"https://fnet.bmfbovespa.com.br/fnet/publico/abrirGerenciadorDocumentosCVM?cnpjFundo={cnpj}"
    resp = requests.get(url, verify=False)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".xml"):
            if href.startswith("http"):
                full = href
            else:
                full = f"https://fnet.bmfbovespa.com.br{href}"
            links.append(full)
    return links

# Função para baixar e parsear um arquivo XML em DataFrame e metadados
def parse_xml(url: str) -> dict:
    resp = requests.get(url)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    # Metadados
    versao = root.findtext('.//VERSAO')
    dt_compt = root.findtext('.//DT_COMPT')
    cnpj_adm = root.findtext('.//NR_CNPJ_ADM')
    patrimonio = float(root.findtext('.//VL_SOM_PATRLIQ') or 0)

    # Mapa de rentabilidades
    rent_map = {}
    for rent in root.findall('.//RENT_MES/*'):
        serie = rent.findtext('SERIE')
        tipo = rent.findtext('TIPO')
        pr = rent.findtext('PR_APURADA')
        rent_map[(serie, tipo)] = pr

    rows = []
    # Séries Senior
    for senior in root.findall('.//DESC_SERIE_CLASSE_SENIOR'):
        serie = senior.findtext('SERIE')
        qt = float(senior.findtext('QT_COTAS') or 0)
        vl = float(senior.findtext('VL_COTAS') or 0)
        qt_cot = int(senior.findtext('QT_COTISTAS') or 0)
        rent = rent_map.get((serie, 'Senior'), '')
        rows.append(['Senior', serie, qt, vl, qt * vl, qt_cot, rent])

    # Séries Subordinadas
    for sub in root.findall('.//DESC_SERIE_CLASSE_SUBORD'):
        tipo = sub.findtext('TIPO')
        serie = sub.findtext('SERIE') or ''
        qt = float(sub.findtext('QT_COTAS') or 0)
        vl = float(sub.findtext('VL_COTAS') or 0)
        qt_cot = int(sub.findtext('QT_COTISTAS') or 0)
        rent = rent_map.get((serie, tipo), '')
        rows.append([tipo, serie, qt, vl, qt * vl, qt_cot, rent])

    df = pd.DataFrame(
        rows,
        columns=['Tipo', 'Série', 'Qt Cotas', 'Vl Cota', 'Vl Total', 'Qt Cotistas', 'Rentabilidade']
    )

    return {
        'versao': versao,
        'dt_compt': dt_compt,
        'cnpj_adm': cnpj_adm,
        'patrimonio': patrimonio,
        'table': df
    }

# Interface Streamlit
def main():
    st.title("Consulta de XML da CVM")
    st.write("Informe o CNPJ do fundo (somente dígitos, ex: 22340978000135)")
    cnpj = st.text_input("CNPJ do fundo")

    if st.button("Buscar arquivos XML"):
        if not cnpj.isdigit():
            st.error("Por favor, digite apenas dígitos no CNPJ.")
            return
        with st.spinner("Buscando documentos..."):
            links = get_xml_links(cnpj)

        if not links:
            st.warning("Nenhum arquivo XML encontrado para esse CNPJ.")
            return

        sel = st.selectbox("Selecione o arquivo XML", links)
        if st.button("Carregar e processar XML"):
            with st.spinner("Processando XML..."):
                data = parse_xml(sel)

            st.subheader("Metadados do XML")
            st.write(f"**Versão:** {data['versao']}")
            st.write(f"**Data de Competência:** {data['dt_compt']}")
            st.write(f"**CNPJ Administrador:** {data['cnpj_adm']}")
            st.write(f"**Patrimônio Líquido:** R$ {data['patrimonio']:,}")

            st.subheader("Informações de Cotas")
            st.dataframe(data['table'])

if __name__ == "__main__":
    main()
