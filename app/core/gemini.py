import os
import json
import dotenv
import google.generativeai as genai

# Carrega variáveis de ambiente do arquivo .env
dotenv.load_dotenv()

# Configura a API do Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# Gera recomendações de bem-estar usando o modelo Gemini
def generate_recommendations(percent: int, level: str, dims: list[dict]) -> list[dict]:
  prompt = f"""
  Você é um assistente que gera recomendações breves de bem-estar para estudantes.
  Avalie o seguinte resultade de teste de estresse:
  - Índice Geral: {percent}/100
  - Nível de Estresse: {level}
  - Dimensões:
  {dims}
  
  Gere de 3 a 5 recomendações práticas, curtas e em português,
  no formato JSON, como no exemplo:
  [
    {{ "tag": "Sono", "text": "Durma 7–9h por noite e evite telas antes de dormir." }},
    {{ "tag": "Pausas", "text": "Faça pequenas pausas de 5 minutos a cada hora de estudo." }}
  ]
  
  Certifique-se de que o JSON seja válido e bem formatado.
  """
  
  # Gera o conteúdo usando o modelo Gemini
  response = model.generate_content(prompt)
  
  # Tenta parsear o texto retornado como JSON
  try:
    text = response.text.strip()

    # Remove blocos de código se existirem
    if text.startswith("```"):
        text = text.strip("`")
        # remove o prefixo "json" se existir
        if text.lower().startswith("json"):
            text = text[4:].strip()

    # Parseia o JSON
    tips = json.loads(text)
    if isinstance(tips, list):
        return tips
  except Exception as e:
    print("Falha ao parsear JSON do Gemini:", e, response.text)
  
  # Retorna recomendações padrão em caso de falha
  return [
        {"tag": "Revisar", "text": "Faça pausas curtas e revise sua rotina de sono."},
        {"tag": "Respire", "text": "Tente exercícios de respiração antes de estudar."},
    ]
    