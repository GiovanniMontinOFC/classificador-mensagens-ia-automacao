import os
import json
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = FastAPI(title="API Classificador de Mensagens")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Modelos oficiais ativos informados pela API do Google + descoberta dinâmica
MODELOS_PRIORITARIOS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
]


class MensagemEntrada(BaseModel):
    cliente: str
    mensagem: str


class ClassificacaoSaida(BaseModel):
    categoria: str
    prioridade: str
    setor_destino: str
    resumo_curto: str


def obter_lista_modelos():
    modelos = list(MODELOS_PRIORITARIOS)
    try:
        for m in client.models.list():
            nome = m.name.replace("models/", "")
            if "flash" in nome and nome not in modelos:
                modelos.append(nome)
    except Exception:
        pass
    return modelos


@app.post("/classificar", response_model=ClassificacaoSaida)
async def classificar_mensagem(dados: MensagemEntrada):
    prompt = f"""
    Você é um assistente de triagem de atendimento ao cliente.
    Analise a mensagem abaixo e classifique-a estritamente dentro das regras:
    - categoria: deve ser 'Dúvida', 'Reclamação' ou 'Solicitação'.
    - prioridade: deve ser 'Alta', 'Média' ou 'Baixa'.
    - setor_destino: deve ser 'Suporte Técnico', 'Financeiro' ou 'Comercial'.
    - resumo_curto: resumo da mensagem em até 10 palavras.

    Cliente: {dados.cliente}
    Mensagem: {dados.mensagem}
    """

    ultimo_erro = None
    modelos = obter_lista_modelos()

    for modelo in modelos:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ClassificacaoSaida,
                    temperature=0.1,
                ),
            )
            print(f"[SUCESSO] Classificado usando o modelo: {modelo}")
            return json.loads(response.text)
        except Exception as e:
            ultimo_erro = e
            print(f"[AVISO] Modelo '{modelo}' falhou ({e}). Tentando próximo...")
            time.sleep(1)
            continue

    raise HTTPException(
        status_code=503,
        detail=f"Todos os modelos falharam. Último erro: {str(ultimo_erro)}",
    )