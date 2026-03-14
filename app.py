import streamlit as st
from groq import Groq

# --- SISTEMA DE LOGIN (O SEGURANÇA) ---

def password_entered():
    """Verifica se a senha digitada bate com a do cofre (Secrets)."""
    if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
        st.session_state["password_correct"] = True
        del st.session_state["password"]  # Apaga a senha da memória por segurança
    else:
        st.session_state["password_correct"] = False

def check_password():
    """Retorna True se o usuário tiver a senha correta."""
    if "password_correct" not in st.session_state:
        st.title("🔒 Acesso Restrito")
        st.text_input(
            "Digite a senha para acessar a Fábrica de Vídeos:",
            type="password",
            on_change=password_entered,
            key="password",
        )
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔒 Acesso Restrito")
        st.text_input(
            "Digite a senha para acessar a Fábrica de Vídeos:",
            type="password",
            on_change=password_entered,
            key="password",
        )
        st.error("🚫 Senha incorreta. Tente novamente.")
        return False
    else:
        return True


if check_password():
    st.title("Fábrica de Vídeos IA 🎬")
    st.write("Crie roteiros completos em segundos.")

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    tema_usuario = st.text_input("Qual o tema do vídeo?", placeholder="Ex: Histórias de terror narradas")
    tom_usuario = st.selectbox(
        "Qual o tom da narração?",
        ["Sombrio e Misterioso", "Engraçado", "Educativo", "Dramático"],
    )

    if st.button("Gerar Roteiro Mágico"):
        if tema_usuario:
            st.info("A IA está trabalhando. Aguarde... 🧠")

            prompt_completo = f"""
            <system_role>
            You are an elite viral short-video scriptwriter.
            The final output MUST be written entirely in Brazilian Portuguese (pt-BR), EXCEPT for the image prompts which MUST be strictly in English.
            </system_role>

            <user_parameters>
            - Topic: {tema_usuario}
            - Tone: {tom_usuario}
            </user_parameters>

            <strict_rules>
            1. NO CONVERSATIONAL FILLER.
            2. The Hook (first 3 seconds) must be highly controversial.
            3. Keep the script concise (approx. 120-150 words).
            4. The image prompts must be highly detailed and end with "--ar 9:16".
            </strict_rules>

            <output_format>
            **🔥 Gancho (0-3s):** [Hook here]
            **📜 Roteiro:** [Markdown Table with Narração and Cena]

            **🎨 Prompts de Imagem (MUST BE IN ENGLISH):**
            1. [English prompt 1]
            2. [English prompt 2]
            3. [English prompt 3]

            **📱 Metadados:** [Legenda e Hashtags]
            </output_format>
            """

            resposta = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_completo}],
                temperature=0.7,
            )

            st.success("Roteiro Gerado com Sucesso!")
            st.markdown(resposta.choices[0].message.content)
        else:
            st.warning("Por favor, digite um tema para o vídeo primeiro!")

