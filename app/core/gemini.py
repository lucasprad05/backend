import os
import json
import dotenv
import google.generativeai as genai
import re

# Carrega variáveis de ambiente do arquivo .env
dotenv.load_dotenv()

# Configura a API do Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# Gera recomendações de bem-estar usando o modelo Gemini
def generate_recommendations(percent: int, level: str, dims: list[dict]) -> list[dict]:
  prompt = f"""
  Você é um assistente que gera recomendações breves de bem-estar para estudantes.
  Avalie o seguinte resultado de teste de estresse:
  - Índice Geral: {percent}/100
  - Nível de Estresse: {level}
  - Dimensões:
  {dims}
  
  Gere de 3 recomendações práticas, curtas e em português focadas nos pontos onde o usuário está com o nível mais alto de estresse.
  Cada recomendação deve ter uma "tag" (palavra-chave) e um "text" (descrição).
  Retorne as recomendações no formato JSON, como no exemplo:
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

      # Remove blocos de código e qualquer texto antes/depois do JSON
      text = re.sub(r"^```(?:json)?", "", text)
      text = re.sub(r"```$", "", text)
      text = text.strip()

      # Extrai o JSON válido do texto (caso venha misturado)
      match = re.search(r"\[.*\]", text, re.S)
      if match:
          text = match.group(0)

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
    