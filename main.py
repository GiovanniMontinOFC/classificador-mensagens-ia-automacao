import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = FastAPI(title="API Classificador de Mensagens")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class MensagemEntrada(BaseModel):
    cliente: str
    mensagem: str

class ClassificacaoSaida(BaseModel):
    categoria: str
    prioridade: str
    setor_destino: str
    resumo_curto: str

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
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ClassificacaoSaida,
                temperature=0.1
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))