import sys
import types

"""
Este patch é necessário para evitar erros de importação do 'torch.classes' em ambientes 
específicos (como Streamlit Cloud) onde o PyTorch pode não estar completamente inicializado 
ou onde certas dependências opcionais causam conflito.
Mantenha este arquivo a menos que tenha certeza de que o ambiente suporta torch.classes nativamente.
"""
sys.modules['torch.classes'] = types.ModuleType('torch.classes')
