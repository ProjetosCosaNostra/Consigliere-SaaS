# Arquivo: E:\Consigliere\src\cerebro.py
# Módulo: Math Core + Risk + Options (Black-Scholes)
# Status: v55.0 (The Armored - Crash Proof)

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta
from scipy.optimize import minimize
from scipy.stats import norm

# --- INDICADORES TÉCNICOS ---
def calcular_rsi(series, period=14):
    if len(series) < period: return pd.Series(50, index=series.index)
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calcular_atr(df, period=14):
    if df.empty or 'High' not in df.columns or 'Low' not in df.columns: return pd.Series(0, index=df.index if not df.empty else [])
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(window=period).mean()

def calcular_vwap(df):
    if df.empty or 'Volume' not in df.columns: return df['Close'] if not df.empty else pd.Series()
    v = df['Volume'].values
    p = df['Close'].values
    return (p * v).cumsum() / v.cumsum()

def calcular_vwap_bands(df):
    if df.empty: return pd.Series(), pd.Series(), pd.Series()
    vwap = calcular_vwap(df)
    rolling_std = df['Close'].rolling(20).std()
    upper = vwap + (2 * rolling_std)
    lower = vwap - (2 * rolling_std)
    return vwap, upper, lower

def calcular_macd(series):
    if len(series) < 26: return pd.Series(), pd.Series(), pd.Series()
    exp1 = series.ewm(span=12, adjust=False).mean()
    exp2 = series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist

def calcular_fibonacci(df):
    if df.empty or 'High' not in df.columns or 'Low' not in df.columns: return {}
    max_p = df['High'].max(); min_p = df['Low'].min(); diff = max_p - min_p
    return {'0%': min_p, '23.6%': min_p+0.236*diff, '38.2%': min_p+0.382*diff, '50%': min_p+0.5*diff, '61.8%': min_p+0.618*diff, '100%': max_p}

def identificar_padroes_candle(df):
    if df.empty or 'Open' not in df.columns: return []
    df = df.copy()
    df['Body'] = abs(df['Close'] - df['Open'])
    df['Wick_Upper'] = df['High'] - np.maximum(df['Close'], df['Open'])
    df['Wick_Lower'] = np.minimum(df['Close'], df['Open']) - df['Low']
    patterns = []
    for i in range(2, len(df)):
        curr = df.iloc[i]; date = df.index[i]
        if (curr['Wick_Lower'] > 2 * curr['Body']) and (curr['Wick_Upper'] < curr['Body'] * 0.2):
            patterns.append((date, curr['Low'], "🔨", "Bull"))
    return patterns

def calcular_suporte_resistencia_auto(df, window=20):
    if df.empty or 'Low' not in df.columns: return [], []
    df['Min'] = df['Low'].rolling(window, center=True).min()
    df['Max'] = df['High'].rolling(window, center=True).max()
    return df[df['Low']==df['Min']]['Low'].unique()[-3:], df[df['High']==df['Max']]['High'].unique()[-3:]

# --- INSTITUTIONAL TOOLS ---
def identificar_zonas_liquidez(df, n_zonas=3):
    if df.empty or 'Volume' not in df.columns: return []
    try:
        df = df.copy()
        df['Price_Bucket'] = pd.qcut(df['Close'], q=50, duplicates='drop')
        volume_profile = df.groupby('Price_Bucket')['Volume'].sum().sort_values(ascending=False)
        zonas = []
        for i in range(min(n_zonas, len(volume_profile))):
            zonas.append(volume_profile.index[i].mid)
        return zonas
    except: return []

def calcular_pressao_compradora(df):
    if df.empty or 'Volume' not in df.columns: return 50, 50
    df['Up'] = np.where(df['Close'] >= df['Open'], df['Volume'], 0)
    df['Down'] = np.where(df['Close'] < df['Open'], df['Volume'], 0)
    compradores = df['Up'].iloc[-20:].sum()
    vendedores = df['Down'].iloc[-20:].sum()
    total = compradores + vendedores
    pct_buy = (compradores / total * 100) if total > 0 else 50
    return pct_buy, 100 - pct_buy

def calcular_performance_trader(historico):
    if not historico: return None
    df = pd.DataFrame(historico)
    vendas = df[df['Op'] == 'V']
    if vendas.empty: return None
    total_trades = len(vendas)
    volume_total = (vendas['Qtd'] * vendas['Preço']).sum()
    return {'total_trades': total_trades, 'volume_girado': volume_total, 'ultimo_trade': vendas.iloc[0]['Data']}

def calcular_matriz_correlacao_raw(df_precos):
    if df_precos.empty: return pd.DataFrame()
    retornos = df_precos.pct_change().dropna()
    return retornos.corr()

