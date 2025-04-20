from main import get_xml_links

if __name__ == "__main__":
    cnpj = "22340978000135"
    links = get_xml_links(cnpj)
    print(f"Encontrados {len(links)} documentos:\n")
    for url in links:
        print(" -", url)
