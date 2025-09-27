# gestor_acoes_streamlit.py
import json
import os
import uuid
from datetime import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = "actions_data.json"

# ---------------- Persistência ----------------
def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def salvar_dados(lista_de_acoes):
    if os.path.exists(DATA_FILE):
        backup_file = DATA_FILE.replace(".json", "_backup.json")
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                with open(backup_file, "w", encoding="utf-8") as b:
                    b.write(f.read())
        except Exception:
            pass
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(lista_de_acoes, f, ensure_ascii=False, indent=2)

# ---------------- Funções ----------------
def adicionar_acao(lista_de_acoes, nome, data, local):
    nova_acao = {
        "acao_id": str(uuid.uuid4()),
        "nome_acao": nome,
        "data_acao": data,
        "local_acao": local,
        "visitantes": []
    }
    lista_de_acoes.append(nova_acao)
    salvar_dados(lista_de_acoes)
    st.success("Ação adicionada!")

def adicionar_visitante(lista_de_acoes, acao_id, equipe, origem, quantidade, status, observacoes):
    visitante = {
        "visitante_id": str(uuid.uuid4()),
        "data_hora_registro": datetime.now().isoformat(timespec="seconds"),
        "equipe_responsavel": equipe,
        "origem_visitante": origem,
        "quantidade_pessoas": quantidade,
        "observacoes_visitante": observacoes,
        "status_contrato": status
    }
    for acao in lista_de_acoes:
        if acao["acao_id"] == acao_id:
            acao["visitantes"].append(visitante)
            break
    salvar_dados(lista_de_acoes)
    st.success("Visitante adicionado!")

def atualizar_visitante(lista_de_acoes, acao_id, visitante_id, equipe, origem, quantidade, status, observacoes):
    for acao in lista_de_acoes:
        if acao["acao_id"] == acao_id:
            for v in acao["visitantes"]:
                if v["visitante_id"] == visitante_id:
                    v["equipe_responsavel"] = equipe
                    v["origem_visitante"] = origem
                    v["quantidade_pessoas"] = quantidade
                    v["status_contrato"] = status
                    v["observacoes_visitante"] = observacoes
                    salvar_dados(lista_de_acoes)
                    st.success("Visitante atualizado!")
                    return

def remover_visitante(lista_de_acoes, acao_id, visitante_id):
    for acao in lista_de_acoes:
        if acao["acao_id"] == acao_id:
            acao["visitantes"] = [v for v in acao["visitantes"] if v["visitante_id"] != visitante_id]
            salvar_dados(lista_de_acoes)
            st.success("Visitante removido!")
            return

def exportar_csv(lista_de_acoes):
    linhas = []
    for acao in lista_de_acoes:
        for v in acao.get("visitantes", []):
            linhas.append({
                "Ação": acao["nome_acao"],
                "Data": acao["data_acao"],
                "Local": acao["local_acao"],
                "Equipe": v["equipe_responsavel"],
                "Origem": v["origem_visitante"],
                "Qtd Pessoas": v["quantidade_pessoas"],
                "Status Contrato": v["status_contrato"],
                "Observações": v["observacoes_visitante"]
            })
    return pd.DataFrame(linhas)

# ---------------- Streamlit ----------------
st.set_page_config(page_title="Gestor de Ações de Rua", layout="wide")
st.title("🏡 Gestor de Ações de Rua - Imobiliária")

lista_de_acoes = carregar_dados()
tabs = st.tabs(["📌 Ações", "🙋 Visitantes", "📊 Gráficos", "💾 Exportar CSV"])

# ---------------- Aba Ações ----------------
with tabs[0]:
    st.subheader("Adicionar nova ação")
    nome = st.text_input("Nome da Ação")
    data = st.text_input("Data da Ação (YYYY-MM-DD)")
    local = st.text_input("Local da Ação")
    if st.button("➕ Adicionar Ação"):
        if not nome or not data or not local:
            st.warning("Preencha todos os campos.")
        else:
            adicionar_acao(lista_de_acoes, nome, data, local)

    st.subheader("Lista de Ações")
    if lista_de_acoes:
        for acao in lista_de_acoes:
            with st.expander(f"{acao['nome_acao']} — {acao['data_acao']} ({acao['local_acao']})"):
                st.write(f"ID: {acao['acao_id']}")
                st.write(f"Data: {acao['data_acao']}")
                st.write(f"Local: {acao['local_acao']}")
                if st.button(f"❌ Excluir Ação: {acao['nome_acao']}", key=acao['acao_id']):
                    lista_de_acoes.remove(acao)
                    salvar_dados(lista_de_acoes)
                    st.experimental_rerun()

