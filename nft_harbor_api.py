import requests
import json
from datetime import datetime

def get_home_data():
    # URL da API
    url = "https://nftharbor.io/rest/V1/API/getHomeData"
    
    # Dados do payload
    payload = {
        "Version": "4.2",
        "Collection": "TownStar",
        "Guid": "none",
        "SignGuid": "none"
    }
    
    # Headers necessários
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
        # Fazendo a requisição POST
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers
        )
        
        # Verificando se a requisição foi bem-sucedida
        response.raise_for_status()
        
        # Retornando os dados em formato JSON
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer a requisição: {e}")
        return None

def criar_link_acesso(nft):
    # Substituindo : por % no nome do NFT
    nome_formatado = nft['Name'].replace(':', '%3A')
    return f"https://marketplace.nftharbor.io/item/{nft['Category']}/{nft['Collection']}/{nome_formatado}/{nft['AdditionalKey']}"

def exibir_nfts(data):
    if not data or 'data' not in data or 'NewListings' not in data['data']:
        print("Nenhum dado disponível")
        return

    nfts = data['data']['NewListings']
    
    # Ordenando NFTs do mais recente ao mais antigo
    nfts_ordenados = sorted(
        nfts,
        key=lambda x: datetime.strptime(x['Creation_Dt'], "%Y-%m-%dT%H:%M:%S.%fZ"),
        reverse=True
    )
    
    print("\n=== NFTs Disponíveis no TownStar (Do Mais Recente ao Mais Antigo) ===\n")
    
    for nft in nfts_ordenados:
        # Formatando a data de criação
        creation_date = datetime.strptime(nft['Creation_Dt'], "%Y-%m-%dT%H:%M:%S.%fZ")
        creation_formatted = creation_date.strftime("%d/%m/%Y %H:%M:%S")
        
        print(f"Nome: {nft['Name']}")
        print(f"Data de Criação: {creation_formatted}")
        print(f"Categoria: {nft['Category']}")
        print(f"Raridade: {nft['AdditionalKey']}")
        print(f"Preço: {nft['Floor']} ({nft['FloorUSD']})")
        print(f"Melhor Oferta: {nft['Bid']}")
        if nft['BidUSD']:
            print(f"Valor da Oferta em USD: {nft['BidUSD']}")
        
        # Formatando a data de expiração
        expiration_date = datetime.strptime(nft['Expiration_Dt'], "%Y-%m-%dT%H:%M:%S.%fZ")
        expiration_formatted = expiration_date.strftime("%d/%m/%Y %H:%M:%S")
        print(f"Expira em: {expiration_formatted}")
        
        # Adicionando o link de acesso
        print(f"Link de Acesso: {criar_link_acesso(nft)}")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    resultado = get_home_data()
    if resultado:
        exibir_nfts(resultado) 