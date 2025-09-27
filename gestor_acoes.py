import json
import os
import uuid
from datetime import datetime
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

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

# ---------------- Streamlit Config ----------------
st.set_page_config(page_title="Gestor de Ações de Rua", layout="wide", page_icon="🏡")
st.markdown(
    """
    <style>
    /* Background geral da página */
    .stApp {
        background-color: #FFFFFF;
        color: #FFFFFF;
        font-family: 'Arial', sans-serif;
    }

    /* Cabeçalhos */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF;
        font-weight: 600;
        margin-bottom: 10px;
    }

    /* Rótulos dos campos */
    label, .stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label {
        color: #FFFFFF !important;
        font-size: 16px;
        font-weight: 500;
    }

    /* Inputs e text areas */
    div.stTextInput > div > input,
    div.stNumberInput > div > input,
    div.stTextArea > div > textarea,
    div.stSelectbox > div > div > div > select {
        background-color: #1A1A1A;
        color: #000000;
        border: 2px solid #FF0000;
        border-radius: 5px;
        padding: 8px;
        font-size: 14px;
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
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: 500;
        transition: background-color 0.3s ease;
    }

    /* Hover nos botões */
    div.stButton > button:hover {
        background-color: #CC0000;
        box-shadow: 0 2px 5px rgba(255, 0, 0, 0.3);
    }

    /* Dataframes */
    .stDataFrame table {
        background-color: #1A1A1A;
        color: #FFFFFF;
        border-collapse: collapse;
        border-radius: 5px;
        overflow: hidden;
    }
    .stDataFrame th, .stDataFrame td {
        border: 1px solid #FF0000;
        padding: 10px;
        color: #FFFFFF;
    }
    .stDataFrame th {
        background-color: #FF0000;
        color: #FFFFFF;
        font-weight: 600;
    }

    /* Selectbox */
    .stSelectbox > div > div > div > select {
        background-color: #1A1A1A;
        color: #FFFFFF;
    }
    .stSelectbox option {
        background-color: #1A1A1A;
        color: #FFFFFF;
    }

    /* Divisores */
    .stDivider {
        background-color: #FF0000;
        height: 2px;
        margin: 20px 0;
    }

    /* Estilizar métricas */
    .stMetric label {
        color: #FFFFFF;
        font-size: 16px;
    }
    .stMetric .metric-value {
        color: #FF0000;
        font-weight: 600;
    }

    /* Estilizar alertas */
    .stAlert {
        background-color: #1A1A1A;
        color: #FFFFFF;
        border: 1px solid #FF0000;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🏡 Gestor de Ações de Rua - Imobiliária")
st.markdown("---")

lista_de_acoes = carregar_dados()

# ---------------- Aba Ações ----------------
st.header("📌 Ações")
col1, col2 = st.columns([2, 1])
with col1:
    with st.form("form_acao", clear_on_submit=True):
        nome_acao = st.text_input("Nome da Ação")
        data_acao = st.text_input("Data da Ação (YYYY-MM-DD)")
        local_acao = st.text_input("Local da Ação")
        submitted = st.form_submit_button("➕ Adicionar Ação")
        if submitted:
            if not nome_acao or not data_acao or not local_acao:
                st.error("Preencha todos os campos da ação.")
            else:
                try:
                    datetime.strptime(data_acao, "%Y-%m-%d")
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
                except ValueError:
                    st.error("Formato de data inválido. Use YYYY-MM-DD (ex.: 2025-09-27).")

with col2:
    st.markdown("### Lista de Ações")
    if lista_de_acoes:
        df_acoes = pd.DataFrame([{
            "Nome": a["nome_acao"],
            "Data": a["data_acao"],
            "Local": a["local_acao"],
            "Visitantes": len(a.get("visitantes", []))
        } for a in lista_de_acoes]).sort_values("Data", ascending=False)
        st.dataframe(df_acoes, use_container_width=True)
    else:
        st.info("Nenhuma ação cadastrada.")

st.markdown("---")

# ---------------- Aba Visitantes ----------------
st.header("🙋 Visitantes")
col1, col2 = st.columns([2, 1])
with col1:
    acoes_dict = {f"{a['nome_acao']} — {a['data_acao']} ({a['local_acao']})": a["acao_id"] for a in lista_de_acoes}
    acao_selecionada = st.selectbox("Ação associada", options=list(acoes_dict.keys()) if acoes_dict else [])
    with st.form("form_visitante", clear_on_submit=True):
        equipe_responsavel = st.text_input("Equipe Responsável")
        origem_visitante = st.selectbox("Origem do Visitante", ["Folheto", "Folha impressa", "Agendamento", "Viu a ação e veio ver"])
        quantidade_pessoas = st.number_input("Quantidade de Pessoas", min_value=1, step=1)
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

with col2:
    st.markdown("### Visitantes da Ação Selecionada")
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
            st.dataframe(df_visitantes, use_container_width=True)
        else:
            st.info("Nenhum visitante cadastrado para esta ação.")

st.markdown("---")

# ---------------- Resumo Geral ----------------
st.header("📈 Resumo Geral")
if lista_de_acoes:
    total_visitantes = sum(len(a.get("visitantes", [])) for a in lista_de_acoes)
    total_contratos = sum(
        1 for a in lista_de_acoes for v in a.get("visitantes", [])
        if v["status_contrato"] != "nenhum_contrato"
    )
    taxa_conversao = (total_contratos / total_visitantes * 100) if total_visitantes else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Visitantes", total_visitantes)
    col2.metric("Total de Contratos Fechados", total_contratos)
    col3.metric("Taxa de Conversão (%)", f"{taxa_conversao:.1f}")

    acoes_sem_visitantes = [a for a in lista_de_acoes if not a.get("visitantes")]
    visitantes_sem_contrato = [
        (a["nome_acao"], v) for a in lista_de_acoes for v in a.get("visitantes", [])
        if v["status_contrato"] == "nenhum_contrato"
    ]

    if acoes_sem_visitantes:
        st.warning(f"Atenção: {len(acoes_sem_visitantes)} ação(ões) sem visitantes cadastrados!")
    if visitantes_sem_contrato:
        st.warning(f"Atenção: {len(visitantes_sem_contrato)} visitante(s) sem contrato registrado!")

st.markdown("---")

# ---------------- Gráficos ----------------
st.header("📊 Gráficos")
if lista_de_acoes:
    # Gráfico de barras: Visitantes por ação
    nomes = [a["nome_acao"] for a in lista_de_acoes]
    qtds = [len(a.get("visitantes", [])) for a in lista_de_acoes]
    chart_data = {
        "type": "bar",
        "data": {
            "labels": nomes,
            "datasets": [{
                "label": "Nº de Visitantes",
                "data": qtds,
                "backgroundColor": "#FF0000",
                "borderColor": "#FFFFFF",
                "borderWidth": 1
            }]
        },
        "options": {
            "scales": {
                "y": {
                    "beginAtZero": true,
                    "title": {
                        "display": true,
                        "text": "Nº de Visitantes",
                        "color": "#FFFFFF",
                        "font": {"size": 14}
                    },
                    "ticks": {"color": "#FFFFFF"}
                },
                "x": {
                    "title": {
                        "display": true,
                        "text": "Ações",
                        "color": "#FFFFFF",
                        "font": {"size": 14}
                    },
                    "ticks": {
                        "color": "#FFFFFF",
                        "maxRotation": 45,
                        "minRotation": 45
                    }
                }
            },
            "plugins": {
                "legend": {
                    "labels": {
                        "color": "#FFFFFF",
                        "font": {"size": 14}
                    }
                },
                "title": {
                    "display": true,
                    "text": "Visitantes por Ação",
                    "color": "#FFFFFF",
                    "font": {"size": 16}
                }
            }
        }
    }
    components.html(f"""
        <div style="background-color: #000000; padding: 20px; border-radius: 10px;">
            <canvas id="barChart"></canvas>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script>
                const ctx = document.getElementById('barChart').getContext('2d');
                new Chart(ctx, {json.dumps(chart_data)});
            </script>
        </div>
    """, height=400)

    # Gráfico de pizza: Status de contrato
    if acao_selecionada:
        acao_id = acoes_dict[acao_selecionada]
        acao_alvo = next(a for a in lista_de_acoes if a["acao_id"] == acao_id)
        visitantes = acao_alvo.get("visitantes", [])
        if visitantes:
            status = [v["status_contrato"] for v in visitantes]
            labels = list(set(status))
            counts = [status.count(l) for l in labels]
            chart_data_pie = {
                "type": "pie",
                "data": {
                    "labels": labels,
                    "datasets": [{
                        "data": counts,
                        "backgroundColor": ["#FF0000", "#FFFFFF", "#BBBBBB"],
                        "borderColor": "#000000",
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "plugins": {
                        "legend": {
                            "labels": {
                                "color": "#FFFFFF",
                                "font": {"size": 14}
                            }
                        },
                        "title": {
                            "display": true,
                            "text": f"Status de Contrato - {acao_alvo['nome_acao']}",
                            "color": "#FFFFFF",
                            "font": {"size": 16}
                        }
                    }
                }
            }
            components.html(f"""
                <div style="background-color: #000000; padding: 20px; border-radius: 10px;">
                    <canvas id="pieChart"></canvas>
                    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                    <script>
                        const ctxPie = document.getElementById('pieChart').getContext('2d');
                        new Chart(ctxPie, {json.dumps(chart_data_pie)});
                    </script>
                </div>
            """, height=400)

    # Gráfico de linha: Evolução temporal
    st.subheader("📅 Evolução Temporal")
    all_visits = []
    for a in lista_de_acoes:
        for v in a.get("visitantes", []):
            all_visits.append({
                "acao": a["nome_acao"],
                "data": pd.to_datetime(v["data_hora_registro"]).strftime("%Y-%m-%d"),
                "contrato": 1 if v["status_contrato"] != "nenhum_contrato" else 0
            })
    if all_visits:
        df_time = pd.DataFrame(all_visits)
        df_time.sort_values("data", inplace=True)
        df_cum = df_time.groupby(["data", "acao"]).agg(
            visitantes_cum=pd.NamedAgg(column="acao", aggfunc="count"),
            contratos_cum=pd.NamedAgg(column="contrato", aggfunc="sum")
        ).groupby(level=1).cumsum().reset_index()

        datasets = []
        for acao in df_cum["acao"].unique():
            df_plot = df_cum[df_cum["acao"] == acao]
            datasets.append({
                "label": f"{acao} - Visitantes",
                "data": df_plot["visitantes_cum"].tolist(),
                "borderColor": "#FF0000",
                "fill": False
            })
            datasets.append({
                "label": f"{acao} - Contratos",
                "data": df_plot["contratos_cum"].tolist(),
                "borderColor": "#FFFFFF",
                "fill": False
            })
        chart_data_line = {
            "type": "line",
            "data": {
                "labels": df_cum["data"].unique().tolist(),
                "datasets": datasets
            },
            "options": {
                "scales": {
                    "y": {
                        "beginAtZero": true,
                        "title": {
                            "display": true,
                            "text": "Cumulativo",
                            "color": "#FFFFFF",
                            "font": {"size": 14}
                        },
                        "ticks": {"color": "#FFFFFF"}
                    },
                    "x": {
                        "title": {
                            "display": true,
                            "text": "Data",
                            "color": "#FFFFFF",
                            "font": {"size": 14}
                        },
                        "ticks": {"color": "#FFFFFF"}
                    }
                },
                "plugins": {
                    "legend": {
                        "labels": {
                            "color": "#FFFFFF",
                            "font": {"size": 14}
                        }
                    },
                    "title": {
                        "display": true,
                        "text": "Evolução de Visitantes e Contratos",
                        "color": "#FFFFFF",
                        "font": {"size": 16}
                    }
                }
            }
        }
        components.html(f"""
            <div style="background-color: #000000; padding: 20px; border-radius: 10px;">
                <canvas id="lineChart"></canvas>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <script>
                    const ctxLine = document.getElementById('lineChart').getContext('2d');
                    new Chart(ctxLine, {json.dumps(chart_data_line)});
                </script>
            </div>
        """, height=400)

st.markdown("---")

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