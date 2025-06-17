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
    """Analisa a força de uma senha com base em múltiplos critérios."""
    tokens = {tipo: len(re.findall(padrao, senha)) for tipo, padrao in TOKEN_TYPES.items()}
    comprimento = len(senha)
    # Critérios originais + avançados
    criterios = {
        "maiuscula": False,
        "minuscula": False,
        "numero": False,
        "simbolo": False,
        "repeticoes": False,
        "comum": False,
        "nao_comeca_numero": False,
        "nao_termina_numero": False,
        "sem_seq_letras": False,
        "sem_seq_numeros": False,
        "sem_repetidos_lado": False,
        "dois_simbolos": False,
        "dois_numeros": False,
        "duas_maiusculas": False,
        "duas_minusculas": False,
        "sem_palavra_senha": False,
        "comprimento": False,
        # Novos critérios difíceis
        "alfabeto_misto": False,  # letras latinas + não latinas
        "simbolo_raro": False,    # símbolo fora dos comuns
        "sem_padroes_teclado": False, # não contém padrões de teclado
        "maiuscula_minuscula_misturado": False, # alternância
        "tres_tipos": False,      # pelo menos 3 tipos diferentes
        "quatro_tipos": False,    # todos os tipos
        "palindromo": False,      # não é palíndromo
        "sem_nome_usuario": False # não contém 'usuario', 'admin', 'root'
    }
    if senha:
        criterios["maiuscula"] = tokens["MAIUSCULA"] > 0
        criterios["minuscula"] = tokens["MINUSCULA"] > 0
        criterios["numero"] = tokens["NUMERO"] > 0
        criterios["simbolo"] = tokens["SIMBOLO"] > 0
        repeticoes = max(senha.count(c) for c in set(senha)) > (comprimento // 2) if senha else False
        criterios["repeticoes"] = not repeticoes and comprimento > 1
        comum = senha.lower() in SENHAS_FRACAS or any(re.match(padrao, senha.lower()) for padrao in PADROES_FRACOS)
        criterios["comum"] = not comum and comprimento > 1
        criterios["nao_comeca_numero"] = len(senha) > 1 and not senha[0].isdigit()
        criterios["nao_termina_numero"] = len(senha) > 1 and not senha[-1].isdigit()
        criterios["sem_seq_letras"] = len(senha) > 2 and not bool(re.search(r"abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz", senha, re.IGNORECASE))
        criterios["sem_seq_numeros"] = len(senha) > 2 and not bool(re.search(r"012|123|234|345|456|567|678|789|890", senha))
        criterios["sem_repetidos_lado"] = len(senha) > 1 and not bool(re.search(r"(.)\\1", senha))
        criterios["dois_simbolos"] = len(set(re.findall(r"[!@#$%^&*(),.?\":{}|<>]", senha))) >= 2
        criterios["dois_numeros"] = len(set(re.findall(r"[0-9]", senha))) >= 2
        criterios["duas_maiusculas"] = len(re.findall(r"[A-Z]", senha)) >= 2
        criterios["duas_minusculas"] = len(re.findall(r"[a-z]", senha)) >= 2
        criterios["sem_palavra_senha"] = len(senha) > 5 and not bool(re.search(r"senha|password", senha, re.IGNORECASE))
        criterios["comprimento"] = comprimento >= 12
        # Critérios difíceis
        criterios["alfabeto_misto"] = bool(re.search(r"[a-zA-Z]", senha)) and bool(re.search(r"[à-ÿÀ-ß]", senha))
        criterios["simbolo_raro"] = bool(re.search(r"[§¢£¥©®±µ¶¿¡]", senha))
        criterios["sem_padroes_teclado"] = not bool(re.search(r"qwerty|asdf|zxcv|1234|abcd|!@#|qaz|wsx|edc|rfv|tgb|yhn|ujm|ik,|ol.|pl;", senha, re.IGNORECASE))
        criterios["maiuscula_minuscula_misturado"] = bool(re.search(r"([a-z][A-Z])|([A-Z][a-z])", senha))
        tipos = sum([
            bool(re.search(r"[A-Z]", senha)),
            bool(re.search(r"[a-z]", senha)),
            bool(re.search(r"[0-9]", senha)),
            bool(re.search(r"[!@#$%^&*(),.?\":{}|<>§¢£¥©®±µ¶¿¡]", senha))
        ])
        criterios["tres_tipos"] = tipos >= 3
        criterios["quatro_tipos"] = tipos == 4
        criterios["palindromo"] = senha != senha[::-1]
        criterios["sem_nome_usuario"] = not bool(re.search(r"usuario|admin|root", senha, re.IGNORECASE))
    # Ajuste: se senha < 6, sempre Muito Fraca
    if comprimento < 6:
        classificacao = "Muito Fraca"
        pontuacao = 0
    else:
        total_criterios = len(criterios)
        criterios_atingidos = sum(criterios.values())
        criterios["forte_80"] = criterios_atingidos / total_criterios >= 0.8 if senha else False
        pontuacao = criterios_atingidos
        nivel = [
            "Muito Fraca", "Fraca", "Moderada", "Forte", "Muito Forte", "Extremamente Forte", "Impressionante"
        ]
        # Só "Impressionante" se TODOS os critérios forem True
        if all(criterios[k] for k in criterios if k != "forte_80"):
            classificacao = "Impressionante"
        elif criterios["forte_80"] and criterios["comprimento"] and criterios["quatro_tipos"]:
            classificacao = "Extremamente Forte"
        elif criterios["forte_80"] and criterios["comprimento"]:
            classificacao = "Muito Forte"
        elif criterios["forte_80"]:
            classificacao = "Forte"
        elif pontuacao >= 10:
            classificacao = "Moderada"
        elif pontuacao >= 6:
            classificacao = "Fraca"
        else:
            classificacao = "Muito Fraca"
    return {
        "senha": senha,
        "criterios": criterios,
        "pontuacao": pontuacao,
        "classificacao": classificacao
    }
    
@app.route("/analisar", methods=["POST"])
def api_analisar_senha():
    """Endpoint da API para analisar a senha."""
    dados = request.get_json()
    if not dados or "senha" not in dados:
        return jsonify({"erro": "O campo 'senha' é obrigatório."}), 400
    
    senha = dados["senha"]
    
    if re.search(r"\s", senha):
        return jsonify({"erro": "A senha não pode conter espaços em branco."}), 400

    resultado = analisar_senha(senha)
    return jsonify(resultado)

@app.route("/")
def home():
    """Página inicial para verificar se a API está no ar."""
    return "API de verificação de senha está rodando!"

if __name__ == "__main__":
    app.run(debug=True)