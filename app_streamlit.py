# app_streamlit.py
import streamlit as st
from agent_core import (load_csv, detect_column_types, descriptive_stats, 
                        plot_histogram, plot_correlation_heatmap, answer_question, 
                        OUTPUT_DIR, load_memory)
import os
import pandas as pd

st.set_page_config(page_title="Agente EDA Autônomo", layout="wide")

# CSS customizado
st.markdown("""
    <style>
    .main-title {font-size: 2.5rem; color: #1f77b4; font-weight: bold;}
    .section-header {font-size: 1.8rem; color: #ff7f0e; margin-top: 2rem;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🤖 Agente Autônomo de EDA - Análise Exploratória de Dados</p>', unsafe_allow_html=True)
st.markdown("**Carregue qualquer arquivo CSV e faça perguntas sobre os dados**")

uploaded_file = st.file_uploader("📁 Escolha um arquivo CSV", type=["csv"])

if uploaded_file is None:
    st.info("👆 Faça upload de um arquivo CSV para começar a análise")
    st.markdown("---")
    st.subheader("📋 Exemplos de perguntas que você pode fazer:")
    st.markdown("""
    - Quais são os tipos de dados?
    - Mostre a distribuição de [nome_coluna]
    - Qual o intervalo das variáveis numéricas?
    - Quais são as medidas de tendência central?
    - Existe correlação entre as variáveis?
    - Detecte outliers nos dados
    - Qual a taxa de fraude? (para datasets com classe)
    - Quais são as conclusões do agente?
    """)
else:
    df = load_csv(uploaded_file)
    
    # Sidebar com info rápida
    st.sidebar.header("📊 Visão Geral")
    st.sidebar.metric("Linhas", f"{len(df):,}")
    st.sidebar.metric("Colunas", len(df.columns))
    st.sidebar.metric("Células", f"{len(df) * len(df.columns):,}")
    
    if st.sidebar.button("🔍 Detectar Tipos de Colunas"):
        types = detect_column_types(df)
        st.sidebar.write("**Tipos detectados:**")
        for col, tipo in types.items():
            st.sidebar.write(f"• {col}: `{tipo}`")
    
    # Tabs para organizar
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Dados", "💬 Perguntas ao Agente", "🛠️ Ferramentas Rápidas", "🧠 Memória"])
    
    with tab1:
        st.header("Tabela de Dados (primeiras 100 linhas)")
        st.dataframe(df.head(100), use_container_width=True)
        
        st.subheader("📈 Estatísticas Descritivas")
        st.dataframe(df.describe(), use_container_width=True)
    
    with tab2:
        st.header("💬 Faça perguntas ao agente")
        st.markdown("O agente analisará automaticamente seus dados e responderá suas perguntas.")
        
        q = st.text_input("🔎 Insira sua pergunta:", 
                         placeholder="Ex: Quais são os tipos de dados?",
                         help="Digite sua pergunta em linguagem natural")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            perguntar_btn = st.button("🚀 Perguntar", type="primary")
        
        if perguntar_btn and q:
            with st.spinner("Processando..."):
                resp = answer_question(df, q)
                
                st.success("✅ Resposta do agente:")
                
                # Formatação baseada no tipo
                if resp.get("type") == "types":
                    st.json(resp.get("answer"))
                elif resp.get("type") == "proportion":
                    ans = resp.get("answer")
                    st.write(f"**Coluna analisada:** {ans['column']}")
                    st.write(f"**Total de registros:** {ans['total']:,}")
                    st.write("**Contagens:**")
                    for k, v in ans['counts'].items():
                        st.write(f"  • Classe {k}: {v:,} ({ans['proportions'][k]:.2f}%)")
                elif resp.get("type") == "correlation":
                    ans = resp.get("answer")
                    if isinstance(ans, dict) and "correlations" in ans:
                        st.write(f"**Top 10 correlações com {ans['target']}:**")
                        for col, corr in ans['correlations']:
                            st.write(f"  • {col}: {corr:.4f}")
                    else:
                        st.write(ans)
                elif resp.get("type") == "outliers":
                    ans = resp.get("answer")
                    st.write("**Outliers detectados (método IQR):**")
                    for col, info in list(ans['iqr_summary'].items())[:5]:
                        st.write(f"  • {col}: {info['n_outliers']} outliers")
                    st.write(f"**Outliers detectados (Isolation Forest):** {ans['isolation_forest_outliers']}")
                else:
                    st.write(resp.get("answer"))
                
                if resp.get("artifact"):
                    st.image(resp.get("artifact"), use_container_width=True)
    
    with tab3:
        st.header("🛠️ Ferramentas Rápidas")
        
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        
        if numeric_cols:
            col = st.selectbox("Selecione uma coluna numérica:", numeric_cols)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Gerar Histograma"):
                    hist_path = os.path.join(OUTPUT_DIR, f"hist_{col}.png")
                    plot_histogram(df, col, save_as=hist_path)
                    st.image(hist_path, use_container_width=True)
            
            with col2:
                if st.button("📦 Gerar Boxplot"):
                    from agent_core import plot_boxplot
                    box_path = os.path.join(OUTPUT_DIR, f"box_{col}.png")
                    plot_boxplot(df, col, save_as=box_path)
                    st.image(box_path, use_container_width=True)
        
        st.markdown("---")
        
        if st.button("🔥 Gerar Heatmap de Correlação"):
            if len(numeric_cols) < 2:
                st.warning("⚠️ São necessárias pelo menos 2 colunas numéricas para calcular correlação.")
            else:
                path = os.path.join(OUTPUT_DIR, "corr_heatmap.png")
                plot_correlation_heatmap(df, numeric_cols, save_as=path)
                st.image(path, use_container_width=True)
    
    with tab4:
        st.header("🧠 Memória do Agente")
        st.markdown("Histórico de análises realizadas nesta sessão:")
        
        mem = load_memory()
        if mem["analyses"]:
            for i, entry in enumerate(reversed(mem["analyses"][-10:]), 1):
                with st.expander(f"📌 Análise {i}: {entry['question'][:50]}..."):
                    st.write(f"**Pergunta:** {entry['question']}")
                    st.write(f"**Resumo:** {entry['summary']}")
                    st.write(f"**Timestamp:** {entry['timestamp']}")
                    if entry['artifacts']:
                        st.write(f"**Artefatos gerados:** {len(entry['artifacts'])}")
        else:
            st.info("Nenhuma análise realizada ainda. Faça perguntas na aba 'Perguntas ao Agente'.")
        
        if st.button("🗑️ Limpar Memória"):
            import json
            with open("memory.json", "w") as f:
                json.dump({"analyses": []}, f)
            st.success("Memória limpa!")
            st.rerun()

st.markdown("---")
st.markdown("*Desenvolvido para a disciplina de Agentes Autônomos - Atividade Extra*")