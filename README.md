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

### **1\. Configuração do Ambiente**

1. **Clone o Repositório:** (Assumindo que este código estará em um repositório Git)

git clone https://github.com/JEAN-ALMEIDA-CZO/glpiapicustom.git

2. Crie e Ative um Ambiente Virtual (Recomendado):  
   Isso isola as dependências do seu projeto.
    
   python \-m venv venv  
   \# No Windows:  
   .\\venv\\Scripts\\activate  
   \# No macOS/Linux:  
   source venv/bin/activate

4. **Instale as Dependências:**  
   pip install Flask requests

### **2\. Configuração do GLPI**

Para que a integração funcione, você precisa configurar seu GLPI:

1. **Habilitar a API REST:**  
   * Vá em Configurar \> Geral \> API.  
   * Crie e ative a API REST.  
   * Anote o **App-Token** que será gerado ou crie um novo.  
2. **Criar um Usuário para API:**  
   * Crie um usuário no GLPI que será usado exclusivamente pela API.  
   * Vá em Administração \> Usuários \> Clique no usuário \> Aba Tokens de API.  
   * Crie um **Personal Access Token (User-Token)** para este usuário. Anote-o.  
3. **Campo Personalizado de CNPJ na Entidade:**   
4. **( requer plugin “Campos Adicionais” )**  
   * O código assume que você tem um campo personalizado para o CNPJ nas entidades do GLPI.  
   * Vá em Configurar \> Campos Adicionais.  
   * Crie um campo do tipo "Texto" com o rótulo "CNPJ" ou similar.  
     * \* Configure este campo para ser exibido nas entidades. 

   (conforme a imagem [Configuração campo CNPJ](https://github.com/JEAN-ALMEIDA-CZO/glpiapicustom/blob/ipad/Configura%C3%A7%C3%A3o%20campo%20CNPJ%20no%20cadastro%20de%20entidades.png) )

     * **Crucial:** Para a função buscar\_entidade\_por\_cnpj funcionar, você precisa do **ID numérico** deste campo personalizado.  
     * Para descobrir o ID, você pode fazer uma chamada GET para https://seusite.com.br/apirest.php/listSearchOptions/Ticket. Procure pelo nome do seu campo CNPJ na resposta e obtenha o ID associado (conforme a imagem [Buscar Campo CNPJ PERSONALIZADO](https://github.com/JEAN-ALMEIDA-CZO/glpiapicustom/blob/ipad/Buscar%20Campo%20CNPJ%20PERSONALIZADO.png) )

     
       \* Preencha o campo CNPJ no cadastro de suas entidades (clientes) no GLPI. 

   (conforme a imagem [Cadastro de CNPJ Formatado](https://github.com/JEAN-ALMEIDA-CZO/glpiapicustom/blob/ipad/Cadastro%20de%20CNPJ%20Formatado%20Empresa.png) )

5. **Configurar Categorias, Usuários e Origens de Requisição:**  
   * Certifique-se de que os IDs para itilcategories\_id, users\_id\_recipient, users\_id, \_users\_id\_requester, requestsources\_id e requesttypes\_id no corpo da requisição de criação de chamado (app.py) correspondem a IDs válidos no seu GLPI. Você pode ajustá-los conforme sua necessidade.

### **3\. Configuração do app.py**

Abra o arquivo app.py e preencha as seguintes variáveis:

GLPI\_URL \= "http://seusite.com.br/apirest.php" \# \<-- Mude para a URL da sua instalação GLPI  
APP\_TOKEN \= ""  \# \<-- Insira seu App-Token do GLPI  
USER\_TOKEN \= "" \# \<-- Insira seu User-Token do GLPI

\# Na função 'buscar\_entidade\_por\_cnpj', altere o ID do campo personalizado:  
\# "criteria\[0\]\[field\]": 76674, \# \<-- Altere este ID para o ID do seu campo CNPJ no GLPI

\# Na função 'criar\_chamado', ajuste o ID da categoria padrão e do usuário requerente/destinatário:  
\# categoria\_id \= dados.get("categoria", "18") \# \<-- Defina a categoria padrão aqui (o ID do meu caso é 18\)  
\# "users\_id\_recipient": 36, \# \<-- Crie um usuário para identificar o requerente (o ID do meu caso é 36\)  
\# "users\_id": 36,  
\# "\_users\_id\_requester": 36,  
\# "requestsources\_id": 5, \# \<-- ID da origem de requisição  
\# "requesttypes\_id": 5 \# \<-- ID do tipo de requisição

### **4\. Executar a Aplicação Flask**

No terminal, com o ambiente virtual ativado:

python app.py

A aplicação será iniciada, geralmente em http://127.0.0.1:5000.

### **5\. Testando os Endpoints**

Você pode usar ferramentas como Postman, Insomnia ou curl para testar sua API.

#### **5.1. Verificar o Status da Aplicação**

* **Endpoint:** /ping  
* **Método:** GET  
* **URL:** http://127.0.0.1:5000/ping  
* **Resposta Esperada:** App Flask está ativo\! (Status 200 OK)

#### **5.2. Criar um Chamado**

* **Endpoint:** /criar-chamado  
* **Método:** POST  
* **URL:** http://127.0.0.1:5000/criar-chamado  
* **Content-Type:** application/json  
* **Corpo (Body) da Requisição (JSON):**  
  
  {  
      "nome\_cliente": "Fulano de Tal",  
      "telefone\_cliente": "5511987654321",  
      "cnpj\_cliente": "00.000.000/0001-00",  
      "anydesk\_cliente": "123 456 789",  
      "descricao\_problema": "Problema com lentidão no sistema X",  
      "categoria": "18"  
  }

  * **cnpj\_cliente**: **Muito Importante\!** Deve ser um CNPJ válido e **cadastrado em uma entidade no seu GLPI**, no campo personalizado que você configurou. Se o CNPJ não for encontrado, o chamado não será criado.  
  * **categoria (opcional)**: Se omitido, usará o valor padrão definido no app.py (18 no exemplo).  
* **Resposta Esperada em caso de sucesso:**  
  {  
      "ticket\_id": 1234  
  }

  (Onde 1234 é o ID do chamado recém-criado no GLPI).  
* **Respostas de Erro:**  
  * **400 Bad Request:** {"erro": "Campos obrigatórios ausentes", ...} se faltar algum campo no JSON.  
  * **401 Unauthorized:** {"erro": "Falha ao iniciar sessão"} se os tokens do GLPI estiverem incorretos ou a API não estiver acessível.  
  * **404 Not Found:** {"erro": "Entidade não encontrada para o CNPJ informado"} se o CNPJ não corresponder a nenhuma entidade no GLPI.  
  * **Outros Erros HTTP:** {"erro": "Erro ao criar chamado", "detalhe": "..."} com o status code do GLPI.  
  * **500 Internal Server Error:** {"erro": "Erro interno", "detalhe": "..."} para erros não tratados na aplicação Flask.

## **🐳 Docker (Opcional, para Deploy)**

Para implantar esta aplicação em um ambiente de produção ou de forma mais isolada, você pode usar Docker.

1. **Crie um arquivo Dockerfile na raiz do projeto:**  
   \# Use uma imagem base Python  
   FROM python:3.9-slim-buster

   \# Define o diretório de trabalho dentro do contêiner  
   WORKDIR /app

   \# Copia o arquivo de requisitos e instala as dependências  
   COPY requirements.txt .  
   RUN pip install \--no-cache-dir \-r requirements.txt

   \# Copia o restante do código da aplicação para o contêiner  
   COPY . .

   \# Expõe a porta em que o Flask rodará  
   EXPOSE 5000

   \# Comando para rodar a aplicação Flask  
   \# Use um servidor WSGI como Gunicorn para produção:  
   \# RUN pip install gunicorn  
   \# CMD \["gunicorn", "--bind", "0.0.0.0:5000", "app:app"\]  
   \# Ou para desenvolvimento:  
   CMD \["python", "app.py"\]

2. **Crie um arquivo requirements.txt na raiz do projeto:**  
   Flask  
   requests  
   gunicorn \# Adicione se for usar Gunicorn para produção

3. **Construa a imagem Docker:**  
   docker build \-t glpi-integration-app .

4. **Execute o contêiner Docker:**  
   docker run \-p 5000:5000 glpi-integration-app

   Sua aplicação estará acessível em http://localhost:5000.

## **🤝 Contribuição**

Contribuições são bem-vindas\! Se você tiver sugestões, melhorias ou encontrar bugs, sinta-se à vontade para:

1. Abrir uma [Issue](https://github.com/JEAN-ALMEIDA-CZO/glpiapicustom/issues)  
2. Criar um [Pull Request](https://github.com/JEAN-ALMEIDA-CZO/glpiapicustom/pulls)

## **📄 Licença**

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para mais detalhes.
