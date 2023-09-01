# 🦜️🔗 Langchain "converse com..." Demo

![Python](https://img.shields.io/badge/python-3.10-blue)

- [🦜️🔗 Langchain "converse com..." Demo](#️-langchain-converse-com-demo)
  - [Introdução](#introdução)
  - [Instalação](#instalação)
  - [Main](#main)
  - [File QA / Talk With Your Documents](#file-qa--talk-with-your-documents)
  - [Website QA / Talk With Your Website](#website-qa--talk-with-your-website)
  - [Duck Duck go](#duck-duck-go)

O objetivo do projeto é explorar algumas funções do langchain, comparar respostas do ChatGPT com as obtidas com modelos menores (mDeBERTa) e testar uma maneira mais barata de usar o ChatGPT para responder perguntas relacionadas a um site.

## Introdução

Os modelos utilizados nesse projeto foram o ChatGPT-3.5 turbo e o [mDeBERTa](https://huggingface.co/timpal0l/mdeberta-v3-base-squad2). Este último apenas para responder perguntas com base em documentos fornecidos.

Neste aplicativo temos uma série de modelos de QA (_question answering_), isto é, cada página tem a função de responder perguntas com base em um contexto fornecido pelo próprio usuário. Estes contextos podem ser de arquivo ou sites.

Praticamente todas as funcionalidades seguem o já conhecido fluxo de QA : 1. Os textos são quebrados em pedaços e transformados em embeddings. 2. Um indexador cria os índices para esses embeddings e o armazena no que chamamos de base de conhecimento (_knowledge base_).  3. Quando o usuário faz uma pergunta, uma busca semântica é feita na nossa base de conhecimento que retorna os trechos mais prováveis de conter a resposta. 4. Esses trechos são então enviados, junto a pergunta do usuário, para modelo QA que retorna a resposta final ao usuário. A imagem abaixo ilustra esse fluxo.

<div style="text-align: center;">
    <img src="assets\qa_flow.png" alt="QA flow">
</div>
<p style="text-align: center;">
    Fluxo Question Answering
</p>

Utilizei um sistema idêntico a esse para responder perguntas com base em um site fornecido pelo usuário, nesse cenário o documento que compõe o embedding é o conteúdo do link que o usuário fornece. 

Com exceção do Duck Duck Go. Neste caso é feito uma busca na web utilizando a API do Duck Duck Go com a restrição de que o resultado deve ter o mesmo domínio informado pelo usuário. Mais detalhes sobre o sistema pode ser encontrado na seção [Duck Duck go](#duck-duck-go).

## Instalação

Neste projeto fizemos uso do pipenv e do docker. Se não tiver o docker instalado, aqui estão os links para instalação para [linux](https://docs.docker.com/desktop/install/linux-install/) e [windows](https://docs.docker.com/desktop/install/windows-install/). Se já tiver o docker instalado é só rodar no terminal:

```console
docker-compose build
```

o processo demora um pouco quando executado pela primeira vez. Em seguida:

```console
docker-compose up
```

Se tudo correr bem, aparecerá a mensagem "_You can now view your Streamlit app in your browser._". Então é só digitar no navegador: "<http://localhost:8001/>" para acessar o aplicativo.

## Main

A página inicial (main) é simplesmente o chatgpt-3.5 turbo. Basta inserir sua OpenAI Key para poder utilizar.

## File QA / Talk With Your Documents

Na página _File QA_ é possível conversar com esse LEIAME que já teve índexes gerados e está disponível para os modelos. Você pode fazer qualquer pergunta sobre esse projeto.

Você também pode enviar documentos de até 200mb no formato .txt ou .pdf. Para fazer o upload é necessário selecionar um ou mais modelo embedding. O "HuggingFace embedding" será usado para gerar os embeddings que serão indexados e estarão disponível para o mDeBERTa. Já o "OpenAi embedding" ficará disponível para o ChatGPT.

Você também pode fazer o upload de vários documentos de uma só vez. Após submeter corretamente os arquivos, já é possível conversar com os documentos, tanto os novos quanto os antigos para os quais você já gerou indexes. Ao final, a fonte no qual a resposta foi retirada é informada.

## Website QA / Talk With Your Website

Nesta seção, o usuário deve fornecer um URL antes de fazer perguntas. Por padrão será feito o scrape apenas da página fornecida, mas o usuário tem a opção de selecionar "_Entire Website_" (Todo o site), onde scrape de todo o site será feito. Tenha em mente que esta ação pode ter um custo elevado, visto que será feito o embedding de todo o site utilizando o modelo "text-embedding-ada-002" da OpenAI.

Após inserir um URL válido e decidir se quer ou não utilizar todo o site, você pode fazer perguntas para o website fornecido.

## Duck Duck go

O alto custo de processar um site inteiro, como mencionado na seção anterior, pode ser contornado utilizando um modelo embedding gratuito, a priori. Por exemplo, poderíamos utilizar o modelo que gera embeddings para o mDeBERTa: ["intfloat/multilingual-e5-base"](https://huggingface.co/intfloat/multilingual-e5-base).

Porém eu decidi fazer este teste utilizando o Duck-Duck-Go Search. Como não temos um modelo inteligente como o ChatGPT para traduzir as informações automaticamente, temos que verificar antes se o idioma do site informado e o idioma que o usuário escreveu a pergunta são o mesmo e, caso necessário, traduzir a pergunta do usuário para o mesmo idioma do site.

O fluxo então pode ser descrito nos seguintes passos. 1. traduz a query do usuário, caso necessário. 2. utiliza a API do Duck Duck Go para pesquisar a pergunta do usuário na web com a seguinte restrição: a resposta deve estar no mesmo domínio informado pelo usuário. 3. Passamos os trechos com as respostas encontradas pelo Duck Duck Go e a pergunta do usuário para o ChatGPT. 4. O modelo se encarrega de encontrar a resposta e traduzir de volta, se necessário, para o idioma do usuário.

<div style="text-align: center;">
    <img src="assets\duck_go_flow.png" alt="Duck Go flow">
</div>
<p style="text-align: center;">
    Fluxo do Duck Duck Go Search
</p>

Note que dessa forma, não geramos os índices semânticos. O próprio Duck Duck Go se encarrega de fazer a busca pela informação que desejamos. Embora o modelo pareça funcionar bem, ele é mais lento que o fluxo QA. Isso acontece porque não é criada uma base de conhecimento com índices para fazermos a busca semântica. Ou seja, a cada pergunta o fluxo inteiro é refeito.

<style>
    body {
        text-align: justify;
    }
</style>