# --- RISK (VaR, Stress & HEDGE) ---
def calcular_var_portfolio(portfolio, df_precos, confianca=0.95):
    ativos_validos = [a for a in portfolio.keys() if a != 'Caixa' and a in df_precos.columns]
    if not ativos_validos: return 0.0, 0.0
    
    valores = []
    for a in ativos_validos:
        qtd = portfolio[a]['qtd']
        preco = df_precos[a].iloc[-1]
        valores.append(qtd * preco)
        
    valor_total_ativos = sum(valores)
    if valor_total_ativos == 0: return 0.0, 0.0
    
    pesos = np.array(valores) / valor_total_ativos
    retornos = df_precos[ativos_validos].pct_change().dropna()
    if retornos.empty: return 0.0, 0.0
    
    cov_matrix = retornos.cov()
    port_vol_diaria = np.sqrt(np.dot(pesos.T, np.dot(cov_matrix, pesos)))
    z_score = norm.ppf(confianca)
    var_pct = port_vol_diaria * z_score
    var_financeiro = valor_total_ativos * var_pct
    
    return var_financeiro, var_pct * 100

def calcular_cvar_portfolio(portfolio, df_precos, confianca=0.95):
    ativos_validos = [a for a in portfolio.keys() if a != 'Caixa' and a in df_precos.columns]
    if not ativos_validos: return 0.0
    valores = [portfolio[a]['qtd'] * df_precos[a].iloc[-1] for a in ativos_validos]
    valor_total = sum(valores)
    if valor_total == 0: return 0.0
    pesos = np.array(valores) / valor_total
    retornos = df_precos[ativos_validos].pct_change().dropna()
    if retornos.empty: return 0.0
    retornos_port = retornos.dot(pesos)
    var_cutoff = retornos_port.quantile(1 - confianca)
    cvar_pct = retornos_port[retornos_port <= var_cutoff].mean()
    return abs(cvar_pct) * valor_total

def executar_stress_test(portfolio, df_precos, cenario_pct=-0.10, ativo_choque='^GSPC'):
    ativos_validos = [a for a in portfolio.keys() if a != 'Caixa' and a in df_precos.columns]
    if not ativos_validos: return 0.0, {}
    
    # Blindagem contra falta de benchmark
    if ativo_choque in df_precos.columns:
        ret_bench = df_precos[ativo_choque].pct_change().fillna(0)
    else:
        # Fallback: Usa média do mercado se S&P falhar
        ret_bench = df_precos.pct_change().mean(axis=1).fillna(0)
        
    impactos = {}
    perda_total = 0
    
    for a in ativos_validos:
        ret_ativo = df_precos[a].pct_change().fillna(0)
        # Verifica se tem dados suficientes
        if len(ret_ativo) < 2 or len(ret_bench) < 2:
            beta = 1.0
        else:
            try:
                cov = np.cov(ret_ativo, ret_bench)[0][1]
                var = np.var(ret_bench)
                beta = cov / var if var != 0 else 1.0
            except: beta = 1.0
            
        queda_estimada = beta * cenario_pct
        valor_posicao = portfolio[a]['qtd'] * df_precos[a].iloc[-1]
        perda_posicao = valor_posicao * queda_estimada
        impactos[a] = {'beta': beta, 'queda_est': queda_estimada * 100, 'perda_monetaria': perda_posicao}
        perda_total += perda_posicao
        
    return perda_total, impactos

