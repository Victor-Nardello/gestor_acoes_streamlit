import json
import os
import uuid
import re
from datetime import datetime
import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

DATA_FILE = "actions_data.json"

# ---------------- Persistência ----------------
# Nota: Para grandes volumes de dados, considere usar SQLite:
# import sqlite3
# conn = sqlite3.connect("acoes.db")
# c.execute('''CREATE TABLE IF NOT EXISTS acoes (...)''')
@st.cache_data
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

# ---------------- Funções Auxiliares ----------------
def validar_texto(texto):
    return bool(re.match(r'^[a-zA-Z0-9\s\-\(\)]+$', texto))

def gerar_pdf(lista_de_acoes, acao_selecionada=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    style = styles["Heading1"]
    style.textColor = colors.black

    elements.append(Paragraph("Relatório - Gestor de Ações de Rua", style))
    data = [["Ação", "Data", "Local", "Equipe", "Origem", "Qtd Pessoas", "Contrato", "Observações"]]
    for a in lista_de_acoes:
        if acao_selecionada and a["acao_id"] != acao_selecionada:
            continue
        for v in a.get("visitantes", []):
            data.append([
                a["nome_acao"], a["data_acao"], a["local_acao"],
                v["equipe_responsavel"], v["origem_visitante"],
                str(v["quantidade_pessoas"]), v["status_contrato"],
                v["observacoes_visitante"]
            ])
    if len(data) > 1:
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.red),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Nenhum dado disponível.", styles["Normal"]))
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------------- Streamlit Config ----------------
st.set_page_config(page_title="Gestor de Ações de Rua", layout="wide", page_icon="🏡")
st.markdown(
    """
    <style>
    /* Background geral da página */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
        font-family: 'Arial', sans-serif;
    }

    /* Cabeçalhos */
    h1, h2, h3, h4, h5, h6 {
        color: #000000;
        font-weight: 600;
        margin-bottom: 10px;
    }

    /* Rótulos dos campos */
    label, .stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label {
        color: #000000 !important;
        font-size: 16px;
        font-weight: 500;
    }

    /* Inputs e text areas */
    div.stTextInput > div > input,
    div.stNumberInput > div > input,
    div.stTextArea > div > textarea,
    div.stSelectbox > div > div > div > select {
        background-color: #FFFFFF;
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
        color: #666666;
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
        transition: transform 0.2s ease, background-color 0.3s ease;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }

    /* Hover nos botões */
    div.stButton > button:hover {
        background-color: #CC0000;
        transform: scale(1.05);
    }

    /* Dataframes */
    .stDataFrame table {
        background-color: #FFFFFF;
        color: #000000;
        border-collapse: collapse;
        border-radius: 5px;
        overflow: hidden;
    }
    .stDataFrame th, .stDataFrame td {
        border: 1px solid #FF0000;
        padding: 10px;
        color: #000000;
    }
    .stDataFrame th {
        background-color: #FF0000;
        color: #FFFFFF;
        font-weight: 600;
    }

    /* Selectbox */
    .stSelectbox > div > div > div > select {
        background-color: #FFFFFF;
        color: #000000;
    }
    .stSelectbox option {
        background-color: #FFFFFF;
        color: #000000;
    }

    /* Divisores */
    .stDivider {
        background-color: #FF0000;
        height: 2px;
        margin: 20px 0;
    }

    /* Estilizar métricas */
    .stMetric label {
        color: #000000;
        font-size: 16px;
    }
    .stMetric .metric-value {
        color: #FF0000;
        font-weight: 600;
    }

    /* Estilizar alertas */
    .stAlert {
        background-color: #FFFFFF;
        color: #000000;
        border: 1px solid #FF0000;
        border-radius: 5px;
    }

    /* Estilizar container de edição */
    .edit-container {
        background-color: #F5F5F5;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #FF0000;
        margin-bottom: 20px;
    }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """,
    unsafe_allow_html=True
)

# Logotipo (substitua pelo caminho real do logotipo da imobiliária)
# st.image("logo_imobiliaria.png", width=150)
st.title('<i class="fas fa-home"></i> Gestor de Ações de Rua - Imobiliária', unsafe_allow_html=True)
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# Gamificação
lista_de_acoes = carregar_dados()
if len(lista_de_acoes) >= 5:
    st.success("🎉 Parabéns! Você cadastrou 5 ações!")

