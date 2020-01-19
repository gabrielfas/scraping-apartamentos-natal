# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import warnings
import datetime
import time
warnings.filterwarnings('ignore')

def tratar_caracteristicas(link):
  caract = link.find('p', class_='text detail-specific').text.strip().split('|')

  tipo, quartos, tamanho, valor_cond = ('', '', '', '')

  for i in range(len(caract)):
    if 'Condomínio' in caract[i].strip():
      valor_cond = caract[i].strip()
    elif 'quartos' in caract[i].strip():
      quartos = caract[i].strip()
    elif 'm²' in caract[i].strip():
      tamanho = caract[i].strip()
    elif ('À venda' in caract[i].strip()) or ('Para alugar' in caract[i].strip()):
      tipo = caract[i].strip()

  return tipo, quartos, tamanho, valor_cond

def tratar_anuncio(tipo_anuncio):
  if tipo_anuncio is None:
    tipo_anuncio = ''
  else:
    tipo_anuncio = link.find('span').text.strip()
    
  return tipo_anuncio

def tratar_dia_hora(dia, hora):
  if dia == 'Hoje':
    hoje = datetime.date.today()
    dia = hoje.strftime("%d %b")
  elif dia == 'Ontem':
    hoje = datetime.date.today()
    ontem = hoje - datetime.timedelta(days = 1)
    dia = ontem.strftime("%d %b")
  return dia, hora

def recuperar_dados(link):
  global apts
  titulo = link.find('h2', class_='OLXad-list-title').text.strip()
  tipo, quartos, tamanho, valor_cond =  tratar_caracteristicas(link)
  bairro = link.find('p', class_='text detail-region').text.split(',')[1].strip()
  categoria = link.find('p', class_='text detail-category').text.split()[0].strip()
  valor = link.find('div', class_='col-3').text.strip().split('\n')[0].strip()
  tipo_anuncio = tratar_anuncio(link.find('span'))
  dia_publi, hora_publi = tratar_dia_hora(link.find_all('p', class_='text mb5px')[0].text.strip(), 
                                          link.find_all('p', class_='text mb5px')[1].text.strip())
  apts.append([titulo, tipo, quartos, tamanho, valor_cond, bairro, 
               categoria, valor, tipo_anuncio, dia_publi, hora_publi])

def exportar_dataset(dataset):
  print('Exportando dataset para CSV...')
  colunas = ['Titulo', 'Tipo', 'Numero de quartos', 'Tamanho (m2)', 
             'Valor do condominio (R$)', 'Bairro', 'Categoria', 'Valor (R$)', 
             'Tipo do anuncio','Dia da publicacao', 'Hora da publicacao']
  
  df = pd.DataFrame(apts, columns=colunas)

  df['Valor do condominio (R$)'] = df['Valor do condominio (R$)'].apply(lambda x: np.nan if x == '' else x.split()[-1]).astype('float')
  df['Numero de quartos'] = df['Numero de quartos'].apply(lambda x: np.nan if x == '' else x.split()[0]).astype('float')
  df['Tamanho (m2)'] = df['Tamanho (m2)'].apply(lambda x: np.nan if x == '' else x.split()[0]).astype('float')
  df['Valor (R$)'] = df['Valor (R$)'].apply(lambda x: np.nan if x == '' else ''.join(x.split()[-1].split('.'))).astype('float')
  df['Tipo do anuncio'] = df['Tipo do anuncio'].apply(lambda x: '' if x == 'sem foto' else x)
  df = df[df['Categoria'] == 'Apartamentos']

  df.to_csv('Apartamentos Natal.csv', index=False)

if __name__ == "__main__":
  apts = []

  print('Coletando dados...')

  for n in range(1,101):
    url = "https://rn.olx.com.br/rio-grande-do-norte/natal/imoveis?o=" + str(n) + "&q=Apartamentos&sf=1"

    r = requests.get(url)
    time.sleep(2)
  
    html_doc = r.text

    soup = BeautifulSoup(html_doc, "html5lib")

    lista = soup.find('ul', id='main-ad-list', class_='list')
  
    try:
      links = lista.find_all('a')
    except:
      continue

    for link in links:
      recuperar_dados(link)

    print('Pag ', n, ' coletada com sucesso...')

print('Total de ', str(len(apts)/50), ' pags coletadas...')
print('Total de ', str(len(apts)), ' registros coletados...')

exportar_dataset(apts)
