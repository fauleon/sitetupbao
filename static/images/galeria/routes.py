# app/galeria/routes.py

from flask import Blueprint, render_template, abort
import os

galeria_bp = Blueprint('galeria', __name__, template_folder='../templates/galeria')

# Define os álbuns da galeria. O 'slug' deve ser o mesmo nome da pasta de imagens.
ALBUNS = [
    {'slug': 'trabalhos-gira', 'titulo': 'Trabalhos de Gira', 'descricao': 'Registros dos nossos rituais de fé e caridade.'},
    {'slug': 'trabalhos-sociais', 'titulo': 'Trabalhos Sociais', 'descricao': 'Ações de amor ao próximo e ajuda à comunidade.'},
    {'slug': 'maos-que-ajudam', 'titulo': 'Mãos que Ajudam', 'descricao': 'Projetos e iniciativas de auxílio e doação.'},
    {'slug': 'aulas-curimba', 'titulo': 'Aulas de Curimba', 'descricao': 'O aprendizado e a vibração dos nossos atabaques.'},
]

# Rota para a página principal da galeria, que mostra todos os álbuns
@galeria_bp.route('/')
def index():
    # Adiciona a primeira imagem de cada álbum para usar como capa
    for album in ALBUNS:
        caminho_pasta = os.path.join('app', 'static', 'images', 'galeria', album['slug'])
        try:
            imagens = sorted([img for img in os.listdir(caminho_pasta) if img.lower().endswith(('.png', '.jpg', '.jpeg'))])
            album['imagem_capa'] = imagens[0] if imagens else 'placeholder.png'
        except FileNotFoundError:
            album['imagem_capa'] = 'placeholder.png' # Imagem padrão se a pasta não existir
            
    return render_template('galeria_index.html', albuns=ALBUNS)

# Rota para mostrar as fotos de um álbum específico
@galeria_bp.route('/<string:album_slug>')
def ver_album(album_slug):
    # Encontra o álbum correspondente ao slug da URL
    album_selecionado = next((album for album in ALBUNS if album['slug'] == album_slug), None)
    
    if not album_selecionado:
        abort(404) # Se não encontrar o álbum, retorna erro 404

    # Carrega a lista de nomes de arquivos de imagem da pasta correta
    caminho_pasta = os.path.join('app', 'static', 'images', 'galeria', album_slug)
    try:
        lista_imagens = sorted([img for img in os.listdir(caminho_pasta) if img.lower().endswith(('.png', '.jpg', '.jpeg'))])
    except FileNotFoundError:
        lista_imagens = []

    album_selecionado['imagens'] = lista_imagens
    
    return render_template('album_fotos.html', album=album_selecionado)
