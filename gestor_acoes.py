import json
import os
import uuid
from datetime import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

# ---------------- Streamlit Config ----------------
st.set_page_config(page_title="Gestor de Ações de Rua", layout="wide", page_icon="🏡")
st.markdown(
    """
    <style>
    /* Background geral da página */
    .stApp {
        background-color: #696969;
        color: #FFFFFF;
    }

    /* Cabeçalhos e títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF;
    }

    /* Rótulos dos campos de entrada */
    label, .stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label {
        color: #FFFFFF !important;
        font-weight: normal;
    }

    /* Inputs e text areas */
    div.stTextInput > div > input,
    div.stNumberInput > div > input,
    div.stTextArea > div > textarea,
    div.stSelectbox > div > div > div > select {
        background-color: #333333;
        color: #FFFFFF;
        border: 1px solid #FF0000;
    }

    /* Placeholders */
    div.stTextInput > div > input::placeholder,
    div.stNumberInput > div > input::placeholder,
    div.stTextArea > div > textarea::placeholder {
        color: #BBBBBB;
        opacity: 1;
    }

    /* Botões */
    div.stButton > button {
        background-color: #FF0000;
        color: #FFFFFF;
        border: none;
        border-radius: 4px;
    }

    /* Hover nos botões */
    div.stButton > button:hover {
        background-color: #CC0000;
    }

    /* Dataframes */
    .stDataFrame div.row-widget.stDataFrameWidget {
        background-color: #111111;
        color: #FFFFFF;
    }

    /* Estilizar bordas e texto do dataframe */
    .stDataFrame table {
        border-collapse: collapse;
    }
    .stDataFrame th, .stDataFrame td {
        border: 1px solid #FFFFFF;
        color: #FFFFFF;
    }

    /* Estilizar selectbox para consistência */
    .stSelectbox > div > div > div > select {
        background-color: #333333;
        color: #FFFFFF;
    }

    /* Estilizar opções do selectbox */
    .stSelectbox option {
        background-color: #333333;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# ---------------- Resumo Geral ----------------
st.header("📈 Resumo Geral")
if lista_de_acoes:
    total_visitantes = sum(len(a.get("visitantes", [])) for a in lista_de_acoes)
    total_contratos = sum(
        1 for a in lista_de_acoes for v in a.get("visitantes", [])
        if v["status_contrato"] != "nenhum_contrato"
    )
    taxa_conversao = (total_contratos / total_visitantes * 100) if total_visitantes else 0

    st.metric("Total de Visitantes", total_visitantes)
    st.metric("Total de Contratos Fechados", total_contratos)
    st.metric("Taxa de Conversão (%)", f"{taxa_conversao:.1f}")

    # Alertas e destaques
    acoes_sem_visitantes = [a for a in lista_de_acoes if not a.get("visitantes")]
    visitantes_sem_contrato = [
        (a["nome_acao"], v) for a in lista_de_acoes for v in a.get("visitantes", [])
        if v["status_contrato"] == "nenhum_contrato"
    ]

    if acoes_sem_visitantes:
        st.warning(f"Atenção: {len(acoes_sem_visitantes)} ação(ões) sem visitantes cadastrados!")
    if visitantes_sem_contrato:
        st.warning(f"Atenção: {len(visitantes_sem_contrato)} visitante(s) sem contrato registrado!")

# ---------------- Gráficos ----------------
st.header("📊 Gráficos")
if lista_de_acoes:
    # Visitantes por ação
    nomes = [a["nome_acao"] for a in lista_de_acoes]
    qtds = [len(a.get("visitantes", [])) for a in lista_de_acoes]
    fig, ax = plt.subplots()
    ax.bar(nomes, qtds, color='red')
    ax.set_ylabel("Nº de Visitantes", color="white")
    ax.set_xlabel("Ações", color="white")
    ax.set_title("Visitantes por Ação", color="white")
    ax.tick_params(axis='x', rotation=45, colors="white")
    ax.tick_params(axis='y', colors="white")
    st.pyplot(fig)

    # Status de contrato da ação selecionada
    if acao_selecionada and visitantes:
        status = [v["status_contrato"] for v in visitantes]
        labels = list(set(status))
        counts = [status.count(l) for l in labels]
        fig2, ax2 = plt.subplots()
        ax2.pie(counts, labels=labels, autopct="%1.1f%%", startangle=140, colors=['#ff0000', '#ffffff', '#808080'])
        ax2.set_title(f"Status de Contrato - {acao_alvo['nome_acao']}", color="white")
        st.pyplot(fig2)

    # Evolução temporal
    st.subheader("📅 Evolução Temporal")
    all_visits = []
    for a in lista_de_acoes:
        for v in a.get("visitantes", []):
            all_visits.append({
                "acao": a["nome_acao"],
                "data": pd.to_datetime(v["data_hora_registro"]),
                "contrato": 1 if v["status_contrato"] != "nenhum_contrato" else 0
            })
    if all_visits:
        df_time = pd.DataFrame(all_visits)
        df_time.sort_values("data", inplace=True)
        df_cum = df_time.groupby(["data", "acao"]).agg(
            visitantes_cum=pd.NamedAgg(column="acao", aggfunc="count"),
            contratos_cum=pd.NamedAgg(column="contrato", aggfunc="sum")
        ).groupby(level=1).cumsum().reset_index()

        fig3, ax3 = plt.subplots()
        for acao in df_cum["acao"].unique():
            df_plot = df_cum[df_cum["acao"] == acao]
            ax3.plot(df_plot["data"], df_plot["visitantes_cum"], label=f"{acao} - Visitantes", color="red")
            ax3.plot(df_plot["data"], df_plot["contratos_cum"], label=f"{acao} - Contratos", color="white")
        ax3.set_xlabel("Data", color="white")
        ax3.set_ylabel("Cumulativo", color="white")
        ax3.set_title("Evolução de Visitantes e Contratos", color="white")
        ax3.legend()
        ax3.tick_params(axis='x', colors="white")
        ax3.tick_params(axis='y', colors="white")
        st.pyplot(fig3)

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