# ---------------- Aba Visitantes ----------------
with tabs[1]:
    st.subheader("Adicionar visitante")
    if lista_de_acoes:
        acao_selecionada = st.selectbox("Ação associada", options=lista_de_acoes,
                                        format_func=lambda x: f"{x['nome_acao']} — {x['data_acao']} ({x['local_acao']})")
        equipe = st.text_input("Equipe Responsável")
        origem = st.selectbox("Origem do Visitante", ["Folheto", "Folha impressa", "Agendamento", "Viu a ação e veio ver"])
        quantidade = st.number_input("Quantidade de Pessoas", min_value=1, step=1)
        status = st.selectbox("Status do Contrato", ["nenhum_contrato", "contrato_por_acao", "contrato_fora_acao"])
        observacoes = st.text_area("Observações")
        if st.button("➕ Adicionar Visitante"):
            adicionar_visitante(lista_de_acoes, acao_selecionada['acao_id'], equipe, origem, quantidade, status, observacoes)

    st.subheader("Visitantes")
    for acao in lista_de_acoes:
        for v in acao.get("visitantes", []):
            with st.expander(f"{v['equipe_responsavel']} — {acao['nome_acao']}"):
                st.write(f"Origem: {v['origem_visitante']}")
                st.write(f"Qtd Pessoas: {v['quantidade_pessoas']}")
                st.write(f"Status: {v['status_contrato']}")
                st.write(f"Observações: {v['observacoes_visitante']}")
                
                equipe_edit = st.text_input("Equipe Responsável", value=v['equipe_responsavel'], key=v['visitante_id']+"_equipe")
                origem_edit = st.selectbox("Origem do Visitante", ["Folheto", "Folha impressa", "Agendamento", "Viu a ação e veio ver"], index=["Folheto", "Folha impressa", "Agendamento", "Viu a ação e veio ver"].index(v['origem_visitante']), key=v['visitante_id']+"_origem")
                quantidade_edit = st.number_input("Qtd Pessoas", min_value=1, value=v['quantidade_pessoas'], key=v['visitante_id']+"_qtd")
                status_edit = st.selectbox("Status do Contrato", ["nenhum_contrato", "contrato_por_acao", "contrato_fora_acao"], index=["nenhum_contrato", "contrato_por_acao", "contrato_fora_acao"].index(v['status_contrato']), key=v['visitante_id']+"_status")
                observacoes_edit = st.text_area("Observações", value=v['observacoes_visitante'], key=v['visitante_id']+"_obs")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Salvar Alterações", key=v['visitante_id']+"_salvar"):
                        atualizar_visitante(lista_de_acoes, acao['acao_id'], v['visitante_id'],
                                           equipe_edit, origem_edit, quantidade_edit, status_edit, observacoes_edit)
                        st.experimental_rerun()
                with col2:
                    if st.button("❌ Remover Visitante", key=v['visitante_id']+"_remover"):
                        remover_visitante(lista_de_acoes, acao['acao_id'], v['visitante_id'])
                        st.experimental_rerun()

# ---------------- Aba Gráficos ----------------
with tabs[2]:
    st.subheader("Gráfico de Visitantes por Ação")
    nomes = [a["nome_acao"] for a in lista_de_acoes]
    qtds = [len(a.get("visitantes", [])) for a in lista_de_acoes]
    if nomes:
        fig, ax = plt.subplots()
        ax.bar(nomes, qtds, color='skyblue')
        ax.set_ylabel("Nº de Visitantes")
        ax.set_xlabel("Ações")
        ax.set_title("Visitantes por Ação")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
    else:
        st.info("Nenhuma ação para exibir gráfico.")

    st.subheader("Gráfico de Status de Contrato por Ação")
    if lista_de_acoes:
        acao_selecionada_graf = st.selectbox("Selecione uma ação", lista_de_acoes,
                                             format_func=lambda x: f"{x['nome_acao']} — {x['data_acao']} ({x['local_acao']})", key="graf")
        status = [v["status_contrato"] for v in acao_selecionada_graf.get("visitantes", [])]
        if status:
            labels = list(set(status))
            counts = [status.count(l) for l in labels]
            fig2, ax2 = plt.subplots()
            ax2.pie(counts, labels=labels, autopct="%1.1f%%", startangle=140)
            ax2.set_title(f"Status de Contrato - {acao_selecionada_graf['nome_acao']}")
            st.pyplot(fig2)
        else:
            st.info("Nenhum visitante nesta ação para gráfico.")

# ---------------- Aba Exportar CSV ----------------
with tabs[3]:
    st.subheader("Exportar CSV")
    df_export = exportar_csv(lista_de_acoes)
    if not df_export.empty:
        st.dataframe(df_export)
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Baixar CSV", data=csv_data, file_name="visitantes.csv", mime="text/csv")
    else:
        st.info("Nenhum dado para exportar.")
