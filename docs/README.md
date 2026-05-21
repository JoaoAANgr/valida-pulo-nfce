# Validador de Pulos de Numeração de NFCe - v3.0

Aplicação em Python que valida pulos de numeração de Notas Fiscais de Consumidor Eletrônico (NFCe) no ERP, cruzando dados do relatório oficial 3.2.22 com o arquivo de possíveis pulos detectados.

## ✨ Novidades v3.0

🎯 **Filtro por Modelo (NFCe vs NFe)**
- Checkbox para validar APENAS modelo 65 (NFCe) 
- Exclui modelo 55 (NFe) que não existe no relatório 3.2.22
- Duas interfaces: GUI (gráfica) e Terminal (simples)
- Arquivo de saída com sufixo `_NFCE` quando filtro ativo

## Problema Resolvido

O aplicativo anterior conseguia detectar quebras de sequência, mas não conseguia precisar quais eram realmente pulos válidos. **NOVO:** Relatório 3.2.22 contém apenas NFCe (modelo 65), mas o arquivo de pulos listava ambos os modelos (55 e 65). Pulos de modelo 55 apareciam como "SEM DADOS", distorcendo os resultados.

**Solução:** Permitir filtrar apenas modelo 65 (NFCe).

Esta solução cruza:
- **Arquivo de Pulos**: Lista de numerações detectadas como potenciais gaps (modelos 55 e 65)
- **Relatório 3.2.22**: Dados oficiais de notas NFCe confirmadas e inutilizadas (apenas modelo 65)

Resultado: Identificação precisa de pulos reais vs falsos positivos com análise de contexto.

## Estrutura de Arquivos

```
Valida pulo/
├── planilhas/
│   ├── ListaPuloNotas_20260408_092156.xlsx    (entrada: pulos detectados)
│   ├── 3.2.22_Vendas_NFCe_SAT.xls             (entrada: relatório oficial)
│   └── Validacao_Pulos_[timestamp].xlsx       (saída: resultado detalhado)
├── validador_pulos.py                          (módulo principal)
├── run_validator.py                            (script executável)
└── README.md                                   (este arquivo)
```

## Como Usar

### 🎨 Opção 1: Interface Gráfica (Recomendado) ⭐

Duplo clique em **`Iniciar_Validador_GUI.bat`**

Aparecerá uma janela com:
- ✅ Checkbox: "Validar APENAS modelo 65 (NFCe)" (padrão recomendado)
- ▶ Botão "Executar Validação"
- 📁 Botão "Abrir Último Resultado" (abre Excel automaticamente)
- 📊 Visualização do progresso em tempo real

### 💻 Opção 2: Terminal Simples

Duplo clique em **`Iniciar_Validador_Terminal.bat`**

O script perguntará:
```
[?] Validação APENAS sobre modelo 65 (NFCe)?
[S] Sim - Validar apenas NFCe (modelo 65)
[N] Não - Incluir modelo 55 (NFe) também

Escolha [S/N]: S
```

Pressione `S` (recomendado) ou `N` e aguarde a conclusão.

### 🐍 Opção 3: Python direto

```bash
cd "C:\Users\João\Desktop\Valida pulo"
python validador_pulos_v3.py
```

Ou para usar em scripts:

```python
from validador_pulos_v3 import *

arquivo_pulos = Path("planilhas/ListaPuloNotas_20260408_092156.xlsx")
df_pulos = carregar_arquivo_pulos(arquivo_pulos)

arquivos_relatorio = localizar_arquivos_relatorio(Path("planilhas"))
df_relatorio, contexto_numeracao = carregar_relatorio_322(arquivos_relatorio)

notas_existentes = extrair_notas_existentes(df_relatorio)

# COM FILTRO (apenas modelo 65)
analise, stats = validar_pulos(
    df_pulos, df_relatorio, contexto_numeracao, notas_existentes,
    apenas_modelo_65=True  # ← Ativa filtro
)
```

## 📊 Comparação de Resultados

### COM FILTRO ✅ (Apenas Modelo 65 - NFCe) - RECOMENDADO

```
Total analisados:       10.800 pulos (modelo 65 apenas)
Pulos REAIS:            10.798
Falsos positivos:       2
Precisão:               99,8%

Distribuição:
  • ANTES da sequência:  10.738 pulos (99,4%)
  • DENTRO da sequência: 1 pulos (0,0%)
  • APÓS da sequência:   5 pulos (0,0%)
  • SEM DADOS:           0 pulos (0,0%) ← Excluído modelo 55

Lojas afetadas:         7
Sequências afetadas:    2
```