# --- NOVO: HEDGE CALCULATOR (Black-Scholes) ---
def calcular_black_scholes(S, K, T, r, sigma, tipo='call'):
    if sigma == 0 or T == 0: return 0, 0
    d1 = (np.log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if tipo == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else: # Put
        price = K * np.exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
    return price, delta

def calcular_hedge_carteira(valor_carteira, beta_carteira, preco_indice, volatilidade_indice):
    nocional_risco = valor_carteira * beta_carteira
    S = preco_indice
    K = preco_indice 
    T = 1/12
    r = 0.11 
    sigma = volatilidade_indice
    
    preco_put, delta_put = calcular_black_scholes(S, K, T, r, sigma, 'put')
    
    if abs(delta_put) > 0:
        qtd_opcoes = nocional_risco / (S * abs(delta_put))
    else:
        qtd_opcoes = 0
        
    custo_seguro = qtd_opcoes * preco_put
    
    return {
        'Risco Beta Ajustado': nocional_risco,
        'Preço Put Teórica': preco_put,
        'Delta Put': delta_put,
        'Qtd Puts Necessárias': qtd_opcoes,
        'Custo Proteção (R$)': custo_seguro,
        'Custo % Carteira': (custo_seguro / valor_carteira) * 100 if valor_carteira > 0 else 0
    }

# --- INTELLIGENCE ---
def gerar_manchetes_algoritmicas(df_precos):
    manchetes = []
    if df_precos.empty: return ["Aguardando dados..."]
    ret = df_precos.pct_change().iloc[-1]
    for at, r in ret.items():
        rp = r*100
        if rp > 2: manchetes.append(f"🚀 {at} dispara {rp:.1f}%")
        elif rp < -2: manchetes.append(f"🩸 {at} cai {rp:.1f}%")
    return manchetes

def detectar_anomalias_zscore(df_precos, window=20, threshold=2.0):
    retornos = df_precos.pct_change()
    z_scores = (retornos - retornos.rolling(window).mean()) / retornos.rolling(window).std()
    ultimo_z = z_scores.iloc[-1]
    return ultimo_z[abs(ultimo_z) > threshold]

def calcular_market_breadth(df_precos):
    retornos = df_precos.pct_change().iloc[-1]
    return retornos[retornos > 0].count(), retornos[retornos < 0].count(), retornos[retornos == 0].count()

def calcular_rrg_lite(df_asset, df_bench, window=14):
    # BLINDAGEM: Se benchmark estiver vazio
    if df_bench.empty or df_asset.empty: return 0, 0, pd.Series(), pd.Series()
    
    df = pd.concat([df_asset['Close'], df_bench['Close']], axis=1, keys=['Asset', 'Bench']).dropna()
    if df.empty: return 0, 0, pd.Series(), pd.Series()
    
    rs_raw = df['Asset'] / df['Bench']
    rs_ratio = (rs_raw / rs_raw.rolling(window=window*2).mean()) * 100
    rs_momentum = (rs_ratio / rs_ratio.shift(window)) * 100
    return rs_ratio.iloc[-1], rs_momentum.iloc[-1], rs_ratio.tail(5), rs_momentum.tail(5)

def calcular_sentimento_global(macro_data):
    # BLINDAGEM: Se macro_data estiver vazio
    if not macro_data: return 50
    score = 50 + (macro_data.get('S&P 500', (0,0))[1] * 10) + (macro_data.get('Bitcoin', (0,0))[1] * 2) - (macro_data.get('Dólar', (0,0))[1] * 8)
    return max(0, min(100, score))

def analisar_sentimento_tecnico(df):
    if 'Volume' not in df.columns: return "⚖️ NEUTRO (Sem Vol)"
    ret = df['Close'].pct_change(5).iloc[-1]; vol = df['Volume'].iloc[-5:].mean(); vol_m = df['Volume'].rolling(20).mean().iloc[-1]
    if vol_m == 0: return "⚖️ NEUTRO"
    if ret > 0.05 and vol > vol_m * 1.2: return "🔥 EUFORIA"
    elif ret < -0.05 and vol > vol_m * 1.2: return "🩸 PÂNICO"
    else: return "⚖️ NEUTRO"

def detectar_baleia(df):
    if 'Volume' not in df.columns: return False
    if len(df) < 21: return False
    return df['Volume'].iloc[-1] > df['Volume'].iloc[-21:-1].mean() * 1.5

def calcular_beta_alpha(a, m):
    # BLINDAGEM: Verifica se séries são válidas
    if a.empty or m.empty: return 1.0, 0.0
    
    df = pd.concat([a, m], axis=1).dropna()
    if df.empty or len(df) < 10: return 1.0, 0.0
    
    try:
        beta = np.cov(df.iloc[:,0], df.iloc[:,1])[0][1] / np.var(df.iloc[:,1])
        alpha = (df.iloc[:,0].mean() - beta*df.iloc[:,1].mean()) * 252
        return beta, alpha
    except: return 1.0, 0.0

def calcular_zscore_arbitragem(a, b, w=20):
    """
    BLINDAGEM TOTAL: Se faltar dados, retorna 0 em vez de crashar.
    O erro da imagem (IndexError) acontece aqui se o DF ficar vazio.
    """
    if a.empty or b.empty: return pd.Series([0])
    
    # Tenta alinhar
    df = pd.concat([a, b], axis=1).dropna()
    
    # Se depois de alinhar ficar vazio (datas não batem), retorna 0
    if df.empty: return pd.Series([0])
    
    try:
        # AQUI OCORRIA O ERRO se df.iloc[0,0] não existisse
        base_a = df.iloc[0,0]
        base_b = df.iloc[0,1]
        
        if base_a == 0 or base_b == 0: return pd.Series([0])
        
        spread = (df.iloc[:,0] / base_a * 100) - (df.iloc[:,1] / base_b * 100)
        return ((spread - spread.rolling(w).mean()) / spread.rolling(w).std()).fillna(0)
    except:
        return pd.Series([0]) # Retorno de segurança

def calcular_sazonalidade(df):
    d = df.copy(); d['Y'] = d.index.year; d['M'] = d.index.month; d['R'] = d['Close'].pct_change()
    return d.groupby(['Y', 'M'])['R'].sum().unstack() * 100

def calcular_score(rsi, pl, dy, desc):
    s = 50 + (25 if rsi<30 else -25 if rsi>70 else 0) + (20 if 0<pl<10 else 0) + (15 if dy>6 else 0) + (15 if desc<-30 else 0)
    return max(0, min(100, s))

def calcular_setup_trade(p, atr):
    s = p - 2*atr; t = p + 3*atr
    return s, t, ((t-p)/(p-s)) if p>s else 0

def calcular_tamanho_posicao(c, r, e, s):
    dist = e - s
    return int((c*(r/100))/dist) if dist > 0 else 0

def gerar_relatorio_tactico(t, s, r, pl, dy, atr, roe, mrg, sent):
    txt = f"### 📝 Dossiê: {t}\n**SENTIMENTO:** {sent}\n"
    if s>=75: txt+="**VEREDITO: BUY**\n"
    elif s>=50: txt+="**VEREDITO: HOLD**\n"
    else: txt+="**VEREDITO: SELL**\n"
    txt+=f"- ⚡ **Vol:** {atr:.2f}"
    return txt

def projecao_propheta(hist, dias=30):
    if hist.empty: return [], [], 0
    last = pd.to_datetime(hist.index[-1])
    df = hist.reset_index(); X = np.arange(len(df)).reshape(-1,1); y=df['Close'].values
    mod = LinearRegression().fit(X,y)
    fut = np.arange(len(df), len(df)+dias).reshape(-1,1)
    return [last + timedelta(days=i) for i in range(1, dias+1)], mod.predict(fut), np.std(y-mod.predict(X))

def monte_carlo_sim(p, c, d=252, s=50):
    r = p.pct_change().dropna()
    if r.empty: return np.zeros((d, s))
    mu = r.mean(); cov = r.cov(); w = np.full(len(p.columns), 1/len(p.columns))
    re = np.sum(mu*w); ve = np.sqrt(np.dot(w.T, np.dot(cov, w)))
    paths = np.zeros((d, s))
    for i in range(s):
        val = [c]; pr = c
        for _ in range(d):
            pr *= (1 + np.random.normal(re, ve))
            val.append(pr)
        paths[:,i] = val[1:]
    return paths

def otimizar_portfolio(p):
    r = p.pct_change().dropna()
    if r.empty: return {}
    mu = r.mean()*252; cov = r.cov()*252; n = len(p.columns)
    def ns(w): 
        risk = np.sqrt(np.dot(w.T, np.dot(cov, w)))
        if risk == 0: return 0
        return -(np.sum(mu*w)/risk)
    res = minimize(ns, np.full(n, 1/n), method='SLSQP', bounds=tuple((0,1) for _ in range(n)), constraints=({'type':'eq', 'fun':lambda x:np.sum(x)-1}))
    return dict(zip(p.columns, res.x))

def gerar_rebalanceamento(port, prices, weights):
    if not weights: return pd.DataFrame()
    caixa = port.get('Caixa', 0)
    val = sum([d['qtd']*prices.get(a,0) if isinstance(d,dict) else d*prices.get(a,0) for a,d in port.items() if a!='Caixa'])
    tot = caixa + val
    ords = []
    for a, w in weights.items():
        p = prices.get(a,0)
        if p > 0:
            tgt = tot * w
            cur = port.get(a,{'qtd':0})['qtd']*p if isinstance(port.get(a,0),dict) else port.get(a,0)*p
            diff = tgt - cur
            q = int(diff/p)
            if abs(q)>0: ords.append({'Ativo':a, 'Ação': "COMPRAR" if q>0 else "VENDER", 'Qtd': abs(q), 'Preço': p, 'Fin': abs(q*p), 'Peso Ideal': w*100})
    return pd.DataFrame(ords)

def analisar_risco_portfolio(port, prices, betas):
    tot = 0; w = {}
    for a, d in port.items():
        if a == 'Caixa': tot += d
        else:
            q = d['qtd'] if isinstance(d, dict) else d
            p = prices.get(a, 0); v = q*p; tot += v; w[a] = v
    if tot == 0: return 0, []
    beta_p = 0; alerts = []
    for a, v in w.items():
        perm = v/tot
        # Proteção se não tiver beta
        b = betas.get(a, 1.0)
        beta_p += perm * b
        if perm > 0.25: alerts.append(f"⚠️ CONCENTRAÇÃO: {a} ({perm*100:.1f}%)")
    return beta_p, alerts