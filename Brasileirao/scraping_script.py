from urllib.error import URLError, HTTPError
from urllib.request import urlopen
import os
import pandas as pd
from bs4 import BeautifulSoup

# Caminho base onde as subpastas serão criadas
pasta_base = r"C:\Users\mathe\Desktop\TCC\Brasileirao\tabelaBrasileiraoCompleto"

# Anos para realizar o web scraping
anos = list(range(2013, 2024))

# URL base para construir a URL específica de cada ano
url_base = "https://fbref.com/en/comps/24/{ano}/{ano}-Serie-A-Stats"

# Dicionário que mapeia o nome da página na planilha com o ID da tabela no HTML
dict_tables = {
    "Classificação": "results{ano}241_overall",
    "Estats Time": "stats_squads_standard_for",
    "Goleiros": "stats_squads_keeper_for",
    "Goleiros adv": "stats_squads_keeper_adv_for",
    "Finalizações": "stats_squads_shooting_for",
    "Passes": "stats_squads_passing_for",
    "Passes Tipo": "stats_squads_passing_types_for",
    "Chances Criadas": "stats_squads_gca_for",
    "Defesa": "stats_squads_defense_for",
    "Posse de Bola": "stats_squads_possession_for",
    "Tempo de Jogo": "stats_squads_playing_time_for",
    "Diversos": "stats_squads_misc_for"
}

for ano in anos:
    # Criar a subpasta para o ano atual no loop, se ela não existir
    pasta_ano = os.path.join(pasta_base, str(ano))
    os.makedirs(pasta_ano, exist_ok=True)

    # Construir a URL para o ano atual no loop
    url = url_base.format(ano=ano) if ano < 2023 else "https://fbref.com/en/comps/24/Serie-A-Stats"

    try:
        # Abrir a URL e obter o conteúdo HTML da página
        response = urlopen(url)
        html = response.read()
    except HTTPError as e:
        print(f"HTTP Error: {e.status} {e.reason} para o ano {ano}")
        continue
    except URLError as e:
        print(f"URL Error: {e.reason} para o ano {ano}")
        continue

    # Tratar o HTML obtido
    html = " ".join(html.decode('utf-8').split()).replace('> <', '><')

    # Criar um objeto BeautifulSoup a partir do HTML tratado
    soup = BeautifulSoup(html, 'html.parser')

    for pagina, id in dict_tables.items():
        # Ajustar o ID da tabela para o ano, se necessário
        id_ajustado = id.replace("{ano}", str(ano)[-2:]) if ano < 2023 else id
        soup_tabela = soup.find('table', id=id_ajustado)

        if soup_tabela:
            soup_tabela = soup_tabela.find_all('tbody')

            lista_equipes = []
            for equipe in soup_tabela[0].find_all('tr'):
                dict_equipe = {}
                dict_equipe[equipe.find('th').get('data-stat')] = equipe.find('th').getText()
                for info in equipe.find_all('td'):
                    dict_equipe[info.get('data-stat')] = info.getText()

                lista_equipes.append(dict_equipe)

            df = pd.DataFrame(lista_equipes)

            # Definir o caminho completo do arquivo CSV dentro da subpasta do ano
            caminho_arquivo_csv = os.path.join(pasta_ano, f"{pagina}.csv")

            # Salvar o DataFrame como CSV no caminho especificado
            df.to_csv(caminho_arquivo_csv, index=False)

            print(f"Tabela '{pagina}' do ano {ano} salva como CSV em '{caminho_arquivo_csv}'.")
        else:
            print(f"A tabela com ID '{id_ajustado}' não foi encontrada para o ano {ano}.")
