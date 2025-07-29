# aplicacao.py
import os
import datetime
import copy
from flask import Flask, render_template, abort
from jinja2 import FileSystemLoader # Importação adicional
import pandas as pd

# --- CONFIGURAÇÃO DA APLICAÇÃO (COM CAMINHOS ABSOLUTOS E ROBUSTOS) ---
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    # Removido o template_folder daqui para uma configuração mais explícita abaixo
    static_folder=os.path.join(basedir, 'static')
)

# --- CORREÇÃO FINAL E EXPLÍCITA PARA O CARREGADOR DE TEMPLATES ---
# Esta abordagem força o Jinja2 a usar o caminho absoluto que definimos.
template_dir = os.path.join(basedir, 'templates')
app.jinja_loader = FileSystemLoader(template_dir)
# --- FIM DA CORREÇÃO ---


# --- LÓGICA PARA CARREGAR OS DADOS DOS PONTOS ---
def carregar_dados_do_csv():
    caminho_csv = os.path.join(basedir, 'dados_formatados.xlsx - Sheet1.csv')
    if not os.path.exists(caminho_csv):
        print(f"AVISO: Ficheiro '{caminho_csv}' não encontrado.")
        return {}
    try:
        df = pd.read_csv(caminho_csv, dtype=str)
        df.fillna('', inplace=True)
    except Exception as e:
        print(f"ERRO ao ler o ficheiro CSV: {e}")
        return {}

    dados_organizados = {
        "entidades": {"linhas": {}}, "orixas": {"linhas": {}}, "ritualisticas": {"linhas": {}}
    }
    for _, row in df.iterrows():
        categoria_principal = str(row.get('Categoria_Principal', '')).strip()
        linha_trabalho = str(row.get('Linha_Trabalho', '')).strip()
        if not linha_trabalho: continue

        chave_categoria = None
        if "Entidades" in categoria_principal: chave_categoria = "entidades"
        elif "Orixas" in categoria_principal or "Orixás" in categoria_principal: chave_categoria = "orixas"
        elif "Rituais" in categoria_principal or "Ritualisticas" in categoria_principal: chave_categoria = "ritualisticas"
        if not chave_categoria: continue

        sub_categoria = str(row.get('Sub_Categoria', 'Pontos Gerais')).strip()
        if not sub_categoria or sub_categoria.lower() in ['n/a', 'nan']: sub_categoria = 'Pontos Gerais'
        nome_ponto = str(row.get('Nome_Ponto', '')).strip()
        if not nome_ponto or nome_ponto == 'Nome_Ponto': continue

        if linha_trabalho not in dados_organizados[chave_categoria]["linhas"]:
            slug = linha_trabalho.lower().replace(' ', '-').replace('ã', 'a').replace('ç', 'c').replace('ó', 'o')
            dados_organizados[chave_categoria]["linhas"][linha_trabalho] = {"linha_nome": linha_trabalho, "linha_slug": slug, "sub_categorias": {}}
        
        if sub_categoria not in dados_organizados[chave_categoria]["linhas"][linha_trabalho]["sub_categorias"]:
            dados_organizados[chave_categoria]["linhas"][linha_trabalho]["sub_categorias"][sub_categoria] = {"titulo": sub_categoria, "pontos": []}
            
        youtube_id = ""
        link_youtube = str(row.get('Link_Youtube', '')).strip()
        if 'v=' in link_youtube: youtube_id = link_youtube.split('v=')[1].split('&')[0]
        
        dados_organizados[chave_categoria]["linhas"][linha_trabalho]["sub_categorias"][sub_categoria]["pontos"].append({
            "nome": nome_ponto, "toque": str(row.get('Tipo_Toque', '')).strip(), "youtube_id": youtube_id
        })

    final_data = {}
    for cat_key, cat_data in dados_organizados.items():
        final_data[cat_key] = {"linhas": sorted(list(cat_data["linhas"].values()), key=lambda x: x['linha_nome'])}
        for linha in final_data[cat_key]["linhas"]:
            linha["sub_categorias"] = sorted(list(linha["sub_categorias"].values()), key=lambda x: x['titulo'])
    return final_data

DADOS_PONTOS = carregar_dados_do_csv()
DADOS_PONTOS_ENTIDADES = DADOS_PONTOS.get("entidades", {}).get("linhas", [])
DADOS_PONTOS_ORIXAS = DADOS_PONTOS.get("orixas", {}).get("linhas", [])
DADOS_PONTOS_RITUAIS = DADOS_PONTOS.get("ritualisticas", {}).get("linhas", [])

