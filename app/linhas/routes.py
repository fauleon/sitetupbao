# app/linhas/routes.py (Pode usar este mesmo código para comunidade/routes.py)
# Apenas um placeholder para não dar erro

from flask import Blueprint, render_template

# Mude 'linhas' para 'comunidade' no outro ficheiro
linhas_bp = Blueprint('linhas', __name__, template_folder='../templates/linhas')

@linhas_bp.route('/')
def index():
    # Crie um template simples ou apenas retorne um texto
    return "<h1>Página de Linhas em Construção</h1>"

# Para comunidade/routes.py:
# comunidade_bp = Blueprint('comunidade', __name__, template_folder='../templates/comunidade')
# @comunidade_bp.route('/')
# def index():
#     return "<h1>Página da Comunidade em Construção</h1>"