### SEM FILTRO ⚠️ (Modelo 65 + 55)

```
Total analisados:       13.390 pulos (todos os modelos)
Pulos REAIS:            13.388
Falsos positivos:       2
Precisão:               99,9%

Distribuição:
  • ANTES da sequência:  10.738 pulos (80,2%)
  • SEM DADOS:           2.589 pulos (19,3%) ← Modelo 55, não existe em 3.2.22
  • DENTRO da sequência: 1 pulos (0,0%)
  • APÓS da sequência:   1 pulos (0,0%)

Lojas afetadas:         9
Sequências afetadas:    2
```

**⚡ Diferença:** Os 2.590 pulos de modelo 55 (NFe) aparecem como "SEM DADOS" pois não existem no relatório 3.2.22 (que contém apenas NFCe).

**📌 Recomendação:** Use o **filtro ativado (modelo 65 apenas)** para uma análise mais precisa, já que o relatório 3.2.22 é específico para NFCe.


O arquivo gerado (`Validacao_Pulos_[timestamp].xlsx`) contém:

### Aba 1: Validação Detalhada
Todos os 13.390 pulos analisados com colunas:
- **Loja**: Código da unidade (H128, H746, etc)
- **Nota**: Número da NFCe
- **Série**: Série da NFCe (1 ou 3)
- **Tipo_Validacao**: `[PULO REAL]` ou `[FALSO POSITIVO]`
- **Status_Relatorio**: CONFIRMADA | INUTILIZADA | NAO ENCONTRADA
- **Contexto**: Posição relativa na série:
  - `ANTES da serie (min=xxxxx)` - Número anterior ao primeiro registrado
  - `DENTRO da serie` - Número entre min e max registrados
  - `APOS a serie (max=xxxxx)` - Número posterior ao último registrado
  - `Sem dados da serie no relatorio` - Série não encontrada no relatório

### Aba 2: Sumário
Estatísticas globais:
- Total de pulos detectados
- Pulos reais vs falsos positivos
- Percentual de precisão do detector anterior

### Aba 3: Resumo por Contexto
Distribuição dos pulos reais:
- 10.738 pulos **ANTES** das séries (numerações antigas)
- 2.589 pulos de **lojas/séries sem dados** no relatório
- 52 pulos **DENTRO** das séries (gaps reais)
- 5 pulos **APÓS** as séries

## Interpretação dos Resultados

### PULO REAL
- **Status = NAO ENCONTRADA**: A numeração realmente não existe
- **Contexto = ANTES da serie**: Numeração mais antiga que o primeiro registro da série
- **Contexto = DENTRO da serie**: Há um gap real entre notas confirmadas
- **Contexto = APOS da serie**: Numeração posterior aos registros (pode ser número futuro)

### FALSO POSITIVO
- **Status = CONFIRMADA ou INUTILIZADA**: Nota existe no relatório oficial
- Deve ser ignorada (foi mal detectada como pulo)

## Exemplo de Saída

```
Total de pulos detectados: 13.390
Pulos REAIS: 13.388
FALSOS POSITIVOS: 2
Precisão do detector anterior: 100.0%

Distribuição de pulos reais por contexto:
  - ANTES da serie (min=50253): 10.738 pulos
  - Sem dados da serie no relatorio: 2.589 pulos
  - DENTRO da serie (min=16860, max=16976): 52 pulos
  - APOS a serie (max=14757): 5 pulos
  ...
```

## Dependências

- Python 3.8+
- pandas
- openpyxl
- xlrd

### Instalar dependências:

```bash
pip install pandas openpyxl xlrd
```

## Próximos Passos

Com os resultados, você pode:

1. **Analisar falsos positivos**: Verificar por que H128 (26228) e H702 (71385) foram detectadas como pulos
2. **Investigar gaps reais**: Focar nos 52 pulos DENTRO das séries, que indicam quebras legítimas
3. **Validar numerações antigas**: Os 10.738 pulos ANTES das séries provavelmente referem-se a notas antigas não migrass no ERP
4. **Atualizar critérios**: Use os falsos positivos para refinar o algoritmo anterior de detecção

## Contato / Dúvidas

Este validador foi criado para proporcionar precisão máxima na identificação de gaps de numeração.
Para melhorias ou ajustes, revise a lógica do método `validar_pulos()` em `validador_pulos.py`.
