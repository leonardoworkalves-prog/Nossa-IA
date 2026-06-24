import streamlit as st
import sqlite3
import hashlib
import os
from google import genai

# =====================================================================
# 1. CONFIGURAÇÃO DA IA (GEMINI)
# =====================================================================
def enviar_mensagem_ia(mensagem, historico_streamlit):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "❌ Erro de Configuração: A chave GEMINI_API_KEY não foi configurada no sistema."
    
    try:
        client = genai.Client(api_key=api_key)
        # Criamos o chat do Gemini
        chat = client.chats.create(model="gemini-2.5-flash")
        
        # Envia a mensagem atual para receber a resposta
        response = chat.send_message(mensagem)
        return response.text
    except Exception as e:
        return f"❌ Erro ao conectar com os servidores de IA: {e}"

# =====================================================================
# 2. CONFIGURAÇÃO DO BANCO DE DADOS (USUÁRIOS)
# =====================================================================
conn = sqlite3.connect('usuarios.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        email TEXT PRIMARY KEY,
        senha TEXT
    )
''')
conn.commit()

def criptografar_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

# =====================================================================
# 3. INTERFACE VISUAL (STREAMLIT)
# =====================================================================
st.set_page_config(page_title="Nossa IA Comercial", page_icon="🚀", layout="centered")

# Controla se o utilizador está logado usando a memória da sessão do navegador
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = ""
if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = []

# --- SE NÃO ESTIVER LOGADO: MOSTRA CADASTRO E LOGIN ---
if not st.session_state.logado:
    st.title("🤖 Bem-vindo à Nossa Plataforma de IA")
    st.write("Crie a sua conta ou faça login para começar a lucrar.")
    
    aba_login, aba_cadastro = st.tabs(["🔒 Acessar Minha Conta", "📝 Criar Nova Conta"])

    with aba_cadastro:
        st.subheader("Faça o seu cadastro gratuitamente")
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
                    st.success("Conta criada com sucesso! Agora vá até a aba de Login para aceder.")
                except sqlite3.IntegrityError:
                    st.error("Este e-mail já está cadastrado no nosso sistema!")

    with aba_login:
        st.subheader("Insira os seus dados de acesso")
        login_email = st.text_input("E-mail:", key="log_email")
        login_senha = st.text_input("Senha:", type="password", key="log_senha")
        
        if st.button("Entrar no Painel"):
            senha_cripto = criptografar_senha(login_senha)
            c.execute('SELECT * VALUES (email, senha) FROM usuarios WHERE email = ? AND senha = ?' if False else 'SELECT * FROM usuarios WHERE email = ? AND senha = ?', (login_email, senha_cripto))
            usuario_encontrado = c.fetchone()
            
            if usuario_encontrado:
                st.session_state.logado = True
                st.session_state.usuario_email = login_email
                st.rerun() # Atualiza a página já logado
            else:
                st.error("E-mail ou senha incorretos.")

# --- SE ESTIVER LOGADO: ABRE O PAINEL DA IA ---
else:
    # Barra lateral para informações e botão de Sair
    with st.sidebar:
        st.write(f"👤 Conectado como: **{st.session_state.usuario_email}**")
        if st.button("Sair da Conta"):
            st.session_state.logado = False
            st.session_state.usuario_email = ""
            st.session_state.historico_chat = []
            st.rerun()

    st.title("⚡ Painel do Assistente IA")
    st.write("Sua IA comercial está pronta para responder aos seus clientes.")
    
    # Exibe o histórico de mensagens na tela com visual de chat profissional
    for mensagem in st.session_state.historico_chat:
        with st.chat_message(mensagem["role"]):
            st.write(mensagem["content"])

    # Campo de texto estilo Chat para o utilizador digitar a pergunta
    if prompt := st.chat_input("Como posso ajudar o seu negócio hoje?"):
        # Mostra a mensagem do utilizador no chat
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.historico_chat.append({"role": "user", "content": prompt})
        
        # Gera a resposta chamando a IA nos bastidores
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                resposta_ia = enviar_mensagem_ia(prompt, st.session_state.historico_chat)
                st.write(resposta_ia)
        st.session_state.historico_chat.append({"role": "assistant", "content": resposta_ia})
