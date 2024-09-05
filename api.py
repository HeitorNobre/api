import requests
from flask import Flask, request, jsonify
from fuzzywuzzy import process
from cachetools import cached, TTLCache
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Carregar variáveis de ambiente do .env, se disponível
load_dotenv()

# Obter valores das variáveis de ambiente
CONTENT_TYPE = os.getenv('CONTENT_TYPE')
APP_TOKEN = os.getenv('APP_TOKEN')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

HEADERS = {
    'Content-Type': CONTENT_TYPE,
    'app_token': APP_TOKEN,
    'access_token': ACCESS_TOKEN
}

# Cache para armazenar resultados de chamadas à API (TTL de 5 minutos)
cache = TTLCache(maxsize=100, ttl=300)

@app.route('/')
def saudar():
    return jsonify(HEADERS)

@cached(cache)
def obter_condominios():
    url = "https://api.superlogica.net/v2/condor/condominios/get?id=-1&somenteCondominiosAtivos=1"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

@cached(cache)
def obter_unidade(cpf, id_cond):
    url = f"https://api.superlogica.net/v2/condor/unidades/index?idCondominio={id_cond}&pesquisa={cpf}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    response_json = response.json()
    if response_json and len(response_json) > 0:
        return response_json[0].get("id_unidade_uni")
    else:
        return None

@cached(cache)
def obter_cobrancas(id_cond, id_unidade):
    url = f"https://api.superlogica.net/v2/condor/cobranca/index?status=pendentes&idCondominio={id_cond}&UNIDADES[0]={id_unidade}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

@app.route('/processar_dados', methods=['GET'])
def processar_dados():
    cpf = request.args.get('cpf')
    nome_condominio = request.args.get('nome_condominio')

    if not cpf or not nome_condominio:
        return jsonify({'error': 'CPF e nome do condomínio são obrigatórios.'}), 400

    try:
        condominios = obter_condominios()
    except requests.RequestException as e:
        return jsonify({'error': 'Erro ao obter lista de condomínios.', 'details': str(e)}), 500

    nomes_condominios = [cond.get('st_fantasia_cond') for cond in condominios]
    melhor_correspondencia, score = process.extractOne(nome_condominio, nomes_condominios)

    if score < 70:
        return jsonify({'error': 'Nome do condomínio não encontrado ou muito diferente.'}), 404

    id_cond = next((cond.get('id_condominio_cond') for cond in condominios if cond.get('st_fantasia_cond') == melhor_correspondencia), None)

    if not id_cond:
        return jsonify({'error': 'Condomínio não encontrado.'}), 404

    try:
        id_unidade = obter_unidade(cpf, id_cond)
    except requests.RequestException as e:
        return jsonify({'error': 'Erro ao obter unidades do condomínio.', 'details': str(e)}), 500

    if not id_unidade:
        return jsonify({'error': 'Unidade não encontrada para o CPF informado.'}), 404

    try:
        cobrancas = obter_cobrancas(id_cond, id_unidade)
    except requests.RequestException as e:
        return jsonify({'error': 'Erro ao obter cobranças.', 'details': str(e)}), 500

    links_cobranca = [cobranca.get('link_segundavia') for cobranca in cobrancas]
    if not links_cobranca:
        return jsonify({'links_cobranca': 'sem cobranças pendentes'})
    return jsonify({'links_cobranca': links_cobranca})

