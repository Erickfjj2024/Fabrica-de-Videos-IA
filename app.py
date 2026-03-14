import streamlit as st
from groq import Groq
from supabase import create_client

# 1. Conexão com o Banco de Dados (Supabase)
# Ele busca os dados que você colocou nos Secrets do Streamlit
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def main():
    st.set_page_config(page_title="Fábrica de Vídeos IA", page_icon="🎬")

    # Inicializa o estado do usuário
    if "user" not in st.session_state:
        st.session_state.user = None

    # TELA DE LOGIN / CADASTRO
    if st.session_state.user is None:
        st.title("🎬 Fábrica de Vídeos IA")
        st.write("Acesse sua conta para criar roteiros virais.")
        
        aba_login, aba_cadastro = st.tabs(["Conectar", "Criar Conta"])
        
        with aba_login:
            email = st.text_input("E-mail", key="l_email")
            senha = st.text_input("Senha", type="password", key="l_pass")
            if st.button("Entrar"):
                try:
                    # Tenta logar no Supabase
                    res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                    st.session_state.user = res.user
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                except Exception:
                    st.error("E-mail ou senha inválidos.")

        with aba_cadastro:
            novo_email = st.text_input("Novo E-mail", key="r_email")
            nova_senha = st.text_input("Nova Senha (mín. 6 caracteres)", type="password", key="r_pass")
            if st.button("Cadastrar"):
                try:
                    # Cria o usuário no banco de dados
                    supabase.auth.sign_up({"email": novo_email, "password": nova_senha})
                    st.success("Conta criada! Agora clique na aba 'Conectar' para entrar.")
                except Exception as e:
                    st.error(f"Erro ao criar conta: {e}")

    else:
        # SE ESTIVER LOGADO, MOSTRA O APP
        painel_geracao()

def painel_geracao():
    # Barra lateral de logout
    st.sidebar.title("Configurações")
    st.sidebar.write(f"Conectado como: **{st.session_state.user.email}**")
    if st.sidebar.button("Sair"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # --- MOTOR DE GERAÇÃO (GROQ) ---
    st.title("Fábrica de Vídeos IA 🎬")
    st.write("Crie roteiros completos em segundos.")

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    tema = st.text_input("Qual o tema do vídeo?", placeholder="Ex: Histórias de terror narradas")
    tom = st.selectbox("Qual o tom da narração?", ["Sombrio", "Engraçado", "Educativo", "Dramático"])

    if st.button("Gerar Roteiro Mágico"):
        if tema:
            with st.spinner("IA processando seu roteiro..."):
                prompt_completo = f"""
                <system_role>
                You are an elite viral short-video scriptwriter.
                The final output MUST be in pt-BR, EXCEPT for image prompts in English.
                </system_role>
                <user_parameters>
                - Topic: {tema} 
                - Tone: {tom}
                </user_parameters>
                <output_format>
                **🔥 Gancho (0-3s):** [Hook]
                **📜 Roteiro:** [Markdown Table]
                **🎨 Prompts de Imagem (ENGLISH):** [Detailed prompts with --ar 9:16]
                **📱 Metadados:** [Caption and Hashtags]
                </output_format>
                """
                
                resposta = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt_completo}],
                    temperature=0.7
                )
                
                st.success("Roteiro pronto!")
                st.markdown(resposta.choices[0].message.content)
        else:
            st.warning("Por favor, digite um tema.")

if __name__ == "__main__":
    main()
