import sys
import os

# Adiciona o diretório raiz do projeto ao PYTHONPATH
# Isso permite que os testes importem "src.*" sem problemas.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
