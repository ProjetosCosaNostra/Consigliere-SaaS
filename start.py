# Arquivo: E:\Consigliere\start.py
# Módulo: The Regent (System Launcher)
# Status: V1.0

import subprocess
import time
import os
import sys

def iniciar_sistema():
    print("==========================================")
    print("   🏛️  COSA NOSTRA FINANCIAL SYSTEM  🏛️")
    print("==========================================")
    print("1. Iniciando Protocolo de Segurança...")
    
    # Caminhos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, 'src')
    sentinela_script = os.path.join(src_dir, 'sentinela.py')
    app_script = os.path.join(src_dir, 'app.py')

    # Inicia a Sentinela em uma nova janela (independente)
    print("2. Acordando a Sentinela (Background)...")
    if sys.platform == 'win32':
        subprocess.Popen(f'start cmd /k python "{sentinela_script}"', shell=True)
    else:
        # Linux/Mac (Exemplo genérico, ajustável)
        subprocess.Popen(['python3', sentinela_script])

    time.sleep(2)

    # Inicia o Dashboard (Streamlit)
    print("3. Abrindo o Terminal do Don...")
    print(f"   > Carregando: {app_script}")
    os.system(f'streamlit run "{app_script}"')

if __name__ == "__main__":
    try:
        iniciar_sistema()
    except KeyboardInterrupt:
        print("\nSistema encerrado.")