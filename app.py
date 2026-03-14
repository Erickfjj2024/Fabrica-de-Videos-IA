import streamlit as st
from groq import Groq

st.title("Fábrica de Vídeos IA 🎬")
st.write("Crie roteiros completos em segundos.")

# AQUI ESTÁ A MÁGICA DA SEGURANÇA: Ele vai buscar a chave no "cofre" do Streamlit
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

tema_usuario = st.text_input("Qual o tema do vídeo?", placeholder="Ex: Histórias de terror narradas")
tom_usuario = st.selectbox("Qual o tom da narração?", ["Sombrio e Misterioso", "Engraçado", "Educativo", "Dramático"])

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
        
        # Usando o modelo novo e poderoso que você encontrou!
        resposta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt_completo}],
            temperature=0.7
        )
        
        st.success("Roteiro Gerado com Sucesso!")
        st.markdown(resposta.choices[0].message.content)
    else:
        st.warning("Por favor, digite um tema para o vídeo primeiro!")