# --- LÓGICA DA GALERIA ---
ALBUNS = [
    {'slug': 'trabalhos-gira', 'titulo': 'Trabalhos de Gira', 'descricao': 'Registros dos nossos rituais de fé e caridade.'},
    {'slug': 'trabalhos-sociais', 'titulo': 'Trabalhos Sociais', 'descricao': 'Ações de amor ao próximo e ajuda à comunidade.'},
    {'slug': 'maos-que-ajudam', 'titulo': 'Mãos que Ajudam', 'descricao': 'Projetos e iniciativas de auxílio e doação.'},
    {'slug': 'aulas-curimba', 'titulo': 'Aulas de Curimba', 'descricao': 'O aprendizado e a vibração dos nossos atabaques.'},
]

# --- DISPONIBILIZAR VARIÁVEIS GLOBAIS PARA OS TEMPLATES ---
@app.context_processor
def inject_global_vars():
    return dict(
        year=datetime.date.today().year,
        TODAS_LINHAS_ENTIDADES=DADOS_PONTOS_ENTIDADES,
        TODAS_LINHAS_ORIXAS=DADOS_PONTOS_ORIXAS,
        TODAS_LINHAS_RITUAIS=DADOS_PONTOS_RITUAIS
    )

# --- ROTAS (URLS) DO SITE ---

# Rota Principal
@app.route('/')
def index():
    return render_template('index.html')

# Rotas dos Pontos
def find_linha_by_slug(slug, lista_de_linhas):
    return next((linha for linha in lista_de_linhas if linha["linha_slug"] == slug), None)

@app.route('/pontos/entidades/<string:linha_slug>')
def page_linha_entidade(linha_slug):
    linha_encontrada = find_linha_by_slug(linha_slug, DADOS_PONTOS_ENTIDADES)
    if not linha_encontrada: abort(404)
    return render_template('pontos/lista_pontos.html', linha=linha_encontrada)

@app.route('/pontos/orixas/<string:linha_slug>')
def page_linha_orixa(linha_slug):
    linha_encontrada = find_linha_by_slug(linha_slug, DADOS_PONTOS_ORIXAS)
    if not linha_encontrada: abort(404)
    return render_template('pontos/lista_pontos.html', linha=linha_encontrada)

@app.route('/pontos/rituais/<string:linha_slug>')
def page_linha_ritual(linha_slug):
    linha_encontrada = find_linha_by_slug(linha_slug, DADOS_PONTOS_RITUAIS)
    if not linha_encontrada: abort(404)
    return render_template('pontos/lista_pontos.html', linha=linha_encontrada)

# Rotas da Galeria
@app.route('/galeria/')
def galeria_index():
    albuns_com_capa = copy.deepcopy(ALBUNS)
    for album_item in albuns_com_capa:
        caminho_pasta = os.path.join(app.static_folder, 'images', 'galeria', album_item['slug'])
        try:
            imagens = sorted([img for img in os.listdir(caminho_pasta) if img.lower().endswith(('.png', '.jpg', '.jpeg'))])
            album_item['imagem_capa'] = imagens[0] if imagens else 'placeholder.png'
        except FileNotFoundError:
            album_item['imagem_capa'] = 'placeholder.png'
    return render_template('galeria/galeria_index.html', albuns=albuns_com_capa)

@app.route('/galeria/<string:album_slug>')
def ver_album(album_slug):
    album_encontrado = next((a for a in ALBUNS if a['slug'] == album_slug), None)
    if not album_encontrado: abort(404)
    
    album_para_template = copy.deepcopy(album_encontrado)
    
    caminho_pasta = os.path.join(app.static_folder, 'images', 'galeria', album_slug)
    try:
        lista_imagens = sorted([img for img in os.listdir(caminho_pasta) if img.lower().endswith(('.png', '.jpg', '.jpeg'))])
    except FileNotFoundError:
        lista_imagens = []
    
    album_para_template['imagens'] = lista_imagens
    return render_template('galeria/album_fotos.html', album=album_para_template)

# --- EXECUTAR A APLICAÇÃO ---
if __name__ == "__main__":
    print(">>> Servidor a iniciar em http://127.0.0.1:5000 <<<")
    app.run(host='127.0.0.1', port=5000, debug=True)
