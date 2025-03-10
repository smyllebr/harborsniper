from flask import Flask, render_template, jsonify, request
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

ITEMS_FILE = 'items_salvos.json'

def carregar_items_salvos():
    if os.path.exists(ITEMS_FILE):
        try:
            with open(ITEMS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_items(items):
    with open(ITEMS_FILE, 'w') as f:
        json.dump(items, f, indent=2)

def get_home_data():
    url = "https://nftharbor.io/rest/V1/API/getHomeData"
    
    payload = {
        "Version": "4.2",
        "Collection": "TownStar",
        "Guid": "none",
        "SignGuid": "none"
    }
    
    headers = {
        "Content-Type": "text/plain;charset=UTF-8",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Origin": "https://marketplace.nftharbor.io",
        "Referer": "https://marketplace.nftharbor.io/",
        "Sec-Ch-Ua": '"Not A(Brand";v="8", "Chromium";v="132"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Windows",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty"
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer a requisição: {e}")
        return None

def processar_nfts(data):
    if not data or 'data' not in data or 'NewListings' not in data['data']:
        return []

    nfts = data['data']['NewListings']
    
    # Ordenando NFTs do mais recente ao mais antigo
    nfts_ordenados = sorted(
        nfts,
        key=lambda x: datetime.strptime(x['Creation_Dt'], "%Y-%m-%dT%H:%M:%S.%fZ"),
        reverse=True
    )
    
    nfts_processados = []
    for nft in nfts_ordenados:
        # Formatando as datas
        creation_date = datetime.strptime(nft['Creation_Dt'], "%Y-%m-%dT%H:%M:%S.%fZ")
        expiration_date = datetime.strptime(nft['Expiration_Dt'], "%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Criando o link de acesso
        nome_formatado = nft['Name'].replace(':', '%3A')
        link_acesso = f"https://marketplace.nftharbor.io/item/{nft['Category']}/{nft['Collection']}/{nome_formatado}/{nft['AdditionalKey']}"
        
        nft_processado = {
            'id': f"{nft['Name']}_{nft['Creation_Dt']}",  # ID único para cada NFT
            'nome': nft['Name'],
            'data_criacao': creation_date.strftime("%d/%m/%Y %H:%M:%S"),
            'data_criacao_raw': nft['Creation_Dt'],  # Mantendo a data original para comparação
            'categoria': nft['Category'],
            'raridade': nft['AdditionalKey'],
            'preco_gala': nft['Floor'],
            'preco_usd': nft['FloorUSD'],
            'melhor_oferta': nft['Bid'],
            'oferta_usd': nft['BidUSD'],
            'expiracao': expiration_date.strftime("%d/%m/%Y %H:%M:%S"),
            'link_acesso': link_acesso,
            'imagem': nft['Image']  # Adicionando a URL da imagem
        }
        nfts_processados.append(nft_processado)
    
    return nfts_processados

@app.route('/')
def index():
    dados = get_home_data()
    nfts_atuais = processar_nfts(dados)
    nfts_salvos = carregar_items_salvos()
    
    # Identificando novos itens
    ids_salvos = {nft['id'] for nft in nfts_salvos}
    novos_items = [nft for nft in nfts_atuais if nft['id'] not in ids_salvos]
    
    # Atualizando lista salva
    salvar_items(nfts_atuais)
    
    return render_template('index.html', 
                         nfts=nfts_atuais, 
                         novos_items=[nft['id'] for nft in novos_items])

@app.route('/check_updates')
def check_updates():
    dados = get_home_data()
    nfts_atuais = processar_nfts(dados)
    nfts_salvos = carregar_items_salvos()
    
    # Identificando novos itens
    ids_salvos = {nft['id'] for nft in nfts_salvos}
    novos_items = [nft for nft in nfts_atuais if nft['id'] not in ids_salvos]
    
    # Atualizando lista salva
    salvar_items(nfts_atuais)
    
    return jsonify({
        'novos_items': novos_items,
        'todos_items': nfts_atuais
    })

@app.route('/healthz')
def healthcheck():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 