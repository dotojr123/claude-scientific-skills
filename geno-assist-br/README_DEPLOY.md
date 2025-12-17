# GenoAssist BR - Assistente de Genética Clínica (MVP)

O **GenoAssist BR** é uma plataforma SaaS projetada para auxiliar geneticistas e laboratórios brasileiros na análise de variantes genéticas. Ele automatiza a consulta a bancos de dados públicos (ClinVar, PubMed) e utiliza LLMs (OpenAI ou Gemini) para gerar laudos preliminares em Português do Brasil (PT-BR).

## 🚀 Funcionalidades (MVP)

1.  **Consulta Automática ao ClinVar**: Verifica a classificação clínica oficial (Pathogenic, Benign, etc.) e o status de revisão.
2.  **Busca de Literatura (PubMed)**: Encontra artigos recentes relacionados ao gene e variante.
3.  **Geração de Laudo com IA**: Sintetiza as evidências e escreve um laudo técnico em PT-BR, seguindo a nomenclatura ACMG adaptada.
4.  **Interface Simples**: Dashboard limpo para inserção de variantes e visualização do laudo.

## 🛠️ Stack Tecnológica

-   **Frontend**: Next.js 14 (App Router), React, Tailwind CSS.
-   **Backend**: Python (Serverless Functions no Vercel).
-   **Bioinformática**: Integração via API (E-utilities do NCBI) com scripts Python customizados.
-   **IA**: OpenAI API (GPT-4) ou Google Gemini API.

## 📦 Como Rodar Localmente

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/geno-assist-br.git
    cd geno-assist-br
    ```

2.  **Instale as dependências (Node.js):**
    ```bash
    npm install
    # ou
    yarn install
    ```

3.  **Configure o Python:**
    Certifique-se de ter o Python 3.9+ instalado. Recomenda-se criar um virtualenv (opcional para dev local, mas útil):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # ou
    .\venv\Scripts\activate  # Windows

    pip install -r requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente:**
    Crie um arquivo `.env.local` na raiz:
    ```env
    OPENAI_API_KEY=sk-sua-chave-aqui
    # ou
    GOOGLE_API_KEY=sua-chave-gemini-aqui
    ```

5.  **Rode o servidor de desenvolvimento:**
    ```bash
    npm run dev
    ```
    Acesse `http://localhost:3000`.

## ☁️ Como Fazer Deploy no Vercel

O projeto está configurado para ser implantado diretamente no Vercel com suporte a Python Serverless.

1.  **Push para o GitHub:** Envie o código para um repositório no seu GitHub.
2.  **Importe no Vercel:**
    -   Acesse [vercel.com/new](https://vercel.com/new).
    -   Selecione o repositório `geno-assist-br`.
3.  **Configure as Variáveis de Ambiente no Vercel:**
    -   Adicione `OPENAI_API_KEY` ou `GOOGLE_API_KEY` nas configurações do projeto.
4.  **Deploy:** Clique em "Deploy". O Vercel detectará automaticamente o Next.js e as funções Python na pasta `api/`.

## 🧬 Estrutura de Arquivos

-   `app/`: Código do Frontend (Next.js App Router).
-   `api/`: Backend Python.
    -   `analyze.py`: Endpoint HTTP (Serverless Function).
    -   `engine.py`: Lógica principal (ClinVar, PubMed, Prompt Engineering).
-   `requirements.txt`: Dependências Python para o Vercel.

## ⚠️ Aviso Legal

Esta ferramenta é um assistente de pesquisa e **não substitui o julgamento clínico**. Todos os laudos gerados devem ser revisados por um geneticista qualificado.
