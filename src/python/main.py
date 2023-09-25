import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import html

link = "https://www.vivareal.com.br/aluguel/espirito-santo/serra/"
requisicao = requests.get(link)
soup  = BeautifulSoup(requisicao.text,"html.parser")
tree = html.fromstring(str(soup))


# elementos_a = soup.select('a>')

# # # Itere sobre os elementos <a> e imprima seus textos
# for elemento in elementos_a:
#     print(elemento)
elementos_a = tree.xpath('//a')

# Itere sobre os elementos <a> e imprima seus textos
for elemento in elementos_a:
    print(elemento.text_content())

