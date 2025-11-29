# Arquivo: E:\Consigliere\src\oraculo.py
# Módulo: The Oracle v1.1 (Persistência de Memória)
# Status: Production Ready

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib # BIBLIOTECA PARA SALVAR A IA
import os
import datetime

# Pasta para salvar os cérebros dos ativos
MODEL_DIR = "modelos_ia"
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

def preparar_dados_ml(df):
    """
    Cria 'features' (variáveis) para a IA aprender.
    """
    df = df.copy()
    df['Retorno'] = df['Close'].pct_change()
    df['Volatilidade'] = df['Retorno'].rolling(5).std()
    df['RSI'] = calcular_rsi_interno(df['Close'])
    df['Momentum'] = df['Close'] - df['Close'].shift(4)
    df['SMA_Diff'] = df['Close'] - df['Close'].rolling(20).mean()
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    return df.dropna()

def calcular_rsi_interno(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def prever_tendencia_ml(ticker, df_original):
    """
    Treina OU carrega um modelo para esse ativo.
    """
    if len(df_original) < 100:
        return 50.0, 0.0, "Dados Insuficientes"
    
    nome_arquivo_modelo = f"{MODEL_DIR}/modelo_{ticker}.pkl"
    modelo = None
    acuracia = 0.0
    
    # --- MELHORIA: Verifica se já existe um modelo treinado hoje ---
    re_treinar = True
    if os.path.exists(nome_arquivo_modelo):
        tempo_modificacao = os.path.getmtime(nome_arquivo_modelo)
        idade_arquivo = datetime.datetime.now().timestamp() - tempo_modificacao
        # Se o modelo tem menos de 24 horas (86400 seg), usamos ele
        if idade_arquivo < 86400:
            try:
                dados_modelo = joblib.load(nome_arquivo_modelo)
                modelo = dados_modelo['model']
                acuracia = dados_modelo['acc']
                re_treinar = False
            except:
                re_treinar = True

    features = ['Retorno', 'Volatilidade', 'RSI', 'Momentum', 'SMA_Diff']
    
    if re_treinar:
        try:
            dados = preparar_dados_ml(df_original)
            X = dados[features]
            y = dados['Target']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
            
            modelo = RandomForestClassifier(n_estimators=100, min_samples_split=10, random_state=42)
            modelo.fit(X_train, y_train)
            
            preds = modelo.predict(X_test)
            acuracia = accuracy_score(y_test, preds) * 100
            
            # Salva o modelo no disco
            joblib.dump({'model': modelo, 'acc': acuracia}, nome_arquivo_modelo)
        except Exception as e:
            return 50.0, 0.0, f"Erro Treino: {e}"

    # Previsão
    try:
        # Recalcula features recentes
        df_recente = df_original.iloc[-30:].copy()
        df_recente['Retorno'] = df_recente['Close'].pct_change()
        df_recente['Volatilidade'] = df_recente['Retorno'].rolling(5).std()
        df_recente['RSI'] = calcular_rsi_interno(df_recente['Close'])
        df_recente['Momentum'] = df_recente['Close'] - df_recente['Close'].shift(4)
        df_recente['SMA_Diff'] = df_recente['Close'] - df_recente['Close'].rolling(20).mean()
        
        input_predicao = df_recente.iloc[[-1]][features].fillna(0)
        probabilidade = modelo.predict_proba(input_predicao)[0][1] * 100
        
        sinal = "NEUTRO"
        if probabilidade > 60: sinal = "ALTA PROVÁVEL 🟢"
        elif probabilidade < 40: sinal = "BAIXA PROVÁVEL 🔴"
        
        return probabilidade, acuracia, sinal
        
    except Exception as e:
        return 50.0, 0.0, f"Erro Predição: {e}"