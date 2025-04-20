import streamlit as st
from utils import fetch_documents

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
        with st.spinner('Consultando...'):
            docs = fetch_documents(cnpj)

        if docs:
            for nome, xml in docs.items():
                with st.expander(nome):
                    st.code(xml, language='xml')
        else:
            st.warning('Nenhum documento XML encontrado para este CNPJ.')
    except Exception as e:
        st.error(f'Erro ao consultar: {e}')
