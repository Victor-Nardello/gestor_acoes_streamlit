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
    # Backup automático
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

# ---------------- App ----------------
st.set_page_config(page_title="Gestor de Ações de Rua", layout="wide")
st.title("🏡 Gestor de Ações de Rua - Imobiliária")

lista_de_acoes = carregar_dados()

# ---------------- Aba Ações ----------------
st.header("📌 Ações")
with st.form("form_acao", clear_on_submit=True):
    nome_acao = st.text_input("Nome da Ação")
    data_acao = st.text_input("Data da Ação (YYYY-MM-DD)")
    local_acao = st.text_input("Local da Ação")
    submitted = st.form_submit_button("➕ Adicionar Ação")
    if submitted:
        if not nome_acao or not data_acao or not local_acao:
            st.error("Preencha todos os campos da ação.")
        else:
            nova_acao = {
                "acao_id": str(uuid.uuid4()),
                "nome_acao": nome_acao,
                "data_acao": data_acao,
                "local_acao": local_acao,
                "visitantes": []
            }
            lista_de_acoes.append(nova_acao)
            salvar_dados(lista_de_acoes)
            st.success("Ação adicionada com sucesso!")

if lista_de_acoes:
    df_acoes = pd.DataFrame([{
        "Nome": a["nome_acao"],
        "Data": a["data_acao"],
        "Local": a["local_acao"],
        "Visitantes": len(a.get("visitantes", []))
    } for a in lista_de_acoes])
    st.dataframe(df_acoes)

# ---------------- Aba Visitantes ----------------
st.header("🙋 Visitantes")
acoes_dict = {f"{a['nome_acao']} — {a['data_acao']} ({a['local_acao']})": a["acao_id"] for a in lista_de_acoes}
acao_selecionada = st.selectbox("Ação associada", options=list(acoes_dict.keys()) if acoes_dict else [])

with st.form("form_visitante", clear_on_submit=True):
    equipe_responsavel = st.text_input("Equipe Responsável")
    origem_visitante = st.selectbox("Origem do Visitante", ["Folheto", "Folha impressa", "Agendamento", "Viu a ação e veio ver"])
    quantidade_pessoas = st.number_input("Quantidade de Pessoas", min_value=0, step=1)
    status_contrato = st.selectbox("Status do Contrato", ["nenhum_contrato", "contrato_por_acao", "contrato_fora_acao"])
    observacoes = st.text_area("Observações")
    submitted_v = st.form_submit_button("➕ Adicionar Visitante")
    if submitted_v:
        if not acao_selecionada:
            st.warning("Selecione uma ação antes de adicionar visitantes.")
        else:
            acao_id = acoes_dict[acao_selecionada]
            acao_alvo = next(a for a in lista_de_acoes if a["acao_id"] == acao_id)
            visitante = {
                "visitante_id": str(uuid.uuid4()),
                "data_hora_registro": datetime.now().isoformat(timespec="seconds"),
                "equipe_responsavel": equipe_responsavel,
                "origem_visitante": origem_visitante,
                "quantidade_pessoas": int(quantidade_pessoas),
                "observacoes_visitante": observacoes,
                "status_contrato": status_contrato
            }
            acao_alvo["visitantes"].append(visitante)
            salvar_dados(lista_de_acoes)
            st.success("Visitante adicionado com sucesso!")

# Mostrar visitantes da ação selecionada
if acao_selecionada:
    acao_id = acoes_dict[acao_selecionada]
    acao_alvo = next(a for a in lista_de_acoes if a["acao_id"] == acao_id)
    visitantes = acao_alvo.get("visitantes", [])
    if visitantes:
        df_visitantes = pd.DataFrame([{
            "Data/Hora": v["data_hora_registro"],
            "Equipe": v["equipe_responsavel"],
            "Origem": v["origem_visitante"],
            "Qtd Pessoas": v["quantidade_pessoas"],
            "Contrato": v["status_contrato"],
            "Observações": v["observacoes_visitante"]
        } for v in visitantes])
        st.dataframe(df_visitantes)
    else:
        st.info("Nenhum visitante cadastrado para esta ação.")

# ---------------- Gráficos ----------------
st.header("📊 Gráficos")

# Gráfico de visitantes por ação
if lista_de_acoes:
    nomes = [a["nome_acao"] for a in lista_de_acoes]
    qtds = [len(a.get("visitantes", [])) for a in lista_de_acoes]
    fig, ax = plt.subplots()
    ax.bar(nomes, qtds, color='skyblue')
    ax.set_ylabel("Nº de Visitantes")
    ax.set_xlabel("Ações")
    ax.set_title("Visitantes por Ação")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

# Gráfico de status de contrato da ação selecionada
if acao_selecionada and visitantes:
    status = [v["status_contrato"] for v in visitantes]
    labels = list(set(status))
    counts = [status.count(l) for l in labels]
    fig2, ax2 = plt.subplots()
    ax2.pie(counts, labels=labels, autopct="%1.1f%%", startangle=140)
    ax2.set_title(f"Status de Contrato - {acao_alvo['nome_acao']}")
    st.pyplot(fig2)

# ---------------- Export CSV ----------------
if st.button("💾 Exportar CSV"):
    all_rows = []
    for a in lista_de_acoes:
        for v in a.get("visitantes", []):
            all_rows.append({
                "Ação": a["nome_acao"],
                "Data": a["data_acao"],
                "Local": a["local_acao"],
                "Equipe": v["equipe_responsavel"],
                "Origem": v["origem_visitante"],
                "Qtd Pessoas": v["quantidade_pessoas"],
                "Status Contrato": v["status_contrato"],
                "Observações": v["observacoes_visitante"]
            })
    if all_rows:
        df_all = pd.DataFrame(all_rows)
        df_all.to_csv("export_visitantes.csv", index=False, encoding="utf-8")
        st.success("Arquivo CSV exportado como 'export_visitantes.csv'.")
    else:
        st.info("Não há dados para exportar.")
