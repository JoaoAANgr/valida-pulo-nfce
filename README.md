# Validador de Pulos de NFCe v3.0

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/maintained%3F-yes-green.svg)](https://github.com/JoaoAANgr/valida-pulo-nfce/graphs/commit-activity)

**Ferramenta profissional para validação de pulos de numeração em NFCe (Modelo 65)**

[Features](#-features-principais) • [Instalação](#-instalação) • [Como Usar](#-como-usar) • [Documentação](#-documentação)

</div>

---

## 📋 Sobre

O **Validador de Pulos de NFCe** é uma ferramenta especializada para detectar quebras e anomalias na sequência de notas fiscais eletrônicas. Processa relatórios 3.2.22 com alta performance, oferecendo análise detalhada de pulos em múltiplos contextos.

**Perfeito para:**
- Auditorias de conformidade fiscal
- Validação de integridade de dados NFCe
- Análise de sequências de numeração
- Geração de relatórios para auditoria

---

## ✨ Features Principais

✅ **Validação Múltipla** - Processar vários validadores simultaneamente  
✅ **Seleção Flexível** - Escolha lojas específicas ou todas  
✅ **Análise Contextual** - Detecta pulos em diferentes contextos (padrão, fim de dia, múltiplos dias)  
✅ **Exportação Profissional** - Excel com 5 abas analíticas + CSV opcional  
✅ **Interface Amigável** - GUI responsiva com Tkinter (sem dependências externas extras)  
✅ **Performance Otimizada** - Processa tudo em menos de 1 segundo  
✅ **Executável Standalone** - Não requer Python instalado  
✅ **Pasta de Destino Customizável** - Salve resultados onde quiser  

---

## 🚀 Início Rápido

### Opção 1: Executável (Recomendado)

Simples, rápido e sem dependências:

```bash
# Windows
Validador_Pulos_NFCe.exe
```

Pronto! A interface gráfica abrirá em segundos. ✨

### Opção 2: Código-Fonte (Desenvolvimento)

Para desenvolvedores e contribuidores:

```bash
# Clone o repositório
git clone https://github.com/JoaoAANgr/valida-pulo-nfce.git
cd valida-pulo-nfce

# Crie um ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instale dependências
pip install -r requirements.txt

# Execute a interface
python interface_validador.py
```

---

## � Como Usar

### Passo 1: Adicionar Arquivos
Clique em **"➕ Adicionar Validador"** e selecione sua lista de pulos em formato XLS/XLSX.

Pode adicionar múltiplos validadores! Também é possível adicionar vários **relatórios 3.2.22** clicando em **"➕ Adicionar Relatório 3.2.22"**.

### Passo 2: Selecionar Lojas
Marque as lojas que deseja validar ou use **"✓ Todas"** para processar todas.

### Passo 3: Escolher Pasta de Destino
Clique em **"📁 Escolher Pasta"** para definir onde os resultados serão salvos.

- **Padrão**: `./planilhas/` (mesma pasta do aplicativo)
- **Customizado**: Qualquer pasta do seu computador

### Passo 4: Configurar Exportação (Opcional)
- ✅ Marque **"Exportar também em CSV"** para salvar em CSV
- Excel é sempre gerado automaticamente

### Passo 5: Executar
Clique em **"▶ EXECUTAR VALIDAÇÃO"** e aguarde.

Os resultados serão salvos em:
```
PASTA_ESCOLHIDA/YYYY-MM-DD/
├── Validacao_Val[validador]_Rel[relatório]_HHMMSS.xlsx
└── Validacao_Val[validador]_Rel[relatório]_HHMMSS.csv (opcional)
```

---

## 📊 Saídas Geradas

### Excel (Automático)
**Nome**: `Validacao_Val[validador]_Rel[relatório]_HHMMSS.xlsx`

**5 Abas Incluídas:**

| Aba | Conteúdo |
|-----|----------|
| **Validação Detalhada** | Todos os registros analisados com detalhes completos |
| **Sumário** | Estatísticas agregadas e métricas gerais |
| **Pulos Reais** | Apenas os pulos efetivamente detectados |
| **Resumo por Contexto** | Análise agrupada por tipo de contexto |
| **Informações** | Metadados, criador, data, versão do validador |

### CSV (Opcional)
**Nome**: `Validacao_Val[validador]_Rel[relatório]_HHMMSS.csv`

Formato simplificado com colunas essenciais:
- `Loja` - Código da loja
- `Nota` - Número da nota fiscal
- `Sequência` - Valor da sequência
- `Tipo_Validação` - Tipo de pulo detectado
- `Contexto` - Contexto em que ocorreu
- `Observação` - Descrição do pulo

---

## 📁 Estrutura do Projeto

```
valida-pulo-nfce/
│
├── 📄 interface_validador.py      ← Interface gráfica (Tkinter)
├── 📄 validador_pulos_v3.py       ← Motor de validação (Pandas)
├── 📄 requirements.txt            ← Dependências Python
├── 📄 README.md                   ← Este arquivo
├── 📄 LICENSE                     ← Licença MIT
├── 📄 .gitignore                  ← Configuração Git
│
├── 📂 docs/                       ← Documentação adicional
│   ├── INICIO_RAPIDO.md
│   ├── MUDANCAS.md
│   └── ...
│
└── 📂 planilhas/                  ← Pasta de resultados (criada ao usar)
    └── YYYY-MM-DD/               ← Subpastas por data
        ├── Validacao_*.xlsx
        └── Validacao_*.csv
```

---

## ⚙️ Requisitos Técnicos

### Executável (Recomendado)
- Windows 7 ou superior
- 150 MB de espaço livre em disco
- Nenhuma instalação necessária
- Nenhuma dependência externa

### Código-Fonte (Desenvolvimento)
- Python 3.7+
- pip ou conda
- 2 dependências leves: `pandas` e `openpyxl`

**Stack Técnico:**
- 🐍 **Linguagem**: Python 3.13
- 🖥️ **GUI**: Tkinter (nativo, sem dependências)
- 📊 **Processamento**: Pandas + NumPy (vetorizado)
- 📈 **Excel**: OpenPyXL
- ⚡ **Performance**: Otimizado para análise em tempo real

---

## � Instalação de Dependências

Se você clonar este repositório e quiser executar o código-fonte:

```bash
# Instalar dependências
pip install -r requirements.txt

# requirements.txt contém:
# - pandas>=1.3.0
# - openpyxl>=3.0.0
```
---

## 🔧 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'pandas'"

**Solução:**
```bash
pip install pandas openpyxl
```

### Problema: Arquivo não encontrado

Certifique-se de que:
1. O arquivo XLS/XLSX está acessível
2. Você tem permissão de leitura
3. O arquivo não está corrompido

### Problema: Resultado não foi salvo

Verifique:
1. Se você tem permissão de escrita na pasta escolhida
2. Se há espaço livre em disco
3. Se a pasta `planilhas/` foi criada automaticamente

---

## 📚 Documentação

Para mais detalhes, consulte:

- [Início Rápido](docs/INICIO_RAPIDO.md)
- [Mudanças e Histórico](docs/MUDANCAS.md)
- [Features Completas](FEATURES_WIKI.md)
- [Resumo Técnico](RESUMO_PREPARACAO.md)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Se você encontrou um bug ou tem uma ideia de melhoria:

1. **Faça um Fork** deste repositório
2. **Crie uma Branch** para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit suas mudanças** (`git commit -m 'Add some AmazingFeature'`)
4. **Push para a Branch** (`git push origin feature/AmazingFeature`)
5. **Abra um Pull Request**

---

## 📝 Licença

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👨‍💻 Autor

**João Nogueira**

- GitHub: [@JoaoAANgr](https://github.com/JoaoAANgr)
- Projeto: [Validador de Pulos de NFCe](https://github.com/JoaoAANgr/valida-pulo-nfce)

---

## 📞 Suporte

Tem dúvidas ou encontrou um problema?

- 📋 Abra uma [Issue](https://github.com/JoaoAANgr/valida-pulo-nfce/issues)
- 📧 Entre em contato diretamente

---

## 🎯 Roadmap

- [ ] Suporte a múltiplos formatos de entrada (CSV, XML)
- [ ] Gráficos de análise visual
- [ ] Exportação em PDF
- [ ] Validação em tempo real
- [ ] Integração com APIs

---

<div align="center">

⭐️ Se este projeto foi útil, considere dar uma estrela no GitHub!

</div>
