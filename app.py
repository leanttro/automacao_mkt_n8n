import os
import psycopg2
from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do Flask (não precisa mudar)
app = Flask(__name__, static_url_path='', static_folder='.')

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    return conn

# --- ALTERAÇÃO AQUI ---
@app.route("/")
def index():
    """
    Serve a página principal do formulário.
    Usamos send_from_directory para dizer ao Flask para pegar o arquivo da pasta raiz ('.').
    """
    return send_from_directory('.', 'index.html')

@app.route("/submit", methods=["POST"])
def submit():
    """Recebe os dados do formulário e insere no banco de dados."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        empresa = request.form.get('empresa')
        cargo = request.form.get('cargo')

        sql = """
            INSERT INTO leads (nome, email, telefone, empresa, cargo)
            VALUES (%s, %s, %s, %s, %s);
        """
        cur.execute(sql, (nome, email, telefone, empresa, cargo))
        conn.commit()

        return jsonify({"success": True, "message": "Lead cadastrado com sucesso!"}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Erro ao conectar ou inserir no banco de dados: {e}")
        return jsonify({"success": False, "message": "Erro interno no servidor (conexão com DB)."}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=True)
