# 📦 Distribuição - Validador de Pulos NFCe

## Opção 1: Criar Executável (Recomendado)

Se você quer enviar um único arquivo `.exe` para seus colegas:

### Pé 1: Instalar PyInstaller
```bash
pip install pyinstaller
```

### Passo 2: Gerar o Executável
Execute o script gerador:
```bash
python gerar_executavel.py
```

Isso criará um arquivo em `distribuivel/Validador_Pulos_NFCe.exe`

### Passo 3: Distribuir
- Envie o arquivo `Validador_Pulos_NFCe.exe` para seus colegas
- Eles apenas precisam executar o arquivo
- **Nenhuma instalação adicional é necessária!**

---

## Opção 2: Instalar Python + Programa

Se você quer que seus colegas tenham acesso ao código:

### Passo 1: Instalar Python
Seus colegas deverão:
1. Baixar Python em https://www.python.org
2. Instalar com "Add Python to PATH" marcado

### Passo 2: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 3: Executar
```bash
python interface_validador.py
```

---

## 📋 Arquivos Necessários

### Para usar localmente:
- `interface_validador.py` - Interface gráfica
- `validador_pulos_v3.py` - Motor de validação
- `planilhas/` - Pasta com arquivos de trabalho
- `requirements.txt` - Dependências Python

### Para distribuir (Opção 1):
- `Validador_Pulos_NFCe.exe` - Apenas este arquivo!

---

## 🚀 Como Usar

### Fluxo de Uso:
1. **Selecionar arquivo de validador** (arquivo de pulos)
   - Clique no botão de procura
   - As lojas são reconhecidas automaticamente

2. **Adicionar relatório(s) 3.2.22**
   - Clique em "Adicionar Relatório 3.2.22"
   - Pode adicionar múltiplos relatórios

3. **Selecionar lojas**
   - Choose which stores to validate
   - Use "Todas" para selecionar todas
   - Use "Limpar" para desselecionar

4. **Executar validação**
   - Clique em "EXECUTAR VALIDAÇÃO"
   - O programa processará e gerará arquivo Excel

5. **Resultado**
   - Arquivo salvo em: `planilhas/Validacao_Pulos_NFCE_[data].xlsx`

---

## ✅ Requisitos

### Opção 1 (Executável):
- Windows 7 ou superior
- ~200 MB de espaço livre

### Opção 2 (Python):
- Python 3.7+
- ~300 MB de dependências
- Qualquer SO (Windows, Mac, Linux)

---

## 📞 Suporte

Se houver problemas:

### Erro "Nenhum arquivo selecionado"
- Certifique-se de selecionar um arquivo válido

### Erro "Nenhuma loja reconhecida"  
- Verifique se o arquivo tem as colunas: Loja., Nota, Serie, Modelo

### Erro "Nenhuma análise para exportar"
- Verifique se as lojas selecionadas existem no relatório
- Tente adicionar o relatório padrão: "3.2.22_Vendas_NFCe_SAT.xls"

---

## 📝 Versão
v3.0 - Validador de Pulos com Interface Gráfica

---

Criado em: 2026-04-09
