import streamlit as st
from groq import Groq
from supabase import create_client
from datetime import date

# Conexão Supabase
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def main():
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        st.title("🎬 Fábrica de Vídeos IA")
        t1, t2 = st.tabs(["Entrar", "Criar Conta"])
        with t1:
            e = st.text_input("E-mail")
            s = st.text_input("Senha", type="password")
            if st.button("Acessar"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": e, "password": s})
                    st.session_state.user = res.user
                    st.rerun()
                except: st.error("Erro no acesso.")
        with t2:
            ne = st.text_input("E-mail Novo")
            ns = st.text_input("Senha Nova", type="password")
            if st.button("Cadastrar"):
                try:
                    supabase.auth.sign_up({"email": ne, "password": ns})
                    st.success("Conta criada! Volte para 'Entrar'.")
                except Exception as ex: st.error(f"Erro: {ex}")
    else:
        painel_geracao()

def painel_geracao():
    user_id = st.session_state.user.id
    hoje = str(date.today()) # Pega a data de hoje (ex: 2026-03-14)

    # 1. Busca os dados do perfil
    res = supabase.table("perfis").select("*").eq("id", user_id).execute()
    
    if len(res.data) == 0:
        # Usuário novo: cria o registro com a data de hoje
        res = supabase.table("perfis").insert({
            "id": user_id, 
            "email": st.session_state.user.email,
            "ultimo_reset": hoje
        }).execute()
        dados = res.data[0]
    else:
        dados = res.data[0]
        
        # --- LÓGICA DE RESET DIÁRIO ---
        if str(dados["ultimo_reset"]) != hoje:
            # Se a data guardada é diferente de hoje, zeramos os usados e atualizamos a data
            supabase.table("perfis").update({
                "usados_hoje": 0,
                "ultimo_reset": hoje
            }).eq("id", user_id).execute()
            # Recarrega os dados atualizados
            res = supabase.table("perfis").select("*").eq("id", user_id).execute()
            dados = res.data[0]

    limite = dados["limite_diario"]
    usados = dados["usados_hoje"]

    # Barra Lateral
    st.sidebar.title("💳 Seus Créditos")
    st.sidebar.metric("Disponível hoje", f"{limite - usados} de {limite}")
    if st.sidebar.button("Sair"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # App Principal
    st.title("Fábrica de Vídeos IA 🎬")
    tema = st.text_input("Sobre o que será o vídeo?")
    
    if st.button("Gerar Roteiro"):
        if usados >= limite:
            st.error("🚫 Seus créditos de hoje acabaram! Volte amanhã para ganhar mais 3.")
        elif not tema:
            st.warning("Digite um tema.")
        else:
            with st.spinner("IA criando roteiro..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": f"Crie um roteiro viral sobre: {tema}"}]
                    )
                    
                    # Consome o crédito no banco de dados
                    supabase.table("perfis").update({"usados_hoje": usados + 1}).eq("id", user_id).execute()
                    
                    st.success("Roteiro gerado!")
                    st.markdown(resp.choices[0].message.content)
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro: {err}")

if __name__ == "__main__":
    main()
