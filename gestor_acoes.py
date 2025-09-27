# gestor_acoes.py
import json
import os
import uuid
from datetime import datetime
import tkinter as tk
import tkinter.messagebox as tk_messagebox
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import matplotlib.pyplot as plt
import csv

DATA_FILE = "actions_data.json"

class GestorDeAcoesDeRua(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("🏡 Gestor de Ações de Rua - Imobiliária")
        self.geometry("1100x700")

        self.lista_de_acoes = []
        self.acao_selecionada = None

        self.carregar_dados()
        self.criar_widgets()
        self.atualizar_lista_acoes()

    # ---------------- Persistência ----------------
    def carregar_dados(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    self.lista_de_acoes = json.load(f)
                except Exception:
                    self.lista_de_acoes = []
        else:
            self.lista_de_acoes = []

    def salvar_dados(self):
        if os.path.exists(DATA_FILE):
            # backup automático
            backup_file = DATA_FILE.replace(".json", "_backup.json")
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    with open(backup_file, "w", encoding="utf-8") as b:
                        b.write(f.read())
            except Exception:
                pass
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.lista_de_acoes, f, ensure_ascii=False, indent=2)

    # ---------------- UI ----------------
    def criar_widgets(self):
        header = ttk.Label(self, text="📊 Gestão de Ações de Rua", font=("Segoe UI", 18, "bold"),
                           bootstyle="inverse-danger")
        header.pack(fill=tk.X, padx=0, pady=(8, 10))

        notebook = ttk.Notebook(self, bootstyle="dark")
        notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Aba Ações
        self.frame_acoes = ttk.Frame(notebook, padding=10)
        notebook.add(self.frame_acoes, text="📌 Ações")

        form_acoes = ttk.Frame(self.frame_acoes)
        form_acoes.pack(fill=tk.X, padx=6, pady=6)

        ttk.Label(form_acoes, text="Nome da Ação:", bootstyle="light").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_nome_acao = ttk.Entry(form_acoes, width=50, bootstyle="dark")
        self.entry_nome_acao.grid(row=0, column=1, sticky="ew", padx=6)

        ttk.Label(form_acoes, text="Data da Ação (YYYY-MM-DD):", bootstyle="light").grid(row=1, column=0, sticky="w",
                                                                                         pady=6)
        self.entry_data_acao = ttk.Entry(form_acoes, width=20, bootstyle="dark")
        self.entry_data_acao.grid(row=1, column=1, sticky="w", padx=6)

        ttk.Label(form_acoes, text="Local da Ação:", bootstyle="light").grid(row=2, column=0, sticky="w", pady=6)
        self.entry_local_acao = ttk.Entry(form_acoes, width=60, bootstyle="dark")
        self.entry_local_acao.grid(row=2, column=1, sticky="ew", padx=6)

        botoes_acoes = ttk.Frame(form_acoes)
        botoes_acoes.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(botoes_acoes, text="➕ Adicionar Ação", bootstyle="danger", command=self.adicionar_acao).pack(
            side="left", padx=6)
        ttk.Button(botoes_acoes, text="❌ Excluir Ação", bootstyle="secondary", command=self.excluir_acao).pack(
            side="left", padx=6)
        ttk.Button(botoes_acoes, text="📊 Gráfico Ações", bootstyle="info", command=self.gerar_grafico_acoes).pack(
            side="left", padx=6)

        self.tree_acoes = ttk.Treeview(self.frame_acoes, columns=("id", "nome", "data", "local"), show="headings",
                                       bootstyle="dark")
        self.tree_acoes.column("id", width=0, stretch=False)
        self.tree_acoes.heading("nome", text="Nome da Ação")
        self.tree_acoes.heading("data", text="Data")
        self.tree_acoes.heading("local", text="Local")
        self.tree_acoes.pack(fill=tk.BOTH, expand=True, padx=6, pady=12)
        self.tree_acoes.bind("<<TreeviewSelect>>", self.on_selecionar_acao_na_lista)
        self.tree_acoes.bind("<Double-1>", self.editar_acao_tree)

        # Aba Visitantes
        self.frame_visitantes = ttk.Frame(notebook, padding=10)
        notebook.add(self.frame_visitantes, text="🙋 Visitantes")

        form_visit = ttk.Frame(self.frame_visitantes)
        form_visit.pack(fill=tk.X, padx=6, pady=6)

        ttk.Label(form_visit, text="Ação associada:", bootstyle="light").grid(row=0, column=0, sticky="w", pady=6)
        self.combo_acao_associada = ttk.Combobox(form_visit, values=[], state="readonly", bootstyle="dark", width=60)
        self.combo_acao_associada.grid(row=0, column=1, sticky="ew", padx=6)

        ttk.Label(form_visit, text="Equipe Responsável:", bootstyle="light").grid(row=1, column=0, sticky="w",
                                                                                 pady=6)
        self.entry_equipe_responsavel = ttk.Entry(form_visit, width=40, bootstyle="dark")
        self.entry_equipe_responsavel.grid(row=1, column=1, sticky="ew", padx=6)

        ttk.Label(form_visit, text="Origem do Visitante:", bootstyle="light").grid(row=2, column=0, sticky="w",
                                                                                   pady=6)
        self.combo_origem_visitante = ttk.Combobox(form_visit,
                                                   values=["Folheto", "Folha impressa", "Agendamento",
                                                           "Viu a ação e veio ver"],
                                                   state="readonly", bootstyle="dark")
        self.combo_origem_visitante.grid(row=2, column=1, sticky="w", padx=6)

        ttk.Label(form_visit, text="Quantidade de Pessoas:", bootstyle="light").grid(row=3, column=0, sticky="w",
                                                                                     pady=6)
        self.entry_quantidade_pessoas = ttk.Entry(form_visit, width=8, bootstyle="dark")
        self.entry_quantidade_pessoas.grid(row=3, column=1, sticky="w", padx=6)

        ttk.Label(form_visit, text="Status do Contrato:", bootstyle="light").grid(row=4, column=0, sticky="w",
                                                                                   pady=6)
        self.combo_status_contrato = ttk.Combobox(form_visit,
                                                  values=["nenhum_contrato", "contrato_por_acao", "contrato_fora_acao"],
                                                  state="readonly", bootstyle="dark")
        self.combo_status_contrato.grid(row=4, column=1, sticky="w", padx=6)

        ttk.Label(form_visit, text="Observações:", bootstyle="light").grid(row=5, column=0, sticky="nw", pady=6)
        self.text_observacoes = tk.Text(form_visit, height=4, width=70)
        self.text_observacoes.grid(row=5, column=1, sticky="ew", padx=6)

        botoes_visit = ttk.Frame(form_visit)
        botoes_visit.grid(row=6, column=0, columnspan=2, pady=(8, 0))
        ttk.Button(botoes_visit, text="➕ Adicionar Visitante", bootstyle="danger",
                   command=self.adicionar_visitante).pack(side="left", padx=6)
        ttk.Button(botoes_visit, text="❌ Excluir Visitante", bootstyle="secondary",
                   command=self.excluir_visitante).pack(side="left", padx=6)
        ttk.Button(botoes_visit, text="📊 Gráfico Visitantes", bootstyle="info",
                   command=self.gerar_grafico_visitantes).pack(side="left", padx=6)
        ttk.Button(botoes_visit, text="💾 Exportar CSV", bootstyle="success",
                   command=self.exportar_csv).pack(side="left", padx=6)

        self.tree_visitantes = ttk.Treeview(self.frame_visitantes,
                                            columns=("id", "datahora", "equipe", "origem", "quantidade", "contrato"),
                                            show="headings", bootstyle="dark")
        self.tree_visitantes.column("id", width=0, stretch=False)
        self.tree_visitantes.heading("datahora", text="Data/Hora")
        self.tree_visitantes.heading("equipe", text="Equipe")
        self.tree_visitantes.heading("origem", text="Origem")
        self.tree_visitantes.heading("quantidade", text="Qtd Pessoas")
        self.tree_visitantes.heading("contrato", text="Contrato")
        self.tree_visitantes.pack(fill=tk.BOTH, expand=True, padx=6, pady=12)
        self.tree_visitantes.bind("<Double-1>", self.editar_visitante_tree)

        self._mapa_display_para_id_acao = {}

    # ---------------- Ações ----------------
    def adicionar_acao(self):
        nome = self.entry_nome_acao.get().strip()
        data = self.entry_data_acao.get().strip()
        local = self.entry_local_acao.get().strip()
        if not nome or not data or not local:
            Messagebox.show_error("Erro", "Preencha todos os campos da ação.")
            return
        nova_acao = {
            "acao_id": str(uuid.uuid4()),
            "nome_acao": nome,
            "data_acao": data,
            "local_acao": local,
            "visitantes": []
        }
        self.lista_de_acoes.append(nova_acao)
        self.salvar_dados()
        self.atualizar_lista_acoes()
        self.entry_nome_acao.delete(0, tk.END)
        self.entry_data_acao.delete(0, tk.END)
        self.entry_local_acao.delete(0, tk.END)

    def excluir_acao(self):
        selecionado = self.tree_acoes.selection()
        if not selecionado:
            Messagebox.show_warning("Aviso", "Selecione uma ação para excluir.")
            return
        acao_id = self.tree_acoes.item(selecionado[0])["values"][0]
        self.lista_de_acoes = [a for a in self.lista_de_acoes if a["acao_id"] != acao_id]
        self.salvar_dados()
        self.acao_selecionada = None
        self.atualizar_lista_acoes()
        self.atualizar_lista_visitantes()

    def atualizar_lista_acoes(self):
        self.tree_acoes.delete(*self.tree_acoes.get_children())
        display_vals = []
        self._mapa_display_para_id_acao.clear()
        for acao in self.lista_de_acoes:
            self.tree_acoes.insert("", tk.END,
                                   values=(acao["acao_id"], acao["nome_acao"], acao["data_acao"], acao["local_acao"]))
            display = f"{acao['nome_acao']} — {acao['data_acao']} ({acao['local_acao']})"
            display_vals.append(display)
            self._mapa_display_para_id_acao[display] = acao["acao_id"]
        self.combo_acao_associada['values'] = display_vals

    def on_selecionar_acao_na_lista(self, event):
        sel = self.tree_acoes.selection()
        if not sel:
            return
        acao_id = self.tree_acoes.item(sel[0])["values"][0]
        self.acao_selecionada = next((a for a in self.lista_de_acoes if a["acao_id"] == acao_id), None)
        if self.acao_selecionada:
            display = f"{self.acao_selecionada['nome_acao']} — {self.acao_selecionada['data_acao']} ({self.acao_selecionada['local_acao']})"
            try:
                self.combo_acao_associada.set(display)
            except Exception:
                pass
        self.atualizar_lista_visitantes()

    # ---------------- Visitantes ----------------
    def adicionar_visitante(self):
        valor_combo = self.combo_acao_associada.get().strip()
        acao_id_selecionada = self._mapa_display_para_id_acao.get(valor_combo)
        if not acao_id_selecionada:
            if self.lista_de_acoes:
                ultima = self.lista_de_acoes[-1]
                confirmar = tk_messagebox.askyesno("Confirmar",
                                                   f"Nenhuma ação selecionada. Deseja adicionar o visitante à última ação cadastrada:\n\n{ultima['nome_acao']} — {ultima['data_acao']} ({ultima['local_acao']})?")
                if confirmar:
                    acao_alvo = ultima
                    acao_id_selecionada = ultima["acao_id"]
                else:
                    Messagebox.show_warning("Aviso", "Selecione uma ação antes de adicionar visitantes.")
                    return
            else:
                Messagebox.show_warning("Aviso", "Nenhuma ação cadastrada. Crie uma ação primeiro.")
                return
        else:
            acao_alvo = next((a for a in self.lista_de_acoes if a["acao_id"] == acao_id_selecionada), None)

        if not acao_alvo:
            Messagebox.show_error("Erro", "Ação alvo não encontrada.")
            return

        equipe = self.entry_equipe_responsavel.get().strip()
        origem = self.combo_origem_visitante.get().strip()
        try:
            quantidade = int(self.entry_quantidade_pessoas.get() or "0")
        except ValueError:
            Messagebox.show_error("Erro", "Quantidade inválida.")
            return
        status_contrato = self.combo_status_contrato.get().strip()
        observacoes = self.text_observacoes.get("1.0", tk.END).strip()

        visitante = {
            "visitante_id": str(uuid.uuid4()),
            "data_hora_registro": datetime.now().isoformat(timespec="seconds"),
            "equipe_responsavel": equipe,
            "origem_visitante": origem,
            "quantidade_pessoas": quantidade,
            "observacoes_visitante": observacoes,
            "status_contrato": status_contrato
        }

        acao_alvo["visitantes"].append(visitante)
        self.salvar_dados()
        self.acao_selecionada = acao_alvo
        self.atualizar_lista_visitantes()

        self.entry_equipe_responsavel.delete(0, tk.END)
        self.combo_origem_visitante.set("")
        self.entry_quantidade_pessoas.delete(0, tk.END)
        self.combo_status_contrato.set("")
        self.text_observacoes.delete("1.0", tk.END)
        Messagebox.show_info("Sucesso", "Visitante adicionado com sucesso.")

    def excluir_visitante(self):
        selecionado = self.tree_visitantes.selection()
        if not selecionado or not self.acao_selecionada:
            Messagebox.show_warning("Aviso", "Selecione um visitante para excluir.")
            return
        visitante_id = self.tree_visitantes.item(selecionado[0])["values"][0]
        self.acao_selecionada["visitantes"] = [v for v in self.acao_selecionada["visitantes"] if
                                               v["visitante_id"] != visitante_id]
        self.salvar_dados()
        self.atualizar_lista_visitantes()

    def atualizar_lista_visitantes(self):
        self.tree_visitantes.delete(*self.tree_visitantes.get_children())
        if not self.acao_selecionada:
            return
        for v in self.acao_selecionada.get("visitantes", []):
            self.tree_visitantes.insert("", tk.END, values=(v["visitante_id"], v["data_hora_registro"], v["equipe_responsavel"],
                                                           v["origem_visitante"], v["quantidade_pessoas"],
                                                           v["status_contrato"]))

    # ---------------- Edição rápida ----------------
    def editar_acao_tree(self, event):
        item = self.tree_acoes.selection()[0]
        acao_id = self.tree_acoes.item(item)["values"][0]
        acao = next((a for a in self.lista_de_acoes if a["acao_id"] == acao_id), None)
        if not acao:
            return
        # Janela simples de edição
        win = tk.Toplevel(self)
        win.title("Editar Ação")
        ttk.Label(win, text="Nome:").grid(row=0, column=0)
        entry_nome = ttk.Entry(win)
        entry_nome.insert(0, acao["nome_acao"])
        entry_nome.grid(row=0, column=1)
        ttk.Label(win, text="Data (YYYY-MM-DD):").grid(row=1, column=0)
        entry_data = ttk.Entry(win)
        entry_data.insert(0, acao["data_acao"])
        entry_data.grid(row=1, column=1)
        ttk.Label(win, text="Local:").grid(row=2, column=0)
        entry_local = ttk.Entry(win)
        entry_local.insert(0, acao["local_acao"])
        entry_local.grid(row=2, column=1)

        def salvar_edicao():
            acao["nome_acao"] = entry_nome.get().strip()
            acao["data_acao"] = entry_data.get().strip()
            acao["local_acao"] = entry_local.get().strip()
            self.salvar_dados()
            self.atualizar_lista_acoes()
            win.destroy()

        ttk.Button(win, text="Salvar", command=salvar_edicao).grid(row=3, column=0, columnspan=2, pady=6)

    def editar_visitante_tree(self, event):
        if not self.acao_selecionada:
            return
        item = self.tree_visitantes.selection()[0]
        visitante_id = self.tree_visitantes.item(item)["values"][0]
        visitante = next((v for v in self.acao_selecionada["visitantes"] if v["visitante_id"] == visitante_id), None)
        if not visitante:
            return
        win = tk.Toplevel(self)
        win.title("Editar Visitante")
        ttk.Label(win, text="Equipe:").grid(row=0, column=0)
        entry_equipe = ttk.Entry(win)
        entry_equipe.insert(0, visitante["equipe_responsavel"])
        entry_equipe.grid(row=0, column=1)
        ttk.Label(win, text="Origem:").grid(row=1, column=0)
        combo_origem = ttk.Combobox(win, values=["Folheto", "Folha impressa", "Agendamento", "Viu a ação e veio ver"])
        combo_origem.set(visitante["origem_visitante"])
        combo_origem.grid(row=1, column=1)
        ttk.Label(win, text="Qtd Pessoas:").grid(row=2, column=0)
        entry_qtd = ttk.Entry(win)
        entry_qtd.insert(0, str(visitante["quantidade_pessoas"]))
        entry_qtd.grid(row=2, column=1)
        ttk.Label(win, text="Status Contrato:").grid(row=3, column=0)
        combo_status = ttk.Combobox(win, values=["nenhum_contrato", "contrato_por_acao", "contrato_fora_acao"])
        combo_status.set(visitante["status_contrato"])
        combo_status.grid(row=3, column=1)
        ttk.Label(win, text="Observações:").grid(row=4, column=0)
        text_obs = tk.Text(win, height=4, width=30)
        text_obs.insert("1.0", visitante["observacoes_visitante"])
        text_obs.grid(row=4, column=1)

        def salvar_edicao():
            visitante["equipe_responsavel"] = entry_equipe.get().strip()
            visitante["origem_visitante"] = combo_origem.get().strip()
            try:
                visitante["quantidade_pessoas"] = int(entry_qtd.get())
            except ValueError:
                Messagebox.show_error("Erro", "Quantidade inválida.")
                return
            visitante["status_contrato"] = combo_status.get().strip()
            visitante["observacoes_visitante"] = text_obs.get("1.0", tk.END).strip()
            self.salvar_dados()
            self.atualizar_lista_visitantes()
            win.destroy()

        ttk.Button(win, text="Salvar", command=salvar_edicao).grid(row=5, column=0, columnspan=2, pady=6)

    # ---------------- Export CSV ----------------
    def exportar_csv(self):
        arquivo = filedialog.asksaveasfilename(defaultextension=".csv",
                                               filetypes=[("CSV files", "*.csv")])
        if not arquivo:
            return
        with open(arquivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Ação", "Data", "Local", "Equipe", "Origem", "Qtd Pessoas", "Status Contrato", "Observações"])
            for acao in self.lista_de_acoes:
                for v in acao.get("visitantes", []):
                    writer.writerow([acao["nome_acao"], acao["data_acao"], acao["local_acao"],
                                     v["equipe_responsavel"], v["origem_visitante"], v["quantidade_pessoas"],
                                     v["status_contrato"], v["observacoes_visitante"]])
        Messagebox.show_info("Sucesso", f"Arquivo CSV exportado para {arquivo}")

    # ---------------- Gráficos ----------------
    def gerar_grafico_acoes(self):
        nomes = [a["nome_acao"] for a in self.lista_de_acoes]
        qtds = [len(a.get("visitantes", [])) for a in self.lista_de_acoes]
        plt.figure(figsize=(10, 5))
        plt.bar(nomes, qtds, color='skyblue')
        plt.ylabel("Nº de Visitantes")
        plt.xlabel("Ações")
        plt.title("Visitantes por Ação")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def gerar_grafico_visitantes(self):
        if not self.acao_selecionada:
            Messagebox.show_warning("Aviso", "Selecione uma ação para gerar gráfico.")
            return
        status = [v["status_contrato"] for v in self.acao_selecionada.get("visitantes", [])]
        labels = list(set(status))
        counts = [status.count(l) for l in labels]
        plt.figure(figsize=(6, 6))
        plt.pie(counts, labels=labels, autopct="%1.1f%%", startangle=140)
        plt.title(f"Status de Contrato - {self.acao_selecionada['nome_acao']}")
        plt.show()


# ---------------- Run ----------------
if __name__ == "__main__":
    app = GestorDeAcoesDeRua()
    app.mainloop()
