import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Definição dos tokens do analisador léxico
TOKEN_TYPES = {
    "MAIUSCULA": r"[A-Z]",
    "MINUSCULA": r"[a-z]",
    "NUMERO": r"\d",
    "SIMBOLO": r"[!@#$%^&*(),.?\":{}|<>]"
}

# Lista de senhas fracas comuns e padrões fracos
SENHAS_FRACAS = {"123456", "password", "qwerty", "abc123", "senha123"}
PADROES_FRACOS = [r"^\d{6,}$", r"^(.)\1{5,}$", r"^(qwerty|asdfgh|zxcvbn|12345|abcdef)$"]

def analisar_senha(senha):
    tokens = {tipo: len(re.findall(padrao, senha)) for tipo, padrao in TOKEN_TYPES.items()}
    comprimento = len(senha)
    repeticoes = max(senha.count(c) for c in set(senha)) > (comprimento // 2)  # Penaliza muitas repetições
    comum = senha.lower() in SENHAS_FRACAS or any(re.match(padrao, senha.lower()) for padrao in PADROES_FRACOS)
    
    criterios = {
        "comprimento": comprimento >= 12,
        "maiuscula": tokens["MAIUSCULA"] > 0,
        "minuscula": tokens["MINUSCULA"] > 0,
        "numero": tokens["NUMERO"] > 0,
        "simbolo": tokens["SIMBOLO"] > 0,
        "repeticoes": not repeticoes,
        "comum": not comum
    }
    
    pontuacao = sum(criterios.values())
    nivel = ["Muito Fraca", "Fraca", "Moderada", "Forte", "Muito Forte", "Extremamente Forte"]
    
    return {
        "senha": senha,
        "criterios": criterios,
        "pontuacao": pontuacao,
        "classificacao": nivel[min(pontuacao, len(nivel) - 1)]
    }
    
@app.route("/analisar", methods=["POST"])
def api_analisar_senha():
    dados = request.get_json()
    if "senha" not in dados:
        return jsonify({"erro": "O campo 'senha' é obrigatório."}), 400
    resultado = analisar_senha(dados["senha"])
    return jsonify(resultado)

@app.route("/")
def home():
    return "API de verificação de senha está rodando!"

if __name__ == "__main__":
    app.run(debug=True)
