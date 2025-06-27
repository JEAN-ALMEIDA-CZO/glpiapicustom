# **Integração GLPI: Criação de Chamados Automatizada**

Este projeto implementa uma pequena API RESTful usando Flask que interage com a API do GLPI para automatizar a criação de chamados. Ele é útil para integrar sistemas externos que precisam abrir tickets no GLPI, como formulários de contato, portais de clientes ou outros sistemas de monitoramento.

## **🌟 Funcionalidades**

* **Início e Fim de Sessão:** Gerencia o ciclo de vida da sessão com a API do GLPI usando App-Token e User-Token.
* **Busca de Entidade por CNPJ:** Localiza entidades (empresas/clientes) no GLPI usando um campo personalizado de CNPJ.
* **Criação de Chamados:** Abre novos chamados no GLPI com informações detalhadas do cliente e do problema.
* **Endpoint de Verificação (/ping):** Permite verificar se a aplicação está no ar.
* **Endpoint de Depuração (/debug):** Ajuda a testar o tratamento de erros.

## **🚀 Como Usar**

### **Pré-requisitos**

Antes de começar, certifique-se de ter o seguinte instalado:

* **Python 3.x**
* **pip** (gerenciador de pacotes do Python)

### **1. Configuração do Ambiente**

1. **Clone o Repositório:**

```bash
git clone https://github.com/JEAN-ALMEIDA-CZO/glpiapicustom.git
cd glpiapicustom
```

2. **Crie e Ative um Ambiente Virtual (Recomendado):**

```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
```

3. **Instale as Dependências:**

```bash
pip install Flask requests
```

### **2. Configuração do GLPI**

1. **Habilitar a API REST:** Vá em Configurar > Geral > API, ative a API REST e gere o App-Token.

2. **Criar um Usuário para API:** Crie um usuário no GLPI, vá até a aba de Tokens de API e gere um User-Token.

3. **Campo Personalizado de CNPJ (Requer plugin “Campos Adicionais”):**

   * Vá em Configurar > Campos Adicionais e crie um campo do tipo "Texto" com o rótulo "CNPJ".
   * Configure o campo para aparecer nas entidades e preencha com os CNPJs correspondentes.
   * Descubra o **ID do campo** via chamada:

```http
GET https://seusite.com.br/apirest.php/listSearchOptions/Ticket
```

* Use esse ID na função de busca por CNPJ.

#### Exemplos ilustrativos:

* Configuração visual do campo "CNPJ" na entidade:
  ![Campo CNPJ](https://github.com/JEAN-ALMEIDA-CZO/glpiapicustom/blob/ipad/Configura%C3%A7%C3%A3o%20campo%20CNPJ%20no%20cadastro%20de%20entidades.png)
* Localização do ID via `listSearchOptions`:
  ![Buscar ID do Campo](https://github.com/JEAN-ALMEIDA-CZO/glpiapicustom/blob/ipad/Buscar%20Campo%20CNPJ%20PERSONALIZADO.png)
* Exemplo de entidade com CNPJ preenchido:
  ![Entidade com CNPJ](https://github.com/JEAN-ALMEIDA-CZO/glpiapicustom/blob/ipad/Cadastro%20de%20CNPJ%20Formatado%20Empresa.png)

4. **IDs de Categoria, Usuário e Origem:** Certifique-se de usar valores válidos nos campos `itilcategories_id`, `users_id_recipient`, `requestsources_id` e similares.

### **3. Configuração do app.py**

Abra o arquivo `app.py` e preencha:

```python
GLPI_URL = "http://seusite.com.br/apirest.php"
APP_TOKEN = ""
USER_TOKEN = ""
```

Na função `buscar_entidade_por_cnpj`, altere:

```python
"criteria[0][field]": 76674  # ID do campo personalizado de CNPJ
```

Na função `criar_chamado`, ajuste os IDs conforme sua estrutura:

```python
categoria_id = dados.get("categoria", "18")
"users_id_recipient": 36,
"users_id": 36,
"_users_id_requester": 36,
"requestsources_id": 5,
"requesttypes_id": 5
```

### **4. Executar a Aplicação Flask**

Com ambiente virtual ativado:

```bash
python app.py
```

A aplicação será iniciada em `http://127.0.0.1:5000`.

### **5. Testando os Endpoints**

#### **5.1. Verificar o Status**

* **Endpoint:** `/ping`
* **Método:** GET
* **Resposta:** `App Flask está ativo!`

#### **5.2. Criar um Chamado**

* **Endpoint:** `/criar-chamado`
* **Método:** POST
* **Content-Type:** `application/json`
* **Exemplo de corpo da requisição:**

```json
{
  "nome_cliente": "Fulano de Tal",
  "telefone_cliente": "5511987654321",
  "cnpj_cliente": "00.000.000/0001-00",
  "anydesk_cliente": "123 456 789",
  "descricao_problema": "Problema com lentidão no sistema X",
  "categoria": "18"
}
```

> ⚠️ O CNPJ deve estar cadastrado na entidade no campo personalizado.

* **Resposta esperada:**

```json
{ "ticket_id": 1234 }
```

* **Possíveis Erros:**

  * `400 Bad Request`: Campos ausentes
  * `401 Unauthorized`: Tokens incorretos
  * `404 Not Found`: CNPJ não encontrado
  * `500 Internal Server Error`: Erro não tratado

## **🐳 Docker (Opcional)**

### Dockerfile

```dockerfile
FROM python:3.9-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### requirements.txt

```
Flask
requests
gunicorn
```

### Comandos

```bash
docker build -t glpi-integration-app .
docker run -p 5000:5000 glpi-integration-app
```

## **🤝 Contribuição**

Contribuições são bem-vindas! Se você tiver sugestões, melhorias ou encontrar bugs:

* [Abrir uma Issue](https://github.com/JEAN-ALMEIDA-CZO/glpiapicustom/issues)
* [Criar um Pull Request](https://github.com/JEAN-ALMEIDA-CZO/glpiapicustom/pulls)

## **📄 Licença**

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para mais detalhes.
