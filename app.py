import streamlit as st
import sqlite3
import hashlib

# 1. Configuração do Banco de Dados (Guarda os Cadastros)
conn = sqlite3.connect('usuarios.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        email TEXT PRIMARY KEY,
        senha TEXT
    )
''')
conn.commit()

# Função para criptografar a senha (segurança)
def criptografar_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

# 2. Configuração Visual da Página
st.set_page_config(page_title="Minha IA Comercial", page_icon="🚀", layout="centered")
st.title("🤖 Bem-vindo à Nossa Plataforma de IA")
st.write("Crie sua conta para começar a usar a tecnologia mais avançada do mercado.")

# 3. Criação das Abas de Login e Cadastro
aba_login, aba_cadastro = st.tabs(["🔒 Acessar Minha Conta", "📝 Criar Nova Conta"])

# --- ABA DE CADASTRO ---
with aba_cadastro:
    st.subheader("Faça seu cadastro gratuitamente")
    novo_email = st.text_input("Escolha um E-mail:", key="cad_email")
    nova_senha = st.text_input("Escolha uma Senha:", type="password", key="cad_senha")
    confirmar_senha = st.text_input("Confirme a Senha:", type="password", key="cad_conf_senha")
    
    if st.button("Finalizar Cadastro", type="primary"):
        if not novo_email or not nova_senha:
            st.error("Por favor, preencha todos os campos!")
        elif nova_senha != confirmar_senha:
            st.error("As senhas não coincidem!")
        else:
            try:
                senha_segura = criptografar_senha(nova_senha)
                c.execute('INSERT INTO usuarios (email, senha) VALUES (?,?)', (novo_email, senha_segura))
                conn.commit()
                st.success("Conta criada com sucesso! Agora vá até a aba de Login para acessar.")
            except sqlite3.IntegrityError:
                st.error("Este e-mail já está cadastrado no nosso sistema!")

# --- ABA DE LOGIN ---
with aba_login:
    st.subheader("Insira seus dados de acesso")
    login_email = st.text_input("E-mail:", key="log_email")
    login_senha = st.text_input("Senha:", type="password", key="log_senha")
    
    if st.button("Entrar no Painel"):
        senha_cripto = criptografar_senha(login_senha)
        c.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (login_email, senha_cripto))
        usuario_encontrado = c.fetchone()
        
        if usuario_encontrado:
            st.success(f"Logado com sucesso como: {login_email}!")
            st.balloons()
        else:
            st.error("E-mail ou senha incorretos.")
