# Validador de Pulos de NFCe v3.0 - Features

## 🎯 O Que É
Ferramenta para validação de pulos de numeração em NFCe (Modelo 65). Detecta quebras e anomalias na sequência de notas fiscais.

## ✨ Features Principais
- ✓ Validação de múltiplos validadores simultaneamente
- ✓ Seleção flexível de lojas
- ✓ Suporte a vários relatórios 3.2.22
- ✓ **Análise por contexto** (padrão, fim de dia, múltiplos dias, etc)
- ✓ **Escolha pasta de destino** para salvar resultados
- ✓ **Exportação em Excel** (automático, 5 abas)
- ✓ Gráfico ASCII de pulos por loja
- ✓ Performance otimizada (<1 segundo)
- ✓ Interface responsiva (Tkinter)

## 📊 Saída Gerada
**Excel (.xlsx)** com 5 abas:
1. Validação Detalhada (todos os registros)
2. Sumário (estatísticas agregadas)
3. Pulos Reais (apenas os pulos detectados)
4. Resumo por Contexto (análise por tipo)
5. Informações (metadados e créditos)

## 🚀 Como Usar
1. Clique 2x em `Validador_Pulos_NFCe.exe`
2. Adicione validador (XLS/XLSX) e relatório 3.2.22
3. Selecione lojas
4. *(Novo)* Clique "📁 Escolher Pasta" para definir destino
5. Clique "▶ EXECUTAR VALIDAÇÃO"
7. Resultado salvo em `PASTA_ESCOLHIDA/YYYY-MM-DD/`

## ⚙️ Requisitos
- Windows 7 ou superior
- 150 MB de espaço em disco
- Sem instalação (executável standalone)
- Sem Python necessário

## 💾 Saída Padrão
```
PASTA_ESCOLHIDA/
└── YYYY-MM-DD/
    └── Validacao_Val[...].xlsx
```

## 📈 Stack Técnico
- **Linguagem**: Python 3.13
- **GUI**: Tkinter (nativo)
- **Processamento**: Pandas + NumPy (vetorizado)
- **Excel**: OpenPyXL
- **Performance**: <1 segundo para 132 registros

## 👤 Desenvolvedor
João Nogueira | v3.0 | 15/04/2026
