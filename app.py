import streamlit as st
from utils import fetch_document_links

st.set_page_config(
    page_title='CVM Scraper',
    layout='wide'
)

st.title('Consulta de Documentos CVM por CNPJ')

cnpj = st.text_input(
    'Informe o CNPJ do fundo (somente dígitos):',
    max_chars=14,
    help='Exemplo: 22340978000135'
)

if st.button('Buscar') and cnpj:
    try:
        with st.spinner('Buscando links...'):
            docs = fetch_document_links(cnpj)

        if docs:
            st.subheader('Documentos disponíveis para download:')
            for idx, (nome, url) in enumerate(docs.items(), 1):
                st.write(f"{idx}. [{nome}]({url})")
        else:
            st.warning('Nenhum documento encontrado para este CNPJ.')
    except Exception as e:
        st.error(f'Erro ao consultar: {e}')
