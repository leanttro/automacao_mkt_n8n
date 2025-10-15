# app.py (CORRIGIDO)

import os
import psycopg2
import psycopg2.extras
# 1. Importe o 'render_template' do Flask
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import requests


# Carrega variáveis do .env
load_dotenv()

# 2. Indique ao Flask onde estão suas pastas
app = Flask(__name__, template_folder='templates', static_folder='static')


# Configurações do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # 3. Altere de request.json para request.form
        # Isso fará com que o backend receba os dados do formulário corretamente
        nome = request.form.get("nome")
        email = request.form.get("email")
        telefone = request.form.get("telefone")
        empresa = request.form.get("empresa")
        cargo = request.form.get("cargo")

        # Salva no banco
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    INSERT INTO contatos (nome, email, telefone, empresa, cargo)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nome, email, telefone, empresa, cargo))
                conn.commit()

        # Dispara webhook n8n (se configurado)
        if WEBHOOK_URL:
            try:
                requests.post(
                    WEBHOOK_URL,
                    json={
                        "nome": nome,
                        "email": email,
                        "telefone": telefone,
                        "empresa": empresa,
                        "cargo": cargo
                    }
                )
            except Exception as notify_error:
                print(f"⚠ Falha ao notificar n8n: {notify_error}")
        else:
            print("⚠ Variável N8N_WEBHOOK_URL não encontrada no .env")

        # 4. Ajuste a resposta para bater com o que o seu JavaScript espera
        return jsonify({"success": True, "message": "Dados enviados com sucesso!"})

    except Exception as e:
        # É uma boa prática imprimir o erro no log para facilitar a depuração
        print(f"ERRO INTERNO: {e}")
        return jsonify({"success": False, "message": "Ocorreu um erro interno no servidor."}), 500

# 5. ESTA É A MUDANÇA PRINCIPAL!
# Altere a rota principal para renderizar o seu arquivo HTML
@app.route('/', methods=['GET'])
def home():
    # O Flask irá procurar por 'index.html' dentro da pasta 'templates'
    return render_template('index.html')

if __name__ == '__main__':
    # O Render gerencia a porta automaticamente, não precisa alterar aqui
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))