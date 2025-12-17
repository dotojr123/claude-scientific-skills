import requests
import json
import os
import time
from datetime import datetime

# Configure APIs
# In production, these should be env vars, but we pass them in for the MVP
# to allow the user to input them in the UI if needed.

def search_clinvar(variant_term):
    """
    Searches ClinVar for a variant and returns its clinical significance and summary.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    # 1. Search for the variant ID
    search_url = f"{base_url}/esearch.fcgi"
    params = {
        "db": "clinvar",
        "term": variant_term,
        "retmode": "json",
        "retmax": 1
    }

    try:
        resp = requests.get(search_url, params=params)
        data = resp.json()

        if int(data['esearchresult']['count']) == 0:
            return {"found": False, "message": "Variant not found in ClinVar"}

        uid = data['esearchresult']['idlist'][0]

        # 2. Get the variant summary
        summary_url = f"{base_url}/esummary.fcgi"
        sum_params = {
            "db": "clinvar",
            "id": uid,
            "retmode": "json"
        }

        sum_resp = requests.get(summary_url, params=sum_params)
        sum_data = sum_resp.json()

        result = sum_data['result'][uid]

        return {
            "found": True,
            "uid": uid,
            "title": result.get('title', ''),
            "clinical_significance": result.get('clinical_significance', {}).get('description', 'Not provided'),
            "review_status": result.get('clinical_significance', {}).get('review_status', 'Not provided'),
            "last_evaluated": result.get('clinical_significance', {}).get('last_evaluated', 'Unknown'),
            "accession": result.get('accession_version', ''),
            "traits": [t.get('name', '') for t in result.get('trait_set', [])]
        }

    except Exception as e:
        return {"found": False, "error": str(e)}

def search_pubmed(gene_symbol, variant_term, max_results=3):
    """
    Searches PubMed for recent papers mentioning the gene and variant.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    query = f"{gene_symbol}[Title/Abstract] AND {variant_term}[All Fields]"

    # 1. Search for PMIDs
    search_url = f"{base_url}/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "sort": "date"
    }

    try:
        resp = requests.get(search_url, params=params)
        data = resp.json()

        if int(data['esearchresult']['count']) == 0:
            return []

        pmids = data['esearchresult']['idlist']

        # 2. Fetch details
        fetch_url = f"{base_url}/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",  # XML is standard for efetch
            "rettype": "abstract"
        }

        # Note: Parsing XML properly requires ElementTree, but for MVP simplicity
        # we might just return the IDs to the LLM or try to use esummary json

        summary_url = f"{base_url}/esummary.fcgi"
        sum_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json"
        }

        sum_resp = requests.get(summary_url, params=sum_params)
        sum_data = sum_resp.json()

        papers = []
        for pmid in pmids:
            if pmid in sum_data['result']:
                doc = sum_data['result'][pmid]
                papers.append({
                    "title": doc.get('title', ''),
                    "authors": [a['name'] for a in doc.get('authors', [])[:3]],
                    "journal": doc.get('source', ''),
                    "pubdate": doc.get('pubdate', ''),
                    "pmid": pmid
                })

        return papers

    except Exception as e:
        return [{"error": str(e)}]

def generate_llm_prompt(variant_input, clinvar_data, pubmed_data):
    """
    Constructs the prompt for the LLM to generate the PT-BR report.
    """

    clinvar_summary = "ClinVar Data:\n"
    if clinvar_data.get('found'):
        clinvar_summary += f"- Classification: {clinvar_data['clinical_significance']}\n"
        clinvar_summary += f"- Review Status: {clinvar_data['review_status']}\n"
        clinvar_summary += f"- Last Evaluated: {clinvar_data['last_evaluated']}\n"
        clinvar_summary += f"- Condition(s): {', '.join(clinvar_data['traits'])}\n"
    else:
        clinvar_summary += "Variant not found in ClinVar.\n"

    pubmed_summary = "Recent Literature:\n"
    for paper in pubmed_data:
        pubmed_summary += f"- {paper.get('title')} ({paper.get('pubdate')}) - {paper.get('journal')}\n"

    prompt = f"""
Você é um geneticista clínico especialista em oncogenética.
Sua tarefa é escrever um LAUDO GENÉTICO em Português do Brasil (PT-BR) para a seguinte variante:

Variante: {variant_input}

Use os dados abaixo como evidência:
{clinvar_summary}
{pubmed_summary}

Diretrizes de Tradução e Estilo:
1. Traduza os termos técnicos seguindo a nomenclatura ACMG adaptada para o Brasil:
   - "Pathogenic" -> "Patogênica"
   - "Likely Pathogenic" -> "Provavelmente Patogênica"
   - "Uncertain Significance" -> "Significado Incerto (VUS)"
   - "Likely Benign" -> "Provavelmente Benigna"
   - "Benign" -> "Benigna"

2. Estrutura do Laudo:
   - **CONCLUSÃO**: Em destaque, a classificação final.
   - **INTERPRETAÇÃO CLÍNICA**: Um parágrafo resumindo por que a variante tem essa classificação. Cite critérios (ex: frequência populacional, dados in silico, funcionais) se inferidos.
   - **EVIDÊNCIAS**: Liste os dados do ClinVar e dos artigos encontrados.
   - **RECOMENDAÇÃO**: Sugestão de conduta (ex: "Aconselhamento genético recomendado").

3. Tom de voz: Profissional, técnico, objetivo.

Gere apenas o conteúdo do laudo em Markdown.
"""
    return prompt

def call_llm(prompt, api_keys):
    """
    Calls OpenAI or Gemini based on available keys.
    """
    openai_key = api_keys.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
    gemini_key = api_keys.get('GOOGLE_API_KEY') or os.environ.get('GOOGLE_API_KEY')

    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"

    elif gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error calling Gemini: {str(e)}"

    else:
        return "Configuração de API Key ausente. Por favor, forneça uma chave da OpenAI ou Google Gemini."

def process_variant(variant_input, api_keys):
    # 1. Parse input (simple assumption: HGVS string like 'BRCA1 c.68_69del')
    parts = variant_input.split()
    gene = parts[0] if len(parts) > 0 else "Unknown"

    # 2. Query ClinVar
    clinvar_res = search_clinvar(variant_input)

    # 3. Query PubMed
    pubmed_res = search_pubmed(gene, variant_input)

    # 4. Generate Prompt
    prompt = generate_llm_prompt(variant_input, clinvar_res, pubmed_res)

    # 5. Call LLM
    report = call_llm(prompt, api_keys)

    return {
        "variant": variant_input,
        "clinvar_data": clinvar_res,
        "pubmed_count": len(pubmed_res),
        "report": report
    }
