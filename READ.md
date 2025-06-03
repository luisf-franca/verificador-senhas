# Verificador de Segurança de Senha

Este projeto é composto por uma API em Python (Flask) e uma interface web simples para verificar a força de senhas.

## Pré-requisitos

- **Python 3** instalado ([Download Python](https://www.python.org/downloads/))
- **pip** (gerenciador de pacotes do Python)
- **Live Server** instalado como extensão no VS Code ([Live Server na Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer))

## Como rodar o projeto

### 1. Instale as dependências do backend

Abra o terminal na pasta do projeto e execute:

```sh
pip install flask flask-cors
```

### 2. Inicie a API

No terminal, execute:

```sh
python3 api.py
```

A API Flask estará rodando em `http://127.0.0.1:5000/`.

### 3. Rode o frontend

Abra a pasta `front` no VS Code, clique com o botão direito no arquivo `index.html` e selecione **"Open with Live Server"** (ou clique em "Go Live" no canto inferior direito do VS Code).

O navegador abrirá a interface web em um endereço como `http://127.0.0.1:5500/front/index.html`.

> **Atenção:** Certifique-se de que a API Flask (`api.py`) está rodando antes de usar o frontend.

## Observações

- Se necessário, ajuste as URLs de requisição do frontend para garantir que apontem para o endereço correto da API.
- O projeto utiliza [axios](https://axios-http.com/) para requisições HTTP no frontend.

---

Qualquer dúvida, consulte os arquivos [api.py](api.py) e [front/index.html](front/index.html).