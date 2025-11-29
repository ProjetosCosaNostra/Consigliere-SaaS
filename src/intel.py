# Arquivo: E:\Consigliere\src\intel.py
# Módulo: The Eyes (Coleta de Notícias e OSINT)
# Status: V1.0 - Real Time Intelligence

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import re

def buscar_noticias_google(termo="Mercado Financeiro Brasil", limite=5):
    """
    Busca notícias reais via RSS do Google News.
    Não requer API Key. É robusto e direto.
    """
    url = f"https://news.google.com/rss/search?q={termo}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return []
        
        root = ET.fromstring(resp.content)
        noticias = []
        
        # Itera sobre os itens do XML
        for item in root.findall('./channel/item')[:limite]:
            titulo = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text
            
            # Limpeza do título (Remove o nome da fonte no final, ex: "... - InfoMoney")
            titulo_limpo = titulo.rsplit(' - ', 1)[0]
            fonte = titulo.rsplit(' - ', 1)[1] if ' - ' in titulo else "Google News"
            
            sentimento, score = analisar_sentimento_rapido(titulo_limpo)
            
            noticias.append({
                'titulo': titulo_limpo,
                'link': link,
                'fonte': fonte,
                'sentimento': sentimento,
                'score': score
            })
            
        return noticias
    except Exception as e:
        print(f"Erro na coleta de intel: {e}")
        return []

def analisar_sentimento_rapido(texto):
    """
    Análise de sentimento baseada em dicionário (Bag of Words)
    Para velocidade extrema antes de usar LLMs pesadas.
    """
    texto = texto.lower()
    
    bullish_terms = ['alta', 'sobe', 'dispara', 'lucro', 'recorde', 'compra', 'otimismo', 'positivo', 'supera', 'dividendos', 'cresce']
    bearish_terms = ['queda', 'cai', 'desaba', 'prejuízo', 'crise', 'risco', 'medo', 'negativo', 'inflação', 'juros', 'recessão']
    
    score = 0
    for w in bullish_terms:
        if w in texto: score += 1
    for w in bearish_terms:
        if w in texto: score -= 1
        
    if score > 0: return "🟢 BULLISH", score
    elif score < 0: return "🔴 BEARISH", score
    else: return "⚖️ NEUTRO", score

def formatar_noticia_html(noticia):
    """Formata a notícia para o Sidebar do Streamlit"""
    cor = "#ccc" # Neutro
    if "BULLISH" in noticia['sentimento']: cor = "#00FF00"
    if "BEARISH" in noticia['sentimento']: cor = "#FF4B4B"
    
    html = f"""
    <div style="padding: 8px; border-bottom: 1px solid #333;">
        <a href="{noticia['link']}" target="_blank" style="text-decoration: none; color: {cor}; font-weight: bold; font-size: 0.85em;">
            {noticia['titulo']}
        </a>
        <div style="font-size: 0.7em; color: #888; margin-top: 2px;">
            {noticia['fonte']} • {noticia['sentimento']}
        </div>
    </div>
    """
    return html