# Abas
tab1, tab2, tab3, tab4 = st.tabs([
    '<i class="fas fa-map-pin"></i> Ações',
    '<i class="fas fa-users"></i> Visitantes',
    '<i class="fas fa-chart-line"></i> Resumo Geral',
    '<i class="fas fa-download"></i> Exportar'
])

# ---------------- Aba Ações ----------------
with tab1:
    st.header('<i class="fas fa-map-pin"></i> Ações', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.form("form_acao", clear_on_submit=True):
            nome_acao = st.text_input("Nome da Ação")
            data_acao = st.text_input("Data da Ação (YYYY-MM-DD)")
            local_acao = st.text_input("Local da Ação")
            submitted = st.form_submit_button('<i class="fas fa-plus"></i> Adicionar Ação', unsafe_allow_html=True)
            if submitted:
                if not nome_acao or not data_acao or not local_acao:
                    st.error("Preencha todos os campos da ação.")
                elif not validar_texto(nome_acao) or not validar_texto(local_acao):
                    st.error("Nome e local da ação devem conter apenas letras, números, espaços, hífens ou parênteses.")
                else:
                    try:
                        datetime.strptime(data_acao, "%Y-%m-%d")
                        with st.spinner("Salvando ação..."):
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

        # Formulário de edição
        if lista_de_acoes:
            acao_para_editar = st.selectbox("Editar Ação", options=[f"{a['nome_acao']} — {a['data_acao']} ({a['local_acao']})" for a in lista_de_acoes], key="edit_acao_select")
            if acao_para_editar:
                acao_id = next(a["acao_id"] for a in lista_de_acoes if f"{a['nome_acao']} — {a['data_acao']} ({a['local_acao']})" == acao_para_editar)
                acao = next(a for a in lista_de_acoes if a["acao_id"] == acao_id)
                with st.container():
                    st.markdown('<div class="edit-container">', unsafe_allow_html=True)
                    st.subheader("Editar Ação")
                    with st.form("form_edit_acao", clear_on_submit=True):
                        edit_nome = st.text_input("Nome da Ação", value=acao["nome_acao"])
                        edit_data = st.text_input("Data da Ação (YYYY-MM-DD)", value=acao["data_acao"])
                        edit_local = st.text_input("Local da Ação", value=acao["local_acao"])
                        submitted_edit = st.form_submit_button('<i class="fas fa-save"></i> Salvar Alterações', unsafe_allow_html=True)
                        if submitted_edit:
                            if not edit_nome or not edit_data or not edit_local:
                                st.error("Preencha todos os campos da ação.")
                            elif not validar_texto(edit_nome) or not validar_texto(edit_local):
                                st.error("Nome e local da ação devem conter apenas letras, números, espaços, hífens ou parênteses.")
                            else:
                                try:
                                    datetime.strptime(edit_data, "%Y-%m-%d")
                                    with st.spinner("Salvando alterações..."):
                                        acao["nome_acao"] = edit_nome
                                        acao["data_acao"] = edit_data
                                        acao["local_acao"] = edit_local
                                        salvar_dados(lista_de_acoes)
                                        st.success("Ação atualizada com sucesso!")
                                        st.rerun()
                                except ValueError:
                                    st.error("Formato de data inválido. Use YYYY-MM-DD (ex.: 2025-09-27).")
                    st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("### Lista de Ações")
        if lista_de_acoes:
            filtro_data = st.date_input("Filtrar por Data", value=None, key="filtro_acao_data")
            df_acoes = pd.DataFrame([{
                "Nome": a["nome_acao"],
                "Data": a["data_acao"],
                "Local": a["local_acao"],
                "Visitantes": len(a.get("visitantes", [])),
                "Ação": a["acao_id"]
            } for a in lista_de_acoes]).sort_values("Data", ascending=False)
            if filtro_data:
                df_acoes = df_acoes[df_acoes["Data"] == filtro_data.strftime("%Y-%m-%d")]
            for i, row in df_acoes.iterrows():
                cols = st.columns([3, 1])
                with cols[0]:
                    st.write(f"{row['Nome']} — {row['Data']} ({row['Local']}) - {row['Visitantes']} visitantes")
                with cols[1]:
                    if st.button('<i class="fas fa-trash"></i> Excluir', key=f"delete_acao_{row['Ação']}", unsafe_allow_html=True):
                        with st.spinner("Excluindo ação..."):
                            lista_de_acoes = [a for a in lista_de_acoes if a["acao_id"] != row["Ação"]]
                            salvar_dados(lista_de_acoes)
                            st.success("Ação excluída com sucesso!")
                            st.rerun()
            st.dataframe(df_acoes.drop(columns=["Ação"]), use_container_width=True)
        else:
            st.info("Nenhuma ação cadastrada.")
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# ---------------- Aba Visitantes ----------------
with tab2:
    st.header('<i class="fas fa-users"></i> Visitantes', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        acoes_dict = {f"{a['nome_acao']} — {a['data_acao']} ({a['local_acao']})": a["acao_id"] for a in lista_de_acoes}
        acao_selecionada = st.selectbox("Ação associada", options=list(acoes_dict.keys()) if acoes_dict else [], key="visitante_acao_select")
        with st.form("form_visitante", clear_on_submit=True):
            equipe_responsavel = st.text_input("Equipe Responsável")
            origem_visitante = st.selectbox("Origem do Visitante", ["Folheto", "Folha impressa", "Agendamento", "Viu a ação e veio ver"])
            quantidade_pessoas = st.number_input("Quantidade de Pessoas", min_value=1, step=1)
            status_contrato = st.selectbox("Status do Contrato", ["nenhum_contrato", "contrato_por_acao", "contrato_fora_acao"])
            observacoes = st.text_area("Observações")
            submitted_v = st.form_submit_button('<i class="fas fa-plus"></i> Adicionar Visitante', unsafe_allow_html=True)
            if submitted_v:
                if not acao_selecionada:
                    st.warning("Selecione uma ação antes de adicionar visitantes.")
                elif not validar_texto(equipe_responsavel) and equipe_responsavel:
                    st.error("Equipe responsável deve conter apenas letras, números, espaços, hífens ou parênteses.")
                else:
                    with st.spinner("Salvando visitante..."):
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

        # Formulário de edição de visitante
        if acao_selecionada:
            acao_id = acoes_dict[acao_selecionada]
            acao_alvo = next(a for a in lista_de_acoes if a["acao_id"] == acao_id)
            visitantes = acao_alvo.get("visitantes", [])
            if visitantes:
                visitante_para_editar = st.selectbox("Editar Visitante", options=[f"{v['data_hora_registro']} - {v['equipe_responsavel']}" for v in visitantes], key="edit_visitante_select")
                if visitante_para_editar:
                    visitante_id = next(v["visitante_id"] for v in visitantes if f"{v['data_hora_registro']} - {v['equipe_responsavel']}" == visitante_para_editar)
                    visitante = next(v for v in visitantes if v["visitante_id"] == visitante_id)
                    with st.container():
                        st.markdown('<div class="edit-container">', unsafe_allow_html=True)
                        st.subheader("Editar Visitante")
                        with st.form("form_edit_visitante", clear_on_submit=True):
                            edit_equipe = st.text_input("Equipe Responsável", value=visitante["equipe_responsavel"])
                            edit_origem = st.selectbox("Origem do Visitante", ["Folheto", "Folha impressa", "Agendamento", "Viu a ação e veio ver"], index=["Folheto", "Folha impressa", "Agendamento", "Viu a ação e veio ver"].index(visitante["origem_visitante"]))
                            edit_quantidade = st.number_input("Quantidade de Pessoas", min_value=1, step=1, value=visitante["quantidade_pessoas"])
                            edit_status = st.selectbox("Status do Contrato", ["nenhum_contrato", "contrato_por_acao", "contrato_fora_acao"], index=["nenhum_contrato", "contrato_por_acao", "contrato_fora_acao"].index(visitante["status_contrato"]))
                            edit_observacoes = st.text_area("Observações", value=visitante["observacoes_visitante"])
                            submitted_edit_v = st.form_submit_button('<i class="fas fa-save"></i> Salvar Alterações', unsafe_allow_html=True)
                            if submitted_edit_v:
                                if not validar_texto(edit_equipe) and edit_equipe:
                                    st.error("Equipe responsável deve conter apenas letras, números, espaços, hífens ou parênteses.")
                                else:
                                    with st.spinner("Salvando alterações..."):
                                        visitante["equipe_responsavel"] = edit_equipe
                                        visitante["origem_visitante"] = edit_origem
                                        visitante["quantidade_pessoas"] = int(edit_quantidade)
                                        visitante["status_contrato"] = edit_status
                                        visitante["observacoes_visitante"] = edit_observacoes
                                        salvar_dados(lista_de_acoes)
                                        st.success("Visitante atualizado com sucesso!")
                                        st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("### Visitantes da Ação Selecionada")
        if acao_selecionada:
            acao_id = acoes_dict[acao_selecionada]
            acao_alvo = next(a for a in lista_de_acoes if a["acao_id"] == acao_id)
            visitantes = acao_alvo.get("visitantes", [])
            if visitantes:
                filtro_status = st.selectbox("Filtrar por Status do Contrato", ["Todos", "nenhum_contrato", "contrato_por_acao", "contrato_fora_acao"], key="filtro_status")
                df_visitantes = pd.DataFrame([{
                    "Data/Hora": v["data_hora_registro"],
                    "Equipe": v["equipe_responsavel"],
                    "Origem": v["origem_visitante"],
                    "Qtd Pessoas": v["quantidade_pessoas"],
                    "Contrato": v["status_contrato"],
                    "Observações": v["observacoes_visitante"],
                    "Visitante": v["visitante_id"]
                } for v in visitantes])
                if filtro_status != "Todos":
                    df_visitantes = df_visitantes[df_visitantes["Contrato"] == filtro_status]
                for i, row in df_visitantes.iterrows():
                    cols = st.columns([3, 1])
                    with cols[0]:
                        st.write(f"{row['Data/Hora']} - {row['Equipe']} ({row['Origem']}) - {row['Qtd Pessoas']} pessoas")
                    with cols[1]:
                        if st.button('<i class="fas fa-trash"></i> Excluir', key=f"delete_visitante_{row['Visitante']}", unsafe_allow_html=True):
                            with st.spinner("Excluindo visitante..."):
                                acao_alvo["visitantes"] = [v for v in visitantes if v["visitante_id"] != row["Visitante"]]
                                salvar_dados(lista_de_acoes)
                                st.success("Visitante excluído com sucesso!")
                                st.rerun()
                st.dataframe(df_visitantes.drop(columns=["Visitante"]), use_container_width=True)
            else:
                st.info("Nenhum visitante cadastrado para esta ação.")
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# ---------------- Aba Resumo Geral ----------------
with tab3:
    st.header('<i class="fas fa-chart-line"></i> Resumo Geral', unsafe_allow_html=True)
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
            st.error(f"🚨 Atenção: {len(acoes_sem_visitantes)} ação(ões) sem visitantes cadastrados!")
        if visitantes_sem_contrato:
            st.warning(f"⚠️ Atenção: {len(visitantes_sem_contrato)} visitante(s) sem contrato registrado!")
    else:
        st.info("Nenhum dado disponível para resumo.")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# ---------------- Aba Exportar ----------------
with tab4:
    st.header('<i class="fas fa-download"></i> Exportar', unsafe_allow_html=True)
    export_type = st.radio("Tipo de Exportação", ["CSV", "PDF"])
    acao_export = st.selectbox("Exportar para", options=["Todas as Ações"] + [f"{a['nome_acao']} — {a['data_acao']} ({a['local_acao']})" for a in lista_de_acoes], key="export_acao_select")
    
    if st.button('<i class="fas fa-file-export"></i> Exportar', unsafe_allow_html=True):
        if lista_de_acoes:
            with st.spinner("Gerando arquivo..."):
                if export_type == "CSV":
                    all_rows = []
                    for a in lista_de_acoes:
                        if acao_export != "Todas as Ações" and f"{a['nome_acao']} — {a['data_acao']} ({a['local_acao']})" != acao_export:
                            continue
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
                        csv = df_all.to_csv(index=False, encoding="utf-8")
                        st.download_button(
                            label="Baixar CSV",
                            data=csv,
                            file_name="export_visitantes.csv",
                            mime="text/csv"
                        )
                        st.success("Arquivo CSV gerado com sucesso!")
                    else:
                        st.info("Não há dados para exportar.")
                else:  # PDF
                    acao_id = None if acao_export == "Todas as Ações" else next(a["acao_id"] for a in lista_de_acoes if f"{a['nome_acao']} — {a['data_acao']} ({a['local_acao']})" == acao_export)
                    pdf_buffer = gerar_pdf(lista_de_acoes, acao_id)
                    st.download_button(
                        label="Baixar PDF",
                        data=pdf_buffer,
                        file_name="relatorio_acoes.pdf",
                        mime="application/pdf"
                    )
                    st.success("Arquivo PDF gerado com sucesso!")
        else:
            st.info("Não há dados para exportar.")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)