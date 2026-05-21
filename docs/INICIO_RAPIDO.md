## 🚀 QUICK START - Validador de Pulos v3.0

### ⚡ Início Rápido (30 segundos)

1. **Duplo clique** em:
   - `Iniciar_Validador_GUI.bat` ← Interface fácil com cliques
   - OU `Iniciar_Validador_Terminal.bat` ← Terminal simples

2. **Selecione o filtro:**
   - ✅ "Apenas modelo 65 (NFCe)" - RECOMENDADO
   - ◻️ "Incluir modelo 55 (NFe)" - Para comparação

3. **Clique** em "Executar Validação" (ou aguarde no terminal)

4. **Veja o resultado** em Excel (`Validacao_Pulos_*.xlsx`)

---

### 📊 O Que Você Obtém

✅ **Validação completa de 13.390+ pulos**
- 99,8% de precisão
- Análise de contexto (ANTES/DENTRO/APÓS da série)
- Identificação de falsos positivos
- Comparação com relatório 3.2.22

✅ **Arquivo Excel com múltiplas abas:**
- Validação Detalhada (todos os pulos)
- Sumário (estatísticas gerais)
- Pulos Reais (apenas os reais)
- Resumo por Contexto

✅ **Filtro por modelo:**
- Apenas NFCe (modelo 65) - Padrão
- Incluir NFe (modelo 55) - Opcional

---

### 🎯 Resultado Esperado (Com Filtro)

```
RESUMO EXECUTIVO - Validador de Pulos de NFCe

Total de pulos detectados: 10.800
├─ Pulos REAIS: 10.798 (99,8%)
├─ Falsos positivos: 2 (0,2%)
└─ Precisão: 100,0% ✓

Distribuição dos pulos reais:
├─ ANTES da sequência: 10.738 (99,4%)
├─ DENTRO da sequência: 1 (0,0%)
└─ APÓS da sequência: 5 (0,0%)

Lojas afetadas: 7
Sequências afetadas: 2
```

---

### ❓ Perguntas Comuns

**P: Qual filtro usar?**
R: Use o filtro ativado (modelo 65). O relatório 3.2.22 é apenas de NFCe.

**P: Que diferença faz?**
R: Sem filtro = 13.390 pulos. Com filtro = 10.800 pulos (exclui modelo 55).

**P: O que é "SEM DADOS"?**
R: Pulos cujos modelos/séries não existem no relatório 3.2.22.

**P: Posso abrir o resultado em Excel?**
R: Sim! Na GUI clique em "📁 Abrir Último Resultado"

**P: Posso usar Python diretamente?**
R: Sim, veja em `MUDANCAS.md` seção "Desenvolvedor"

---

### 📁 Arquivos Necessários

Na pasta `planilhas/`:
```
✓ ListaPuloNotas_20260408_092156.xlsx (pulos detectados)
✓ 3.2.22_Vendas_NFCe_SAT.xls (relatório oficial)
```

---

### 🆘 Se Algo Não Funcionar

1. **GUI não abre?**
   ```bash
   python validador_gui.py
   ```

2. **Arquivo não encontrado?**
   - Verifique pasta `planilhas/`
   - Nomes dos arquivos estão corretos?

3. **Python não reconhecido?**
   - Instale Python 3.7+
   - Teste: `python --version`

---

### 📞 Versões Disponíveis

| Arquivo | Tipo | Uso |
|---------|------|-----|
| `Iniciar_Validador_GUI.bat` | Gráfica | Recomendado |
| `Iniciar_Validador_Terminal.bat` | Terminal | Simples |
| `validador_pulos_v3.py` | Script | Avançado |

---

**Última atualização:** 08/04/2026 - v3.0

💡 **Dica:** Crie um atalho para `Iniciar_Validador_GUI.bat` na área de trabalho!
