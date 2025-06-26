# app.py
# Aplicação Flask para integração com a API do GLPI, criando chamados com base em dados de clientes.

from flask import Flask, request, jsonify
import requests
import traceback

# Inicializa a aplicação Flask com configurações para propagação de exceções e modo de depuração
app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['DEBUG'] = false #padrao false, pode consumir muito recurso do seu servidor!

# Configurações da API do GLPI
GLPI_URL = "https://seusite.com.br/apirest.php"
APP_TOKEN = ""
USER_TOKEN = ""

def iniciar_sessao():
    """
    Inicia uma sessão na API do GLPI usando os tokens de aplicativo e usuário.
    Retorna o token de sessão se bem-sucedido, ou None em caso de erro.
    """
    try:
        headers = {
            "App-Token": APP_TOKEN,
            "Authorization": f"user_token {USER_TOKEN}"
        }
        app.logger.info(f"Tentando iniciar sessão com headers: {headers}")
        response = requests.post(f"{GLPI_URL}/initSession", headers=headers)
        app.logger.info(f"Resposta initSession: {response.status_code} - {response.text}")
        if response.status_code == 200:
            response_json = response.json()
            session_token = response_json.get("session_token")
            if session_token:
                app.logger.info(f"Sessão iniciada com sucesso: {session_token}")
                return session_token
            else:
                app.logger.error(f"Resposta não contém session_token: {response_json}")
                return None
        else:
            app.logger.error(f"Falha ao iniciar sessão: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        app.logger.error(f"Erro de rede ao iniciar sessão: {e}\n{traceback.format_exc()}")
        return None
    except ValueError as e:
        app.logger.error(f"Erro ao processar JSON da resposta: {e}\n{traceback.format_exc()}")
        return None
    except Exception as e:
        app.logger.error(f"Erro inesperado ao iniciar sessão: {e}\n{traceback.format_exc()}")
        return None

def encerrar_sessao(token):
    """
    Encerra a sessão na API do GLPI usando o token de sessão fornecido.
    """
    try:
        headers = {
            "App-Token": APP_TOKEN,
            "Session-Token": token
        }
        response = requests.post(f"{GLPI_URL}/killSession", headers=headers)
        app.logger.info(f"Resposta killSession: {response.status_code} - {response.text}")
    except Exception as e:
        app.logger.error(f"Erro ao encerrar sessão: {e}\n{traceback.format_exc()}")

def buscar_entidade_por_cnpj(token, cnpj):
    """
    Busca uma entidade no GLPI pelo CNPJ usando o token de sessão.
    Normaliza o CNPJ para comparação e usa codificação para a URL.
    Retorna o ID da entidade se encontrado, ou None em caso de erro.
    """
    try:
        headers = {
            "App-Token": APP_TOKEN,
            "Session-Token": token
        }
        cnpj_normalized = ''.join(filter(str.isdigit, cnpj)).strip()
        cnpj_encoded = cnpj.replace("/", "%2F")
        params = {
            "criteria[0][field]": 76674, #id do campo personalizado ( buscar por cnpj realizando chamada "https://seusite.com.br/apirest.php/listSearchOptions/Ticket" )
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": cnpj_encoded,
            "range": "0-1499"
        }
        app.logger.info(f"Buscando CNPJ: {cnpj} (normalizado: {cnpj_normalized}, codificado: {cnpj_encoded}, range: 0-1499)")
        response = requests.get(f"{GLPI_URL}/PluginFieldsEntitycnpj", headers=headers, params=params)
        app.logger.info(f"Resposta buscar_entidade_por_cnpj: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            dados = response.json()
            if not isinstance(dados, list):
                app.logger.error(f"Resposta da API não é uma lista: {dados}")
                return None
            
            app.logger.info(f"Total de registros retornados: {len(dados)}")
            for i, registro in enumerate(dados[:10], 1):
                app.logger.debug(f"Registro {i}: {registro}")
            
            for registro in dados:
                cnpj_field = registro.get("cnpjfield", "").strip()
                cnpj_field_normalized = ''.join(filter(str.isdigit, cnpj_field)) if cnpj_field else ""
                app.logger.debug(f"Comparando: {cnpj_field} (normalizado: {cnpj_field_normalized}) com {cnpj} (normalizado: {cnpj_normalized})")
                if cnpj_field.lower() == cnpj.lower() or cnpj_field_normalized == cnpj_normalized:
                    app.logger.info(f"Registro encontrado para CNPJ {cnpj}: entities_id={registro.get('entities_id')}")
                    return registro.get("entities_id")
            
            app.logger.warning(f"Nenhum registro encontrado para o CNPJ {cnpj} nos primeiros {len(dados)} resultados")
            return None
        else:
            app.logger.error(f"Erro na API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        app.logger.error(f"Erro ao buscar entidade: {e}\n{traceback.format_exc()}")
        return None

@app.route("/criar-chamado", methods=["POST"])
def criar_chamado():
    """
    Endpoint para criar um chamado no GLPI com base em dados JSON recebidos.
    Espera os campos obrigatórios: nome_cliente, telefone_cliente, cnpj_cliente, anydesk_cliente, descricao_problema.
    Retorna o ID do chamado se criado com sucesso, ou uma mensagem de erro.
    """
    try:
        dados = request.json
        # Valida campos obrigatórios
        required_fields = ["nome_cliente", "telefone_cliente", "cnpj_cliente", "anydesk_cliente", "descricao_problema"]
        if not all(key in dados for key in required_fields):
            app.logger.error(f"Campos obrigatórios ausentes: {dados}")
            return jsonify({"erro": "Campos obrigatórios ausentes", "campos_faltando": [k for k in required_fields if k not in dados]}), 400

        token = iniciar_sessao()
        if not token:
            return jsonify({"erro": "Falha ao iniciar sessão"}), 401

        entidade_id = buscar_entidade_por_cnpj(token, dados.get("cnpj_cliente"))
        if not entidade_id:
            app.logger.error(f"Entidade não encontrada para CNPJ: {dados.get('cnpj_cliente')}")
            return jsonify({"erro": "Entidade não encontrada para o CNPJ informado"}), 404

        headers = {
            "App-Token": APP_TOKEN,
            "Session-Token": token,
            "Content-Type": "application/json"
        }
        # Usa categoria do JSON, se fornecida, ou 18 como padrão
        categoria_id = dados.get("categoria", "18") #defina a categoria padrão aqui ( no meu caso o id da categoria escolhida é 18 )
        app.logger.info(f"Usando categoria_id: {categoria_id}")
        body = {
            "input": {
                "name": dados["descricao_problema"],
                "content": (
                    f"Nome do cliente: {dados['nome_cliente']}\n"
                    f"Telefone para contato: {dados['telefone_cliente']}\n"
                    f"CNPJ do cliente: {dados['cnpj_cliente']}\n"
                    f"Anydesk para acesso: {dados['anydesk_cliente']}\n"
                    f"Descrição do ocorrido: {dados['descricao_problema']}"
                ),
                "entities_id": entidade_id, #retorna o id da entidade com base no cnpj do cadastro ( requer plugin custom field instalado e criado o campo cnpj na entidade )
                "urgency": 3, #1 Muito Baixo | 2 Baixo | 3 Medio | 4 Alto | 5 Muito Alto
                "impact": 3, #1 Muito Baixo | 2 Baixo | 3 Medio | 4 Alto | 5 Muito Alto
                "itilcategories_id": categoria_id, #retorna o id da categoria inserida na chamada "criar-chamado" !Cadastrar categoria no glpi e ver o id para chamar na requisição
                "users_id_recipient": 36, #crie um usuário para identificar o requerente ( no meu caso é o 36 )
                "users_id": 36, 
                "_users_id_requester": 36,
                "requestsources_id": 5, #id da origem de requisição !Cadastrar no glpi e adicionar o id aqui
                "requesttypes_id": 5 #id da origem de requisição !Cadastrar no glpi e adicionar o id aqui
                #pode adicionar mais parametros aqui para abrir o chamado
            }
        }
        response = requests.post(f"{GLPI_URL}/Ticket", headers=headers, json=body)
        app.logger.info(f"Resposta criar chamado: {response.status_code} - {response.text}")
        if response.status_code == 201:
            return jsonify({"ticket_id": response.json().get("id")})
        app.logger.error(f"Erro ao criar chamado: {response.status_code} - {response.text}")
        return jsonify({"erro": "Erro ao criar chamado", "detalhe": response.text}), response.status_code

    except KeyError as e:
        app.logger.error(f"Campo obrigatório ausente: {e}")
        return jsonify({"erro": "Campo obrigatório ausente", "detalhe": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Erro interno: {e}\n{traceback.format_exc()}")
        return jsonify({"erro": "Erro interno", "detalhe": str(e)}), 500

    finally:
        if 'token' in locals() and token:
            encerrar_sessao(token)

@app.route("/debug")
def debug_test():
    """
    Endpoint de depuração para testar o tratamento de erros e logs.
    Levanta uma exceção intencionalmente e retorna o rastreamento de erro em HTML.
    """
    try:
        raise Exception("Teste de erro para verificar detalhes")
    except Exception as e:
        return f"<h1>Erro capturado</h1><pre>{traceback.format_exc()}</pre>", 500

@app.route("/ping")
def ping():
    """
    Endpoint simples para verificar se a aplicação Flask está ativa.
    Retorna uma mensagem de sucesso com o código de status 200.
    """
    return "App Flask está ativo!", 200

if __name__ == "__main__":
    # Executa a aplicação Flask em modo de depuração
    app.run(debug=True)