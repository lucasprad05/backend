# StressAI Backend

Backend do **StressAI**, uma aplicação que avalia o nível de estresse de estudantes com base em um questionário interativo e fornece recomendações personalizadas.

## Link do repositório Frontend - AMBOS UTILIZAR BRANCH MAIN
https://github.com/lucasprad05/Web-Based-Stres-Screening-System-with-Artificial-Intelligence

Informações sobre Autenticação e Autorização são explicadas no repositório do front-end, porém a implementação está dentro da pasta <strong>app/core/security.py</strong>

## Como Rodar o Projeto Localmente

 - Instalar dependências
```bash
pip install -r requirements.txt
```

- Rodar o servidor local
```bash
uvicorn app.main:app --reload
```
O servidor será iniciado em http://localhost:8000
A documentação automática estará disponível em:

Swagger UI: http://localhost:8000/docs

<strong>O Backend deve ser rodado antes do frontend</strong>

## 📂 Estrutura de Rotas
#/auth — Autenticação e Registro
- POST /auth/register → Cria um novo usuário (valida duplicidade de e-mail).
- POST /auth/token → Realiza login e retorna um JWT para autenticação

#/users — Operações do Usuário
- GET /users/me → Retorna dados do usuário autenticado.
- PUT /users/me/email → Atualiza o e-mail (exige senha atual).
- PUT /users/me/password → Atualiza a senha (verifica senha anterior).
- DELETE /users/me → Exclui permanentemente a conta do usuário.

#/assessments — Avaliações de Estresse
- POST /assessments → Cria uma nova avaliação, calcula o nível de estresse e gera recomendações com a API Gemini.
- GET /assessments/me → Lista todas as avaliações do usuário autenticado (ordem decrescente de data).

## Integração com IA (Gemini API)

A integração com a Gemini API gera recomendações personalizadas com base no nível de estresse e nas dimensões avaliadas.
Essas sugestões são incluídas automaticamente na resposta de cada avaliação.

## Tecnologias Utilizadas
- FastAPI — Framework web principal
- Pydantic — Validação de modelos
- JWT (OAuth2) — Autenticação e autorização
- Gemini API — Geração de recomendações com IA
- Biblioteca SQLModel + SQLLite
- Uvicorn — Servidor ASGI
- Python

## Fluxo Geral
- Registro de usuário (/auth/register)
- Login e geração de token (/auth/token)
- Resposta ao questionário (/assessments)
- Cálculo e recomendações com IA
- Visualização de histórico e gerenciamento de perfil (/users/me)
