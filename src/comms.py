# Arquivo: E:\Consigliere\src\comms.py
# Módulo: The Voice (Sistema de Notificações Telegram)
# Status: V1.0 - Implementado

import requests

def enviar_telegram(token, chat_id, mensagem):
    """
    Envia mensagens de alerta para o Telegram do usuário.
    Requer Bot Token e Chat ID (pegos com @BotFather e @userinfobot).
    """
    if not token or not chat_id:
        return False, "Token ou ID não configurados."
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            return True, "Mensagem enviada com sucesso."
        else:
            return False, f"Erro Telegram: {response.text}"
    except Exception as e:
        return False, f"Erro de Conexão: {e}"

def formatar_alerta_sinal(ativo, sinal, valor, indicador):
    """Formata uma mensagem padrão de sinal técnico."""
    icon = "🟢" if "COMPRA" in sinal or "OVERSOLD" in sinal else "🔴"
    return (
        f"*{icon} CONSIGLIERE ALERT*\n"
        f"---------------------------\n"
        f"🎯 *Ativo:* `{ativo}`\n"
        f"📊 *Sinal:* {sinal}\n"
        f"📉 *Indicador:* {indicador} ({valor:.2f})\n"
        f"---------------------------\n"
        f"Verifique o terminal imediatamente."
    )

def formatar_alerta_baleia(ativo, volume_ratio):
    """Alerta específico para volume anormal (Baleias)."""
    return (
        f"*🐋 WHALE ALERT DETECTED*\n"
        f"---------------------------\n"
        f"🌊 *Ativo:* `{ativo}`\n"
        f"⚠️ *Volume:* {volume_ratio:.1f}x a média!\n"
        f"Movimentação institucional detectada.\n"
        f"---------------------------"
    )