import requests
from bs4 import BeautifulSoup
import psycopg2
import json
import time

con = psycopg2.connect(host='localhost', database='meuimoveldb',
user='postgres', password='123456')
cur = con.cursor()

#titulo, tamanho (m²), logradouro, bairro, cidade, estado, preço, regime

regime = 'aluguel'

def montaDicionario(elements1, elements2, elements3):
    global regime
    
    dic = {}
    if elements1.__len__() == elements2.__len__():
        for i in range(elements1.__len__()):
            el = montaLista(elements1[i].text, elements2[i].text, elements3[i].find('p').text)
            el.append(regime)
            dic[i] = el
    return dic

def montaLista(txt1, txt2, txt3):
    l = []
    try:
        l.append(txt1.split(',')[0].strip()) #titulo
        l.append(int(txt1.split(',')[1].replace(' ', '').replace('m²', ''))) #tamanho
        
        eleementosDeEndereco = txt2.split('-')
        l.append(eleementosDeEndereco[0].strip()) #logradouro
        l.append(eleementosDeEndereco[1].split(',')[0].strip()) #bairro
        l.append(eleementosDeEndereco[1].split(',')[1].strip()) #cidade
        l.append(eleementosDeEndereco[2].strip()) #estado
        
        l.append(float(txt3.replace('R$', '')
                       .replace('/Mês', '')
                       .replace(' ', '')
                       .replace('.', '')
                       .replace(',', '.')
                       .replace('Preçoabaixodomercado', '')
                       .replace('/Dia', ''))) #preco
    except:
        l.append("INVALIDO")
    
    return l

def persist(el):
    global cur
    sql = f"insert into imoveis (titulo, tamanho, logradouro, bairro, cidade, estado, preco, regime, latitude, longitude) \
        values ('{el[0]}', {el[1]}, '{el[2]}', '{el[3]}', '{el[4]}', '{el[5]}', {el[6]}, '{el[7]}', '{el[8]}', '{el[9]}');"
    cur.execute(sql)

def principal(url):
    print("----------------PAGINA-----------------")
    print(url)
    adressClass = "property-card__address"
    titleClass = "property-card__title"
    priceClass = "property-card__price"

    r = requests.get(url).content

    data = BeautifulSoup(r, 'html.parser')

    adress = data.find_all('span', adressClass)
    title = data.find_all('span', titleClass)
    price = data.find_all('div', priceClass)

    if adress.__len__() == title.__len__():
            for i in range(adress.__len__()):
                el = montaLista(title[i].text, adress[i].text, price[i].find('p').text)
                el.append(regime)
                endereco = adress[i].text.replace('-', '').replace(',', '').replace(' ', '+')
                requestLatLon = requests.get(f"https://geocode.maps.co/search?q={endereco}")
                casa = json.loads(requestLatLon.text)
                try:
                    el.append(casa[0]['lat'])
                    el.append(casa[0]['lon'])
                except:
                    el.append('INVALIDO')
                if len(el) == 10:
                    #print(el)
                    persist(el)
            time.sleep(0.5)
            con.commit()
#34561
[principal(f"https://www.vivareal.com.br/{regime}/?pagina={i}") for i in range(1, 34562)]
