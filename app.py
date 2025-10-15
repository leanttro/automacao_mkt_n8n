import os
import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import requests

# Carrega variáveis do .env
load_dotenv()

app = Flask(__name__)

# Configurações do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")  # ✅ Webhook n8n via .env

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        nome = data.get("nome")
        email = data.get("email")
        telefone = data.get("telefone")
        empresa = data.get("empresa")
        cargo = data.get("cargo")

        # ✅ Salva no banco
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    INSERT INTO contatos (nome, email, telefone, empresa, cargo)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nome, email, telefone, empresa, cargo))
                conn.commit()

        # ✅ Dispara webhook n8n (se configurado)
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

        return jsonify({"status": "success", "message": "Dados enviados com sucesso!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API funcionando!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
