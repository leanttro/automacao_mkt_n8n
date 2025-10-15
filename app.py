import os
import psycopg2
from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- CORREÇÃO PRINCIPAL ---
# Ajuste para garantir que o Flask encontre arquivos na pasta raiz
app = Flask(__name__, static_folder='.', static_url_path='')

# Pega a URL de conexão do banco de dados das variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Cria uma conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

@app.route("/")
def index():
    """Renderiza a página principal com o formulário."""
    # Como não especificamos 'template_folder', o Flask procura na pasta 'templates' por padrão.
    # Para forçar a busca na pasta raiz, usamos render_template() do jeito que está,
    # e garantimos que o 'static_folder' sirva a imagem.
    return send_from_directory('.', 'index.html')


@app.route("/submit", methods=["POST"])
def submit():
    """Recebe os dados do formulário e insere no banco de dados."""
    nome = request.form.get('nome')
    email = request.form.get('email')
    telefone = request.form.get('telefone')
    empresa = request.form.get('empresa')
    cargo = request.form.get('cargo')

    if not nome or not email:
        return jsonify({"success": False, "message": "Nome e e-mail são obrigatórios."}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Erro interno no servidor (conexão com DB)."}), 500

    sql = """
        INSERT INTO leads (nome, email, telefone, empresa, cargo)
        VALUES (%s, %s, %s, %s, %s);
    """
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (nome, email, telefone, empresa, cargo))
            conn.commit()
        
        return jsonify({"success": True, "message": "Inscrição realizada com sucesso! Fique de olho no seu e-mail."})

    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({"success": False, "message": "Este e-mail já está cadastrado em nossa base."}), 409
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir dados: {e}")
        return jsonify({"success": False, "message": "Ocorreu um erro inesperado ao processar sua inscrição."}), 500
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5001)

