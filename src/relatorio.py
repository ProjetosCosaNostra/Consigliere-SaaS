# Arquivo: E:\Consigliere\src\relatorio.py
# Módulo: The Scribe (Gerador de Dossiê PDF)
# Status: V1.0 - Institutional Grade

from fpdf import FPDF
from datetime import datetime
import pandas as pd

class PDF(FPDF):
    def header(self):
        # Fundo do Cabeçalho (Preto)
        self.set_fill_color(10, 10, 10)
        self.rect(0, 0, 210, 40, 'F')
        
        # Título (Dourado)
        self.set_font('Arial', 'B', 24)
        self.set_text_color(212, 175, 55) # Dourado
        self.cell(0, 15, 'CONSIGLIERE', 0, 1, 'C')
        
        # Subtítulo (Branco)
        self.set_font('Arial', '', 10)
        self.set_text_color(255, 255, 255)
        self.cell(0, 5, 'COSA NOSTRA HOLDING | DAILY INTELLIGENCE REPORT', 0, 1, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def gerar_dossie(portfolio, historico_trades, sentimento, macro):
    """
    Gera um PDF com o resumo do estado atual.
    Retorna os bytes do PDF.
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- 1. RESUMO EXECUTIVO ---
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, '1. EXECUTIVE SUMMARY', 0, 1, 'L')
    pdf.line(10, 50, 200, 50)
    pdf.ln(5)
    
    # Cálculos Rápidos
    caixa = portfolio.get('Caixa', 0)
    valor_ativos = sum([d['qtd'] * d['pm'] for a, d in portfolio.items() if a != 'Caixa']) # Usando PM como base simples aqui
    total = caixa + valor_ativos
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(50, 10, f"Net Worth Total:", 0, 0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(50, 10, f"R$ {total:,.2f}", 0, 1)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(50, 10, f"Caixa Disponivel:", 0, 0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(50, 10, f"R$ {caixa:,.2f}", 0, 1)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(50, 10, f"Sentimento Mercado:", 0, 0)
    
    cor_sent = (0, 128, 0) if sentimento > 60 else (128, 0, 0) if sentimento < 40 else (200, 150, 0)
    pdf.set_text_color(*cor_sent)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(50, 10, f"{sentimento}/100", 0, 1)
    pdf.set_text_color(0, 0, 0) # Reset cor
    
    pdf.ln(10)
    
    # --- 2. POSIÇÕES ATUAIS ---
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '2. ACTIVE POSITIONS', 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Cabeçalho Tabela
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 10, 'Ativo', 1, 0, 'C', 1)
    pdf.cell(40, 10, 'Qtd', 1, 0, 'C', 1)
    pdf.cell(40, 10, 'Preco Medio', 1, 0, 'C', 1)
    pdf.cell(40, 10, 'Total Investido', 1, 1, 'C', 1)
    
    pdf.set_font('Arial', '', 10)
    tem_posicao = False
    for a, d in portfolio.items():
        if a != 'Caixa':
            tem_posicao = True
            q = d['qtd']
            pm = d['pm']
            tot = q * pm
            pdf.cell(40, 10, str(a), 1, 0, 'C')
            pdf.cell(40, 10, f"{q:.2f}", 1, 0, 'C')
            pdf.cell(40, 10, f"R$ {pm:.2f}", 1, 0, 'C')
            pdf.cell(40, 10, f"R$ {tot:.2f}", 1, 1, 'C')
            
    if not tem_posicao:
        pdf.cell(160, 10, "Nenhuma posicao ativa.", 1, 1, 'C')
        
    pdf.ln(10)
    
    # --- 3. INTELLIGENCE (MACRO) ---
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '3. MACRO SNAPSHOT', 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font('Courier', '', 11)
    for k, v in macro.items():
        pdf.cell(0, 8, f"{k}: {v[0]:,.2f} ({v[1]:+.2f}%)", 0, 1)
        
    pdf.ln(10)
    
    # --- 4. ÚLTIMAS OPERAÇÕES ---
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '4. RECENT ACTIVITY', 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    if historico_trades:
        # Pega os últimos 5
        ultimos = historico_trades[-5:]
        ultimos.reverse() # Mais recente primeiro
        
        for trade in ultimos:
            sinal = "[+]" if trade['Op'] == 'C' else "[-]"
            txt = f"{trade['Data']} | {sinal} {trade['Op']} {trade['Qtd']}x {trade['Ativo']} @ {trade['Preço']:.2f}"
            pdf.set_font('Courier', '', 10)
            pdf.cell(0, 8, txt, 0, 1)
            if trade.get('Nota'):
                pdf.set_font('Arial', 'I', 8)
                pdf.cell(0, 5, f"   Obs: {trade['Nota']}", 0, 1)
    else:
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, "Sem historico recente.", 0, 1)

    # Output
    # Retorna o string binário do PDF para download
    return pdf.output(dest='S').encode('latin-1')