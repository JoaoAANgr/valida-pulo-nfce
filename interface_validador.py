#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interface Gráfica - Validador de Pulos de NFCe v3.0
Permite selecionar arquivo 3.2.22 e aplicar filtro de modelo

Criado por: João Nogueira
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import pandas as pd
import threading
import queue
from datetime import datetime
import validador_pulos_v3 as validator


class InterfaceValidador:
    def __init__(self, root):
        self.root = root
        # Título com data de hoje
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        self.root.title(f"Validador de Pulos de NFCe v3.0 - Atualizado em {data_hoje} - João Nogueira")
        self.root.geometry("900x600")  # Inicio em tamanho menor
        self.root.resizable(True, True)
        
        # Maximizar janela ao abrir
        try:
            self.root.state('zoomed')  # Windows
        except:
            self.root.attributes('-zoomed', True)  # Linux
        
        # Variáveis
        self.arquivos_pulos = []  # CHANGED: Now supports multiple break validators
        self.arquivos_relatorios = []
        self.apenas_modelo_65 = True
        self.lojas_disponiveis = []
        self.ultimo_arquivo = None
        self.checkboxes_lojas = {}
        self.lojas_selecionadas_vars = {}
        self.frame_checkboxes_lojas = None
        
        # Definir pasta de planilhas padrão (sempre relativa ao executável)
        self.pasta_planilhas = Path(__file__).parent / "planilhas"
        self.pasta_planilhas.mkdir(exist_ok=True)
        
        # Queue para comunicação entre thread e UI
        self.log_queue = queue.Queue()
        
        self.criar_interface()
        
    def criar_interface(self):
        """Cria layout da interface"""
        
        # Frame principal com PanedWindow (redimensionável)
        main_frame = ttk.PanedWindow(self.root, orient="horizontal")
        main_frame.pack(fill="both", expand=True)
        
        # ======== LADO ESQUERDO - Configurações (redimensionável) ========
        frame_left = ttk.Frame(main_frame, width=300, relief="flat", borderwidth=0)
        main_frame.add(frame_left, weight=1)  # weight=1 permite redimensionar
        
        # Canvas com scrollbar para conteúdo da esquerda
        canvas_left = tk.Canvas(frame_left, highlightthickness=0, bg="white")
        scrollbar_left = ttk.Scrollbar(frame_left, orient="vertical", command=canvas_left.yview)
        
        frame_left_content = ttk.Frame(canvas_left)
        
        def on_frame_configure(event):
            canvas_left.configure(scrollregion=canvas_left.bbox("all"))
        
        def on_canvas_configure(event):
            # Atualiza a largura do frame_left_content para preencher o canvas (sem controlar altura)
            canvas_width = event.width
            canvas_left.itemconfig("frame_left_content", width=max(canvas_width - 15, 280))
        
        frame_left_content.bind("<Configure>", on_frame_configure)
        
        canvas_id = canvas_left.create_window((0, 0), window=frame_left_content, anchor="nw", tags="frame_left_content")
        canvas_left.bind("<Configure>", on_canvas_configure)
        canvas_left.configure(yscrollcommand=scrollbar_left.set)
        
        canvas_left.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        scrollbar_left.pack(side="right", fill="y", padx=0)
        
        # Título
        ttk.Label(frame_left_content, text="CONFIGURAÇÃO", font=("Arial", 11, "bold")).pack(anchor="w", pady=(8, 5), padx=5)
        
        # Seleção de arquivos
        frame_arquivos = ttk.LabelFrame(frame_left_content, text="📁 Arquivos", padding=6)
        frame_arquivos.pack(fill="x", pady=2, padx=5)
        
        ttk.Label(frame_arquivos, text="Validadores de Quebra (múltiplos):", font=("Arial", 8, "bold")).pack(anchor="w", pady=(2, 2))
        
        # Listbox para validadores de quebra
        scrollbar_pulos = ttk.Scrollbar(frame_arquivos)
        scrollbar_pulos.pack(side="right", fill="y")
        
        self.listbox_pulos = tk.Listbox(frame_arquivos, height=3, yscrollcommand=scrollbar_pulos.set)
        scrollbar_pulos.config(command=self.listbox_pulos.yview)
        self.listbox_pulos.pack(fill="both", expand=True, pady=2)
        
        ttk.Button(frame_arquivos, text="➕ Adicionar Validador", 
                   command=self.selecionar_pulos).pack(fill="x", pady=2)
        ttk.Button(frame_arquivos, text="🗑️ Remover Selecionado", 
                   command=self.remover_validador).pack(fill="x", pady=2)
        
        ttk.Label(frame_arquivos, text="Relatórios 3.2.22 (múltiplos):", font=("Arial", 8, "bold")).pack(anchor="w", pady=(6, 2))
        
        # Listbox para relatórios
        scrollbar_relatorios = ttk.Scrollbar(frame_arquivos)
        scrollbar_relatorios.pack(side="right", fill="y")
        
        self.listbox_relatorios = tk.Listbox(frame_arquivos, height=3, yscrollcommand=scrollbar_relatorios.set)
        scrollbar_relatorios.config(command=self.listbox_relatorios.yview)
        self.listbox_relatorios.pack(fill="both", expand=True, pady=2)
        
        ttk.Button(frame_arquivos, text="➕ Adicionar Relatório 3.2.22", 
                   command=self.selecionar_relatorio).pack(fill="x", pady=2)
        ttk.Button(frame_arquivos, text="🗑️ Remover Selecionado", 
                   command=self.remover_relatorio).pack(fill="x", pady=2)
        
        # Informação de validação
        frame_info = ttk.LabelFrame(frame_left_content, text="ℹ️ Modelo de Validação", padding=6)
        frame_info.pack(fill="x", pady=2, padx=5)
        
        ttk.Label(frame_info, 
                 text="✓ Este validador trabalha apenas com\nModelo 65 (NFCe)",
                 foreground="green", font=("Arial", 7), justify="left", wraplength=280).pack(anchor="w", pady=2)
        
        # Seleção de lojas com CHECKBOXES
        frame_lojas = ttk.LabelFrame(frame_left_content, text="🎪 Lojas para Validar", padding=6)
        frame_lojas.pack(fill="x", pady=2, padx=5)
        
        ttk.Label(frame_lojas, text="Selecione as lojas:", font=("Arial", 8, "bold")).pack(anchor="w", pady=(2, 3))
        
        # Subframe para canvas + scrollbar (ficam juntos no topo com altura fixa)
        frame_canvas_container = ttk.Frame(frame_lojas, height=150)
        frame_canvas_container.pack(fill="x", expand=False, pady=(0, 3))
        frame_canvas_container.pack_propagate(False)  # Altura fixa
        
        # Canvas com scrollbar para checkboxes
        canvas_lojas = tk.Canvas(frame_canvas_container, bg="white", highlightthickness=0)
        scrollbar_lojas = ttk.Scrollbar(frame_canvas_container, orient="vertical", command=canvas_lojas.yview)
        
        self.frame_checkboxes_lojas = ttk.Frame(canvas_lojas)
        
        def on_checkboxes_configure(event):
            canvas_lojas.configure(scrollregion=canvas_lojas.bbox("all"))
        
        def on_canvas_lojas_configure(event):
            # Atualiza a largura do frame_checkboxes_lojas para preencher o canvas
            canvas_lojas.itemconfig("checkboxes_window", width=max(event.width - 15, 200))
        
        self.frame_checkboxes_lojas.bind("<Configure>", on_checkboxes_configure)
        
        checkboxes_id = canvas_lojas.create_window((0, 0), window=self.frame_checkboxes_lojas, anchor="nw", tags="checkboxes_window")
        canvas_lojas.bind("<Configure>", on_canvas_lojas_configure)
        canvas_lojas.configure(yscrollcommand=scrollbar_lojas.set)
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas_lojas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas_lojas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Canvas e scrollbar lado a lado no container
        canvas_lojas.pack(side="left", fill="both", expand=True)
        scrollbar_lojas.pack(side="right", fill="y")
        
        # Variável para armazenar estado dos checkboxes
        self.checkboxes_lojas = {}
        self.lojas_selecionadas_vars = {}
        
        # Subframe para botoes logo abaixo do canvas
        frame_lojas_botoes_container = ttk.Frame(frame_lojas)
        frame_lojas_botoes_container.pack(fill="x", expand=False, pady=(0, 0))
        
        # Botões com grid - não são comprimidos
        ttk.Button(frame_lojas_botoes_container, text="✓ Todas", command=self.selecionar_todas_lojas).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(frame_lojas_botoes_container, text="✗ Limpar", command=self.desselecionar_todas_lojas).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        frame_lojas_botoes_container.columnconfigure(0, weight=1)
        frame_lojas_botoes_container.columnconfigure(1, weight=1)
        
        # Seleção de pasta de saída
        frame_pasta = ttk.LabelFrame(frame_left_content, text="💾 Pasta de Saída", padding=6)
        frame_pasta.pack(fill="x", pady=2, padx=5)
        
        self.label_pasta_saida = ttk.Label(frame_pasta, text="Padrão: ./planilhas/", 
                                           foreground="blue", font=("Arial", 8), wraplength=280, justify="left")
        self.label_pasta_saida.pack(anchor="w", pady=(2, 5))
        
        ttk.Button(frame_pasta, text="📁 Escolher Pasta", 
                   command=self.escolher_pasta_saida).pack(fill="x", pady=2)
        
        # Botão de execução
        self.btn_executar = ttk.Button(frame_left_content, text="▶ EXECUTAR VALIDAÇÃO", 
                                       command=self.executar_validacao)
        self.btn_executar.pack(fill="x", pady=5, padx=5)
        
        # Status
        frame_status = ttk.LabelFrame(frame_left_content, text="📊 Status", padding=6)
        frame_status.pack(fill="x", pady=2, padx=5)
        
        self.label_status = ttk.Label(frame_status, text="Pronto para executar", 
                                     foreground="blue", font=("Arial", 8))
        self.label_status.pack(fill="x", pady=2)
        
        self.progressbar = ttk.Progressbar(frame_status, mode='indeterminate')
        self.progressbar.pack(fill="x", pady=(2, 0))
        
        # Spacer
        ttk.Frame(frame_left_content).pack(fill="both", expand=True)
        
        # ======== LADO DIREITO - Log (redimensionável) ========
        frame_right = ttk.Frame(main_frame, relief="flat", borderwidth=0)
        main_frame.add(frame_right, weight=2)  # weight=2 dá mais peso ao painel direito
        
        frame_log = ttk.LabelFrame(frame_right, text="📝 Execução Detalhada", padding=0, relief="flat", borderwidth=0)
        frame_log.pack(fill="both", expand=True, padx=0, pady=0, side="left")
        
        self.text_log = tk.Text(frame_log, state="disabled", 
                               font=("Courier", 8), wrap="word", bg="white")
        scrollbar_log = ttk.Scrollbar(frame_log, orient="vertical", command=self.text_log.yview)
        self.text_log.config(yscrollcommand=scrollbar_log.set)
        
        self.text_log.pack(side="left", fill="both", expand=True)
        scrollbar_log.pack(side="right", fill="y")
    
    def selecionar_pulos(self):
        """Seleciona arquivo de validador e adiciona à lista"""
        arquivo = filedialog.askopenfilename(
            title="Selecionar Validador de Quebra",
            filetypes=[("Excel", "*.xlsx *.xls"), ("Todos", "*.*")],
            initialdir="C:/Users/João/Desktop/Valida pulo/planilhas"
        )
        if arquivo:
            caminho = Path(arquivo)
            if caminho not in self.arquivos_pulos:
                self.arquivos_pulos.append(caminho)
                self.atualizar_listbox_pulos()
                self.log(f"✓ Validador adicionado: {caminho.name}")
                self.log(f"  Reconhecendo lojas...\n")
                self.exibir_resumo_lojas()
            else:
                messagebox.showinfo("Info", f"Este validador já foi adicionado!")
    
    def selecionar_relatorio(self):
        """Seleciona arquivo de relatório e adiciona à lista"""
        arquivo = filedialog.askopenfilename(
            title="Selecionar Relatório 3.2.22",
            filetypes=[("Excel", "*.xls *.xlsx"), ("Todos", "*.*")],
            initialdir="C:/Users/João/Desktop/Valida pulo/planilhas"
        )
        if arquivo:
            caminho = Path(arquivo)
            if caminho not in self.arquivos_relatorios:
                self.arquivos_relatorios.append(caminho)
                self.atualizar_listbox_relatorios()
                self.log(f"✓ Relatório adicionado: {caminho.name}")
            else:
                messagebox.showinfo("Info", f"Este relatório já foi adicionado!")
    
    def remover_validador(self):
        """Remove validador selecionado da lista"""
        selecionados = self.listbox_pulos.curselection()
        if not selecionados:
            messagebox.showwarning("Aviso", "Selecione um validador para remover!")
            return
        
        idx = selecionados[0]
        arquivo_removido = self.arquivos_pulos.pop(idx)
        self.atualizar_listbox_pulos()
        self.log(f"✗ Validador removido: {arquivo_removido.name}")
        self.exibir_resumo_lojas()
    
    def remover_relatorio(self):
        """Remove relatório selecionado da lista"""
        selecionados = self.listbox_relatorios.curselection()
        if not selecionados:
            messagebox.showwarning("Aviso", "Selecione um relatório para remover!")
            return
        
        idx = selecionados[0]
        arquivo_removido = self.arquivos_relatorios.pop(idx)
        self.atualizar_listbox_relatorios()
        self.log(f"✗ Relatório removido: {arquivo_removido.name}")
    
    def atualizar_listbox_pulos(self):
        """Atualiza a listbox de validadores de quebra"""
        self.listbox_pulos.delete(0, tk.END)
        for pulo in self.arquivos_pulos:
            self.listbox_pulos.insert(tk.END, pulo.name)
    
    def atualizar_listbox_relatorios(self):
        """Atualiza a listbox de relatórios"""
        self.listbox_relatorios.delete(0, tk.END)
        for rel in self.arquivos_relatorios:
            self.listbox_relatorios.insert(tk.END, rel.name)
    
    def exibir_resumo_lojas(self):
        """Carrega e exibe resumo das lojas nos arquivos de validadores com CHECKBOXES"""
        try:
            if not self.arquivos_pulos:
                self.log("⚠ Nenhum validador selecionado")
                # Limpar checkboxes
                for widget in self.frame_checkboxes_lojas.winfo_children():
                    widget.destroy()
                self.checkboxes_lojas.clear()
                self.lojas_selecionadas_vars.clear()
                return
            
            # Carregar todos os validadores para extrair lojas
            validadores_dict = validator.carregar_todos_validadores(self.arquivos_pulos)
            
            # Consolidar lojas de todos os validadores
            todas_as_lojas = set()
            lojas_stats = {}
            
            for val_nome, df_val in validadores_dict.items():
                if 'Loja.' in df_val.columns:
                    lojas = df_val['Loja.'].unique().astype(str)
                    for loja in lojas:
                        todas_as_lojas.add(loja)
                        lojas_stats[loja] = lojas_stats.get(loja, 0) + len(df_val[df_val['Loja.'] == loja])
            
            self.lojas_disponiveis = sorted(list(todas_as_lojas))
            
            # Limpar checkboxes antigos
            for widget in self.frame_checkboxes_lojas.winfo_children():
                widget.destroy()
            self.checkboxes_lojas.clear()
            self.lojas_selecionadas_vars.clear()
            
            # Criar checkboxes para cada loja
            for loja in self.lojas_disponiveis:
                count = lojas_stats.get(loja, 0)
                
                # Criar variável de controle
                var = tk.BooleanVar(value=True)  # Começam selecionadas por padrão
                self.lojas_selecionadas_vars[loja] = var
                
                # Criar checkbox
                checkbox = ttk.Checkbutton(
                    self.frame_checkboxes_lojas,
                    text=f"Loja {loja} ({count:,} pulos)",
                    variable=var,
                    onvalue=True,
                    offvalue=False
                )
                checkbox.pack(anchor="w", pady=2, padx=10)
                self.checkboxes_lojas[loja] = checkbox
            
            # Log resumido
            resumo = f"\n{'='*70}\n"
            resumo += f"📊 RESUMO DOS VALIDADORES\n"
            resumo += f"{'='*70}\n\n"
            resumo += f"Total de validadores: {len(validadores_dict)}\n"
            resumo += f"Total de lojas: {len(self.lojas_disponiveis)}\n"
            
            total_registros = sum(len(df) for df in validadores_dict.values())
            resumo += f"Total de pulos: {total_registros:,}\n\n"
            
            resumo += f"Validadores:\n"
            for val_nome, df_val in validadores_dict.items():
                resumo += f"  • {val_nome}: {len(df_val):,} pulos\n"
            
            resumo += f"\n{'='*70}\n"
            
            self.log(resumo)
            
        except Exception as e:
            self.log(f"\n⚠ Aviso ao carregar validadores: {str(e)}\n")
            # Limpar checkboxes em caso de erro
            for widget in self.frame_checkboxes_lojas.winfo_children():
                widget.destroy()
    
    def selecionar_todas_lojas(self):
        """Seleciona todos os checkboxes de lojas"""
        for var in self.lojas_selecionadas_vars.values():
            var.set(True)
    
    def desselecionar_todas_lojas(self):
        """Desseleciona todos os checkboxes de lojas"""
        for var in self.lojas_selecionadas_vars.values():
            var.set(False)
    
    def escolher_pasta_saida(self):
        """Abre diálogo para escolher pasta de saída"""
        pasta = filedialog.askdirectory(title="Selecione a pasta para salvar os resultados")
        if pasta:
            self.pasta_planilhas = Path(pasta)
            # Atualizar label com a pasta selecionada
            self.label_pasta_saida.config(text=f"Destino: {pasta}", foreground="green")
        else:
            # Se cancelar, volta ao padrão
            self.pasta_planilhas = Path(__file__).parent / "planilhas"
            self.label_pasta_saida.config(text="Padrão: ./planilhas/", foreground="blue")
    
    def executar_validacao(self):
        """Valida os inputs e executa validação em thread"""
        if not self.arquivos_pulos or not self.arquivos_relatorios:
            messagebox.showwarning("Aviso", "Selecione os validadores e relatórios!")
            return
        
        # Obter lojas selecionadas dos checkboxes
        lojas_selecionadas = [loja for loja, var in self.lojas_selecionadas_vars.items() if var.get()]
        
        if not lojas_selecionadas:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma loja!")
            return
        
        for validador in self.arquivos_pulos:
            if not validador.exists():
                messagebox.showerror("Erro", f"Arquivo não encontrado: {validador}")
                return
        
        for rel in self.arquivos_relatorios:
            if not rel.exists():
                messagebox.showerror("Erro", f"Arquivo não encontrado: {rel}")
                return
        
        self.limpar_log()
        self.progressbar.start()
        self.btn_executar.config(state="disabled")
        thread = threading.Thread(target=self._executar_validacao_thread, daemon=True)
        thread.start()
        # Começar a processar queue periodicamente
        self._processar_queue_periodicamente()
    
    def _executar_validacao_thread(self):
        """Executa validação cruzada OTIMIZADA em thread separada"""
        try:
            # Pegar lojas selecionadas via checkboxes
            lojas_selecionadas = [loja for loja, var in self.lojas_selecionadas_vars.items() if var.get()]
            
            # Exibir resumo inicial
            self.log_queue.put(("log", "Iniciando validação cruzada OTIMIZADA...\n"))
            self.log_queue.put(("log", f"📊 CONFIGURAÇÃO:"))
            self.log_queue.put(("log", f"  • {len(self.arquivos_pulos)} validador(es) de quebra"))
            self.log_queue.put(("log", f"  • {len(self.arquivos_relatorios)} relatório(s) 3.2.22"))
            self.log_queue.put(("log", f"  • Total de validações: {len(self.arquivos_pulos) * len(self.arquivos_relatorios)}"))
            self.log_queue.put(("log", f"  • Lojas selecionadas: {len(lojas_selecionadas)}\n"))
            self.log_queue.put(("log", "=" * 80 + "\n"))
            
            # [1] CARREGA TODOS OS VALIDADORES EM MEMÓRIA
            self.log_queue.put(("log", "[1/4] Carregando TODOS os validadores em memória...\n"))
            validadores = validator.carregar_todos_validadores(self.arquivos_pulos)
            
            for nome, df in validadores.items():
                self.log_queue.put(("log", f"      ✓ {nome}: {len(df):,} registros"))
            self.log_queue.put(("log", "\n"))
            
            # [2] EXTRAI IDs DE LOJA DO VALIDADOR
            self.log_queue.put(("log", "[2/4] Extraindo IDs de loja do validador...\n"))
            lojas_do_validador = validator.extrair_lojas_do_validador(validadores)
            self.log_queue.put(("log", f"      ✓ {len(lojas_do_validador)} loja(s) encontrada(s)\n"))
            
            # [3] CARREGA TODOS OS RELATÓRIOS EM MEMÓRIA (com filtro de lojas)
            self.log_queue.put(("log", "[3/5] Carregando TODOS os relatórios em memória...\n"))
            relatorios, contextos = validator.carregar_todos_relatorios_otimizado(self.arquivos_relatorios, lojas_esperadas=lojas_do_validador)
            
            for nome, df in relatorios.items():
                self.log_queue.put(("log", f"      ✓ {nome}: {len(df):,} registros"))
            self.log_queue.put(("log", "\n"))
            
            # [4] VALIDAÇÃO CRUZADA OTIMIZADA
            self.log_queue.put(("log", "[4/5] Executando validação cruzada otimizada...\n"))
            resultados = validator.validar_cruzado_otimizado(
                validadores, relatorios, contextos,
                apenas_modelo_65=True,
                lojas_filtro=lojas_selecionadas if lojas_selecionadas else None
            )
            
            if not resultados:
                self.log_queue.put(("log", "\n⚠ AVISO: Nenhuma validação foi concluída"))
                self.log_queue.put(("status", "⚠ Sem dados", "orange"))
                self.log_queue.put(("stop", None))
                return
            
            # [5] EXPORTAR TODOS OS RESULTADOS
            self.log_queue.put(("log", "[5/5] Exportando resultados...\n"))
            
            todos_os_resultados = []
            for idx, resultado in enumerate(resultados, 1):
                try:
                    # Gerar sumário
                    summary = validator.gerar_relatorio_summary(
                        resultado['df_analise'], 
                        resultado['stats_modelos']
                    )
                    
                    # Exportar resultado individual
                    arquivo_saida = validator.exportar_resultado(
                        self.pasta_planilhas,
                        resultado['df_analise'],
                        summary,
                        apenas_modelo_65=True,
                        nome_validador=resultado['validador_nome'],
                        nome_relatorio=resultado['relatorio_nome']
                    )
                    
                    if arquivo_saida:
                        self.log_queue.put(("log", f"      ✓ [{idx}] {arquivo_saida.name}"))
                        todos_os_resultados.append({
                            'validador': resultado['validador_nome'],
                            'relatorio': resultado['relatorio_nome'],
                            'pulos_detectados': resultado['total_pulos'],
                            'pulos_reais': resultado['pulos_reais'],
                            'arquivo_saida': arquivo_saida.name,
                            'df_analise': resultado['df_analise'],
                            'summary': summary
                        })
                
                except Exception as e:
                    self.log_queue.put(("log", f"      ✗ [{idx}] ERRO: {str(e)}"))
                    import traceback
                    self.log_queue.put(("log", f"      Traceback: {traceback.format_exc()}"))
                    continue
            
            self.log_queue.put(("log", "\n"))
            
            # SUMÁRIO FINAL COM DETALHES
            self.log_queue.put(("log", "=" * 80))
            self.log_queue.put(("log", "📋 SUMÁRIO DE TODAS AS VALIDAÇÕES".center(80)))
            self.log_queue.put(("log", "=" * 80 + "\n"))
            
            if todos_os_resultados:
                self.log_queue.put(("log", f"✅ Total de {len(todos_os_resultados)} validação(ões) concluída(s)\n"))
                
                # Exibir sumário detalhado de cada validação
                for idx, resultado in enumerate(todos_os_resultados, 1):
                    self.log_queue.put(("log", f"\n{'─'*80}"))
                    self.log_queue.put(("log", f"[{idx}] {resultado['validador']} ✕ {resultado['relatorio']}"))
                    self.log_queue.put(("log", f"{'─'*80}"))
                    
                    # Exibir texto resumido
                    texto_sumario = validator.gerar_texto_sumario(resultado['summary'])
                    self.log_queue.put(("log", texto_sumario))
                    
                    # Exibir gráfico ASCII se houver pulos reais
                    grafico = validator.gerar_grafico_ascii(resultado['df_analise'])
                    if grafico:
                        self.log_queue.put(("log", grafico))
                    
                    self.log_queue.put(("log", f"📁 Arquivo exportado: {resultado['arquivo_saida']}\n"))
            
            # Rodapé
            data_execucao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.log_queue.put(("log", "=" * 80))
            self.log_queue.put(("log", "✅ VALIDAÇÃO CRUZADA CONCLUÍDA COM SUCESSO!"))
            self.log_queue.put(("log", f"Data: {data_execucao}"))
            self.log_queue.put(("log", f"Arquivos salvos em: {self.pasta_planilhas}"))
            self.log_queue.put(("log", "=" * 80))
            self.log_queue.put(("status", "✓ Concluída!", "green"))
            self.log_queue.put(("stop", None))
            self.log_queue.put(("status", "✓ Concluída!", "green"))
            self.log_queue.put(("stop", None))
        
        except Exception as e:
            self.log_queue.put(("log", f"\n❌ ERRO: {str(e)}"))
            self.log_queue.put(("status", "✗ Erro", "red"))
            self.log_queue.put(("error", str(e)))
            self.log_queue.put(("stop", None))
    
    def _processar_queue_periodicamente(self):
        """Processa mensagens da queue periodicamente"""
        try:
            # Processar todas as mensagens na queue
            while True:
                try:
                    msg_tuple = self.log_queue.get_nowait()
                    tipo, dados = msg_tuple[0], msg_tuple[1]
                    
                    if tipo == "log":
                        self.log(dados)
                    elif tipo == "status":
                        cor = msg_tuple[2] if len(msg_tuple) > 2 else "blue"
                        self.label_status.config(text=dados, foreground=cor)
                    elif tipo == "stop":
                        self.progressbar.stop()
                        self.btn_executar.config(state="normal")
                        return
                    elif tipo == "error":
                        messagebox.showerror("Erro", f"Erro durante validação:\n\n{dados}")
                except queue.Empty:
                    # Nenhuma mensagem disponível, continuar tentando
                    break
        except Exception as e:
            pass
        
        # Agendar processamento novamente
        self.root.after(100, self._processar_queue_periodicamente)
    
    def _processar_queue(self):
        """Processa mensagens da queue - compatibilidade"""
        self._processar_queue_periodicamente()
    
    
    def log(self, mensagem):
        """Adiciona mensagem ao log"""
        self.text_log.config(state="normal")
        self.text_log.insert("end", f"{mensagem}\n")
        self.text_log.see("end")
        self.text_log.config(state="disabled")
        self.root.update()
    
    def limpar_log(self):
        """Limpa o log"""
        self.text_log.config(state="normal")
        self.text_log.delete("1.0", "end")
        self.text_log.config(state="disabled")


def main():
    root = tk.Tk()
    app = InterfaceValidador(root)
    root.mainloop()


if __name__ == "__main__":
    main()
