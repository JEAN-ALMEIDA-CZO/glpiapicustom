Integração GLPI: Criação de Chamados AutomatizadaEste projeto implementa uma pequena API RESTful usando Flask que interage com a API do GLPI para automatizar a criação de chamados. Ele é útil para integrar sistemas externos que precisam abrir tickets no GLPI, como formulários de contato, portais de clientes ou outros sistemas de monitoramento.🌟 FuncionalidadesInício e Fim de Sessão: Gerencia o ciclo de vida da sessão com a API do GLPI usando App-Token e User-Token.Busca de Entidade por CNPJ: Localiza entidades (empresas/clientes) no GLPI usando um campo personalizado de CNPJ.Criação de Chamados: Abre novos chamados no GLPI com informações detalhadas do cliente e do problema.Endpoint de Verificação (/ping): Permite verificar se a aplicação está no ar.Endpoint de Depuração (/debug): Ajuda a testar o tratamento de erros.🚀 Como UsarPré-requisitosAntes de começar, certifique-se de ter o seguinte instalado:Python 3.xpip (gerenciador de pacotes do Python)1. Configuração do AmbienteClone o Repositório: (Assumindo que este código estará em um repositório Git)git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DA_PASTA_DO_PROJETO>
Crie e Ative um Ambiente Virtual (Recomendado):Isso isola as dependências do seu projeto.python -m venv venv
# No Windows:
.\venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
Instale as Dependências:pip install Flask requests
2. Configuração do GLPIPara que a integração funcione, você precisa configurar seu GLPI:Habilitar a API REST:Vá em Configuração > Geral > API.Ative a API REST.Anote o App-Token que será gerado ou crie um novo.Criar um Usuário para API:Crie um usuário no GLPI que será usado exclusivamente pela API.Vá em Usuários > Clique no usuário > Aba Tokens de API.Crie um Personal Access Token (User-Token) para este usuário. Anote-o.Campo Personalizado de CNPJ na Entidade:O código assume que você tem um campo personalizado para o CNPJ nas entidades do GLPI.Vá em Configuração > Tipos de Item > Entidade > Campos personalizados.Crie um campo do tipo "Texto" com o rótulo "CNPJ" ou similar.Crucial: Para a função buscar_entidade_por_cnpj funcionar, você precisa do ID numérico deste campo personalizado.Para descobrir o ID, você pode fazer uma chamada GET para https://seusite.com.br/apirest.php/listSearchOptions/Ticket. Procure pelo nome do seu campo CNPJ na resposta e obtenha o ID associado (conforme a imagem Buscar Campo CNPJ PERSONALIZADO.png que você forneceu, onde o ID era 76674).* Configure este campo para ser exibido nas entidades.
* Preencha o campo CNPJ no cadastro de suas entidades (clientes) no GLPI.
Configurar Categorias, Usuários e Origens de Requisição:Certifique-se de que os IDs para itilcategories_id, users_id_recipient, users_id, _users_id_requester, requestsources_id e requesttypes_id no corpo da requisição de criação de chamado (app.py) correspondem a IDs válidos no seu GLPI. Você pode ajustá-los conforme sua necessidade.3. Configuração do app.pyAbra o arquivo app.py e preencha as seguintes variáveis:GLPI_URL = "https://seusite.com.br/apirest.php" # <-- Mude para a URL da sua instalação GLPI
APP_TOKEN = ""  # <-- Insira seu App-Token do GLPI
USER_TOKEN = "" # <-- Insira seu User-Token do GLPI

# Na função 'buscar_entidade_por_cnpj', altere o ID do campo personalizado:
# "criteria[0][field]": 76674, # <-- Altere este ID para o ID do seu campo CNPJ no GLPI

# Na função 'criar_chamado', ajuste o ID da categoria padrão e do usuário requerente/destinatário:
# categoria_id = dados.get("categoria", "18") # <-- Defina a categoria padrão aqui (o ID do meu caso é 18)
# "users_id_recipient": 36, # <-- Crie um usuário para identificar o requerente (o ID do meu caso é 36)
# "users_id": 36,
# "_users_id_requester": 36,
# "requestsources_id": 5, # <-- ID da origem de requisição
# "requesttypes_id": 5 # <-- ID do tipo de requisição
4. Executar a Aplicação FlaskNo terminal, com o ambiente virtual ativado:python app.py
A aplicação será iniciada, geralmente em http://127.0.0.1:5000.5. Testando os EndpointsVocê pode usar ferramentas como Postman, Insomnia ou curl para testar sua API.5.1. Verificar o Status da AplicaçãoEndpoint: /pingMétodo: GETURL: http://127.0.0.1:5000/pingResposta Esperada: App Flask está ativo! (Status 200 OK)5.2. Criar um ChamadoEndpoint: /criar-chamadoMétodo: POSTURL: http://127.0.0.1:5000/criar-chamadoContent-Type: application/jsonCorpo (Body) da Requisição (JSON):{
    "nome_cliente": "Fulano de Tal",
    "telefone_cliente": "5511987654321",
    "cnpj_cliente": "00.000.000/0001-00",
    "anydesk_cliente": "123 456 789",
    "descricao_problema": "Problema com lentidão no sistema X",
    "categoria": "18"
}
cnpj_cliente: Muito Importante! Deve ser um CNPJ válido e cadastrado em uma entidade no seu GLPI, no campo personalizado que você configurou. Se o CNPJ não for encontrado, o chamado não será criado.categoria (opcional): Se omitido, usará o valor padrão definido no app.py (18 no exemplo).Resposta Esperada em caso de sucesso:{
    "ticket_id": 1234
}
(Onde 1234 é o ID do chamado recém-criado no GLPI).Respostas de Erro:400 Bad Request: {"erro": "Campos obrigatórios ausentes", ...} se faltar algum campo no JSON.401 Unauthorized: {"erro": "Falha ao iniciar sessão"} se os tokens do GLPI estiverem incorretos ou a API não estiver acessível.404 Not Found: {"erro": "Entidade não encontrada para o CNPJ informado"} se o CNPJ não corresponder a nenhuma entidade no GLPI.Outros Erros HTTP: {"erro": "Erro ao criar chamado", "detalhe": "..."} com o status code do GLPI.500 Internal Server Error: {"erro": "Erro interno", "detalhe": "..."} para erros não tratados na aplicação Flask.🐳 Docker (Opcional, para Deploy)Para implantar esta aplicação em um ambiente de produção ou de forma mais isolada, você pode usar Docker.Crie um arquivo Dockerfile na raiz do projeto:# Use uma imagem base Python
FROM python:3.9-slim-buster

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o contêiner
COPY . .

# Expõe a porta em que o Flask rodará
EXPOSE 5000

# Comando para rodar a aplicação Flask
# Use um servidor WSGI como Gunicorn para produção:
# RUN pip install gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
# Ou para desenvolvimento:
CMD ["python", "app.py"]
Crie um arquivo requirements.txt na raiz do projeto:Flask
requests
gunicorn # Adicione se for usar Gunicorn para produção
Construa a imagem Docker:docker build -t glpi-integration-app .
Execute o contêiner Docker:docker run -p 5000:5000 glpi-integration-app
Sua aplicação estará acessível em http://localhost:5000.🤝 ContribuiçãoContribuições são bem-vindas! Se você tiver sugestões, melhorias ou encontrar bugs, sinta-se à vontade para:Abrir uma IssueCriar um Pull Request📄 LicençaEste projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para mais detalhes.
