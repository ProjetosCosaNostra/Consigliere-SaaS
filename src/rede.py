# Arquivo: E:\Consigliere\src\rede.py
# Módulo: The Network (Correlation Graph Theory)
# Status: V1.0

import pandas as pd
import networkx as nx
import plotly.graph_objects as go

def gerar_grafo_correlacao(df_precos, threshold=0.75):
    """
    Cria um grafo onde:
    - Nós (Nodes) = Ativos
    - Linhas (Edges) = Correlação forte (acima do threshold)
    Retorna uma figura Plotly interativa.
    """
    if df_precos.empty: return None

    # 1. Calcula Matriz de Correlação
    retornos = df_precos.pct_change().dropna()
    corr_matrix = retornos.corr()
    
    # 2. Cria o Grafo
    G = nx.Graph()
    ativos = corr_matrix.columns.tolist()
    
    # Adiciona Nós
    for ativo in ativos:
        G.add_node(ativo)
    
    # Adiciona Arestas (Conexões)
    for i in range(len(ativos)):
        for j in range(i+1, len(ativos)):
            ativo_a = ativos[i]
            ativo_b = ativos[j]
            correlacao = corr_matrix.loc[ativo_a, ativo_b]
            
            # Só cria linha se a correlação for forte (positiva ou negativa)
            if abs(correlacao) >= threshold:
                # Peso da linha = força da correlação
                G.add_edge(ativo_a, ativo_b, weight=correlacao)
                
    # 3. Layout do Grafo (Posicionamento Fruchterman-Reingold)
    # Isso agrupa ativos conectados visualmente
    try:
        pos = nx.spring_layout(G, k=0.5, iterations=50)
    except:
        # Fallback se der erro no layout
        pos = nx.circular_layout(G)
    
    # 4. Construção Visual (Plotly)
    edge_x = []
    edge_y = []
    edge_colors = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Cor da linha: Verde (Anda Junto) ou Vermelho (Anda Inverso)
        c = edge[2]['weight']
        edge_colors.append('#00FF00' if c > 0 else '#FF0000')

    # Desenha Linhas
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'), # Cor base cinza, simplificada
        hoverinfo='none',
        mode='lines')

    # Desenha Nós
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Texto ao passar o mouse: Nome + Conexões
        conexoes = len(list(G.neighbors(node)))
        node_text.append(f"{node}<br>Conexões Fortes: {conexoes}")
        
        # Cor do Nó baseada na Centralidade (Grau de Conexão)
        node_color.append(conexoes)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[str(n) for n in G.nodes()],
        textposition="top center",
        textfont=dict(color='white'),
        hoverinfo='text',
        hovertext=node_text,
        marker=dict(
            showscale=True,
            colorscale='Bluered',
            reversescale=False,
            color=node_color,
            size=25,
            colorbar=dict(
                thickness=15,
                title='Influência',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    # Monta a Figura
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title=f'Network Map (Threshold: {threshold})',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    plot_bgcolor='#000000',
                    paper_bgcolor='#000000',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    return fig