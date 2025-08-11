# app/pontos/routes.py
from flask import Blueprint, render_template, abort
import pandas as pd
import os

pontos_bp = Blueprint('pontos', __name__, template_folder='../templates/pontos')

def carregar_dados_do_csv():
    caminho_csv = 'dados_formatados.xlsx - Sheet1.csv'
    
    if not os.path.exists(caminho_csv):
        print(f"AVISO: Ficheiro '{caminho_csv}' não encontrado em '{os.path.abspath(caminho_csv)}'. O site ficará sem pontos.")
        return {}

    try:
        df = pd.read_csv(caminho_csv, dtype=str)
        df.fillna('', inplace=True)
    except Exception as e:
        print(f"ERRO ao ler o ficheiro CSV: {e}")
        return {}

    dados_organizados = {
        "entidades": {"titulo_categoria": "Pontos de Entidades", "linhas": {}},
        "orixas": {"titulo_categoria": "Pontos de Orixás", "linhas": {}},
        "ritualisticas": {"titulo_categoria": "Pontos de Rituais", "linhas": {}}
    }

    for _, row in df.iterrows():
        categoria_principal = str(row.get('Categoria_Principal', '')).strip()
        linha_trabalho = str(row.get('Linha_Trabalho', '')).strip()
        sub_categoria = str(row.get('Sub_Categoria', 'Pontos Gerais')).strip()
        if not sub_categoria or sub_categoria.lower() in ['n/a', 'nan']: sub_categoria = 'Pontos Gerais'
        
        nome_ponto = str(row.get('Nome_Ponto', '')).strip()
        tipo_toque = str(row.get('Tipo_Toque', '')).strip()
        link_youtube = str(row.get('Link_Youtube', '')).strip()

        youtube_id = ""
        if 'v=' in link_youtube:
            youtube_id = link_youtube.split('v=')[1].split('&')[0]

        if not nome_ponto or nome_ponto == 'Nome_Ponto':
            continue

        chave_categoria = None
        if "Entidades" in categoria_principal:
            chave_categoria = "entidades"
        elif "Orixas" in categoria_principal or "Orixás" in categoria_principal:
            chave_categoria = "orixas"
        elif "Rituais" in categoria_principal or "Ritualisticas" in categoria_principal:
            chave_categoria = "ritualisticas"

        if not chave_categoria or not linha_trabalho:
            continue
            
        if linha_trabalho not in dados_organizados[chave_categoria]["linhas"]:
            slug = linha_trabalho.lower().replace(' ', '-').replace('ã', 'a').replace('ç', 'c').replace('ó', 'o')
            dados_organizados[chave_categoria]["linhas"][linha_trabalho] = {
                "linha_nome": linha_trabalho,
                "linha_slug": slug,
                "sub_categorias": {}
            }
        
        if sub_categoria not in dados_organizados[chave_categoria]["linhas"][linha_trabalho]["sub_categorias"]:
            dados_organizados[chave_categoria]["linhas"][linha_trabalho]["sub_categorias"][sub_categoria] = {
                "titulo": sub_categoria,
                "pontos": []
            }
            
        dados_organizados[chave_categoria]["linhas"][linha_trabalho]["sub_categorias"][sub_categoria]["pontos"].append({
            "nome": nome_ponto,
            "toque": tipo_toque,
            "youtube_id": youtube_id
        })

    final_data = {}
    for cat_key, cat_data in dados_organizados.items():
        final_data[cat_key] = {
            "titulo_categoria": cat_data["titulo_categoria"],
            "linhas": sorted(list(cat_data["linhas"].values()), key=lambda x: x['linha_nome'])
        }
        for linha in final_data[cat_key]["linhas"]:
            linha["sub_categorias"] = sorted(list(linha["sub_categorias"].values()), key=lambda x: x['titulo'])
    
    return final_data

# Carrega os dados quando o servidor inicia
DADOS_PONTOS = carregar_dados_do_csv()
DADOS_PONTOS_ENTIDADES = DADOS_PONTOS.get("entidades", {}).get("linhas", [])
DADOS_PONTOS_ORIXAS = DADOS_PONTOS.get("orixas", {}).get("linhas", [])
DADOS_PONTOS_RITUAIS = DADOS_PONTOS.get("ritualisticas", {}).get("linhas", [])

def find_linha_by_slug(slug, lista_de_linhas):
    return next((linha for linha in lista_de_linhas if linha["linha_slug"] == slug), None)

@pontos_bp.route('/entidades/<string:linha_slug>')
def page_linha_entidade(linha_slug):
    linha_encontrada = find_linha_by_slug(linha_slug, DADOS_PONTOS_ENTIDADES)
    if not linha_encontrada: abort(404)
    return render_template('lista_pontos.html', linha=linha_encontrada)

@pontos_bp.route('/orixas/<string:linha_slug>')
def page_linha_orixa(linha_slug):
    linha_encontrada = find_linha_by_slug(linha_slug, DADOS_PONTOS_ORIXAS)
    if not linha_encontrada: abort(404)
    return render_template('lista_pontos.html', linha=linha_encontrada)

@pontos_bp.route('/rituais/<string:linha_slug>')
def page_linha_ritual(linha_slug):
    linha_encontrada = find_linha_by_slug(linha_slug, DADOS_PONTOS_RITUAIS)
    if not linha_encontrada: abort(404)
    return render_template('lista_pontos.html', linha=linha_encontrada)
