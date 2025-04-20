import streamlit as st
import requests
from bs4 import BeautifulSoup


# Função para obter os links dos informes
def get_informes(cnpj):
    url = f'https://fnet.bmfbovespa.com.br/fnet/publico/abrirGerenciadorDocumentosCVM?cnpjFundo={cnpj}'
    response = requests.get(url, verify=False)
    
    if response.status_code != 200:
        return f"Erro ao acessar o site. Status code: {response.status_code}"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = [a['href'] for a in soup.find_all('a', href=True) if 'pdf' in a['href']]
    
    if not links:
        return "Não foi possível encontrar links para os informes."
    
    return links

# Streamlit para o front-end
st.title("Consulta de Informes Mensais")
cnpj = st.text_input("Digite os últimos dígitos do CNPJ do fundo:")

if cnpj:
    full_cnpj = f"{cnpj}"  # Adicionando os últimos dígitos ao CNPJ fixo
    informes = get_informes(full_cnpj)
    
    if informes:
        st.write("Links para baixar os informes mensais:")
        for link in informes:
            st.markdown(f"[Baixar Informe]({link})")
    else:
        st.error("Não foi possível obter os informes para este CNPJ.")
