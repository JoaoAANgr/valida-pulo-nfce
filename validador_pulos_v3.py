"""
Validador de Pulos de Numeração de NFCe - VERSAO 3.0 (SIMPLIFICADA)
Cruza dados do relatório 3.2.22 com a lista de pulos detectados
Fornece análise detalhada de pulos reais com contexto de numeração
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import warnings
import re

warnings.filterwarnings('ignore')


def carregar_todos_validadores(arquivos_pulos: List[Path]) -> Dict[str, pd.DataFrame]:
    """Carrega TODOS os validadores uma única vez em memória
    
    Args:
        arquivos_pulos: Lista de caminhos para validadores
    
    Returns:
        Dict com {nome_arquivo: DataFrame}
    """
    print("[*] Carregando todos os validadores em memória...")
    validadores = {}
    
    for idx, arquivo_path in enumerate(arquivos_pulos, 1):
        try:
            print(f"    [{idx}/{len(arquivos_pulos)}] {arquivo_path.name}...")
            df = pd.read_excel(arquivo_path)
            validadores[arquivo_path.stem] = df
            print(f"            ✓ {len(df):,} registros")
        except Exception as e:
            print(f"            ✗ ERRO: {str(e)}")
    
    if not validadores:
        raise Exception("Nenhum validador foi carregado com sucesso")
    
    total_registros = sum(len(df) for df in validadores.values())
    print(f"    OK - {len(validadores)} validador(es), {total_registros:,} registros totais\n")
    return validadores


def extrair_lojas_do_validador(validadores: Dict[str, pd.DataFrame]) -> set:
    """Extrai todos os IDs de loja únicos dos validadores
    
    Args:
        validadores: Dict com DataFrames dos validadores
    
    Returns:
        Set com todos os IDs de loja encontrados
    """
    lojas = set()
    for val_nome, df_val in validadores.items():
        # Procura coluna de loja (pode ser 'Loja.' ou 'Loja')
        loja_col = 'Loja.' if 'Loja.' in df_val.columns else 'Loja'
        if loja_col in df_val.columns:
            lojas_uniques = df_val[loja_col].dropna().unique()
            lojas.update(str(loja).strip() for loja in lojas_uniques)
    
    print(f"\n[*] IDs de loja extraídos do validador:")
    print(f"    Lojas encontradas: {sorted(lojas)}")
    print(f"    Total: {len(lojas)} loja(s)\n")
    
    return lojas


def carregar_todos_relatorios_otimizado(arquivos_relatorio: List[Path], lojas_esperadas: set = None) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Dict]]:
    """Carrega TODOS os relatórios uma única vez em memória com contexto
    
    Args:
        arquivos_relatorio: Lista de caminhos para relatórios
        lojas_esperadas: Set com IDs de loja do validador (se None, tenta detectar)
    
    Returns:
        Tuple com (Dict de DataFrames, Dict de contextos)
    """
    print("[*] Carregando todos os relatórios em memória...")
    if lojas_esperadas:
        print(f"    [FILTRO] Usando lojas do validador: {sorted(lojas_esperadas)}\n")
    
    relatorios = {}
    contextos = {}
    
    for idx, arquivo_path in enumerate(arquivos_relatorio, 1):
        try:
            print(f"    [{idx}/{len(arquivos_relatorio)}] {arquivo_path.name}...")
            
            # Ler sem header para processar a estrutura complexa
            df_raw = pd.read_excel(arquivo_path, sheet_name=0, header=None)
            
            df_limpo = []
            loja_atual = None
            contexto_numeracao = {}
            
            # Processar linha por linha mantendo contexto de loja
            for data_idx, row in df_raw.iterrows():
                # Detectar nova loja
                if pd.notna(row[0]) and isinstance(row[0], str) and " - " in str(row[0]):
                    tentativa_loja = str(row[0]).split(" -")[0].strip()
                    
                    # Se temos lojas esperadas, procura por elas
                    if lojas_esperadas:
                        if tentativa_loja in lojas_esperadas:
                            loja_atual = tentativa_loja
                    else:
                        # Fallback: padrão genérico (1-4 letras + 1-4 dígitos)
                        if re.match(r'^[A-Z]{1,4}\d{1,4}$', tentativa_loja):
                            loja_atual = tentativa_loja
                
                # Se tem NF (coluna 2) e loja, extrai dados
                if pd.notna(row[2]) and loja_atual:
                    try:
                        nf = int(pd.to_numeric(row[2], errors='coerce'))
                        serie = int(pd.to_numeric(row[3], errors='coerce'))
                        status = str(row[11]).strip() if pd.notna(row[11]) else "DESCONHECIDO"
                        
                        df_limpo.append({
                            'Loja': loja_atual,
                            'NF': nf,
                            'Sequência': serie,
                            'Status': status
                        })
                        
                        # Rastrear min/max de numeração por loja e série
                        if loja_atual not in contexto_numeracao:
                            contexto_numeracao[loja_atual] = {}
                        if serie not in contexto_numeracao[loja_atual]:
                            contexto_numeracao[loja_atual][serie] = {'min': nf, 'max': nf}
                        else:
                            contexto_numeracao[loja_atual][serie]['min'] = min(contexto_numeracao[loja_atual][serie]['min'], nf)
                            contexto_numeracao[loja_atual][serie]['max'] = max(contexto_numeracao[loja_atual][serie]['max'], nf)
                    
                    except (ValueError, TypeError):
                        continue
            
            if df_limpo:
                df_temp = pd.DataFrame(df_limpo)
                relatorios[arquivo_path.stem] = df_temp
                contextos[arquivo_path.stem] = contexto_numeracao
                print(f"            ✓ {len(df_limpo):,} registros")
            else:
                print(f"            ✓ 0 registros (nenhum dado válido)")
        
        except Exception as e:
            print(f"            ✗ ERRO ao carregar: {str(e)}")
    
    if not relatorios:
        raise Exception("Nenhum relatório foi carregado com sucesso")
    
    total_registros = sum(len(df) for df in relatorios.values())
    print(f"    OK - {len(relatorios)} relatório(s), {total_registros:,} registros totais\n")
    return relatorios, contextos


def validar_cruzado_otimizado(validadores: Dict[str, pd.DataFrame], 
                              relatorios: Dict[str, pd.DataFrame],
                              contextos: Dict[str, Dict],
                              apenas_modelo_65: bool = False,
                              lojas_filtro: List[str] = None) -> List[Dict]:
    """Realiza validação cruzada otimizada de todos os validadores vs todos os relatórios
    
    Args:
        validadores: Dict com DataFrames dos validadores
        relatorios: Dict com DataFrames dos relatórios
        contextos: Dict com contexto de numeração dos relatórios
        apenas_modelo_65: Se True, filtra apenas modelo 65
        lojas_filtro: Lista de lojas a validar
    
    Returns:
        Lista de dicts com resultados de cada validação
    """
    print(f"[*] Executando validação cruzada otimizada...")
    print(f"    {len(validadores)} validador(es) × {len(relatorios)} relatório(s) = {len(validadores) * len(relatorios)} validações\n")
    
    resultados_validacoes = []
    validacao_atual = 0
    total = len(validadores) * len(relatorios)
    
    for val_nome, df_pulos in validadores.items():
        for rel_nome, df_relatorio in relatorios.items():
            validacao_atual += 1
            
            print(f"[{validacao_atual}/{total}] Validando: {val_nome} ✕ {rel_nome}")
            
            try:
                # Extrair contexto para este relatório
                contexto_numeracao = contextos.get(rel_nome, {})
                
                # Extrair notas existentes
                notas_existentes = {}
                if not df_relatorio.empty:
                    for _, row in df_relatorio.iterrows():
                        try:
                            loja = str(row['Loja']).strip()
                            nota = int(row['NF'])
                            serie = int(row['Sequência'])
                            status = str(row['Status']).strip()
                            chave = (loja, nota, serie)
                            notas_existentes[chave] = status
                        except:
                            continue
                
                # Validar pulos
                analise_resultado, stats_modelos = validar_pulos(
                    df_pulos, df_relatorio, contexto_numeracao, notas_existentes,
                    apenas_modelo_65=apenas_modelo_65,
                    lojas_filtro=lojas_filtro
                )
                
                # Calcular estatísticas
                pulos_reais = len(analise_resultado[analise_resultado['Tipo_Validação'].str.contains('[PULO REAL]', regex=False)])
                
                print(f"    ✓ {len(analise_resultado):,} analisados | {pulos_reais} REAIS\n")
                
                resultados_validacoes.append({
                    'validador_nome': val_nome,
                    'relatorio_nome': rel_nome,
                    'df_analise': analise_resultado,
                    'stats_modelos': stats_modelos,
                    'total_pulos': len(analise_resultado),
                    'pulos_reais': pulos_reais
                })
            
            except Exception as e:
                print(f"    ✗ ERRO: {str(e)}\n")
                continue
    
    print(f"OK - {len(resultados_validacoes)} validação(ões) concluída(s)\n")
    return resultados_validacoes


def localizar_arquivos_relatorio(caminho_base: Path) -> List[Path]:
    """Localiza todos os arquivos de relatório 3.2.22 disponíveis"""
    print("[*] Procurando arquivos de relatório...")
    
    # Padrões possíveis de nomes
    padoes = [
        "3.2.22_Vendas_NFCe_SAT.xls",
        "*3.2.22*.xls",
        "*3.2.22*.xlsx",
    ]
    
    arquivos_encontrados = []
    
    # Procurar arquivos
    for padrao in padoes:
        fornecidos = list(caminho_base.glob(padrao))
        for arquivo in fornecidos:
            if arquivo not in arquivos_encontrados:
                arquivos_encontrados.append(arquivo)
    
    if not arquivos_encontrados:
        print(f"    AVISO - Nenhum arquivo 3.2.22 encontrado em {caminho_base}")
        return []
    
    print(f"    OK - {len(arquivos_encontrados)} arquivo(s) encontrado(s)")
    for arq in arquivos_encontrados:
        print(f"        • {arq.name}")
    
    return arquivos_encontrados


def carregar_relatorio_322(arquivos_relatorio: List[Path]) -> Tuple[pd.DataFrame, Dict]:
    """Carrega e processa o(s) relatório(s) 3.2.22"""
    print("\n[*] Carregando relatório 3.2.22...")
    
    if not arquivos_relatorio:
        raise Exception("Nenhum arquivo de relatório foi fornecido")
    
    print(f"    Processando {len(arquivos_relatorio)} arquivo(s)...")
    
    # Verificar existência de todos os arquivos
    para_carregar = []
    for arquivo in arquivos_relatorio:
        if arquivo.exists():
            para_carregar.append(arquivo)
        else:
            print(f"    AVISO - Arquivo não encontrado: {arquivo}")
    
    if not para_carregar:
        raise Exception("Nenhum arquivo válido encontrado para carregar")
    
    # Combinar dados de todos os relatórios
    todas_as_linhas = []
    total_registros_lidos = 0
    contexto_numeracao = {}  # min/max por loja e série
    
    for idx, arquivo_path in enumerate(para_carregar, 1):
        try:
            print(f"    [{idx}] Carregando: {arquivo_path.name}")
            
            # Ler sem header para processar a estrutura complexa
            df_raw = pd.read_excel(arquivo_path, sheet_name=0, header=None)
            
            df_limpo = []
            loja_atual = None
            
            # Processar linha por linha mantendo contexto de loja
            for data_idx, row in df_raw.iterrows():
                # Detectar nova loja (suporta H001, L01, LIVE01, LV001, etc.)
                if pd.notna(row[0]) and isinstance(row[0], str) and " - " in str(row[0]):
                    tentativa_loja = str(row[0]).split(" -")[0].strip()
                    # Padrão: 1-4 letras seguidas de 1-4 dígitos
                    if re.match(r'^[A-Z]{1,4}\d{1,4}$', tentativa_loja):
                        loja_atual = tentativa_loja
                
                # Se tem NF (coluna 2) e loja, extrai dados
                if pd.notna(row[2]) and loja_atual:
                    try:
                        nf = int(pd.to_numeric(row[2], errors='coerce'))
                        serie = int(pd.to_numeric(row[3], errors='coerce'))
                        status = str(row[11]).strip() if pd.notna(row[11]) else "DESCONHECIDO"
                        
                        df_limpo.append({
                            'Loja': loja_atual,
                            'NF': nf,
                            'Sequência': serie,
                            'Status': status
                        })
                        
                        # Rastrear min/max de numeração por loja e série
                        if loja_atual not in contexto_numeracao:
                            contexto_numeracao[loja_atual] = {}
                        if serie not in contexto_numeracao[loja_atual]:
                            contexto_numeracao[loja_atual][serie] = {'min': nf, 'max': nf}
                        else:
                            contexto_numeracao[loja_atual][serie]['min'] = min(contexto_numeracao[loja_atual][serie]['min'], nf)
                            contexto_numeracao[loja_atual][serie]['max'] = max(contexto_numeracao[loja_atual][serie]['max'], nf)
                    
                    except (ValueError, TypeError):
                        continue
            
            if df_limpo:
                df_temp = pd.DataFrame(df_limpo)
                todas_as_linhas.append(df_temp)
                total_registros_lidos += len(df_limpo)
                print(f"        OK - {len(df_limpo)} registros")
            else:
                print(f"        OK - 0 registros (nenhum dado válido encontrado)")
            
        except Exception as e:
            print(f"        AVISO ao carregar: {str(e)}")
            print(f"        Continuando com próximo arquivo...")
    
    # Consolidar todos em um DataFrame único
    if todas_as_linhas:
        df_relatorio = pd.concat(todas_as_linhas, ignore_index=True)
    else:
        df_relatorio = pd.DataFrame()
    
    print(f"    OK - Total de {total_registros_lidos} registros consolidados")
    
    return df_relatorio, contexto_numeracao


def extrair_notas_existentes(df_relatorio: pd.DataFrame) -> Dict:
    """Extrai mapa de notas existentes do relatório"""
    notas_existentes = {}
    
    if df_relatorio.empty:
        return notas_existentes
    
    for _, row in df_relatorio.iterrows():
        try:
            loja = str(row['Loja']).strip()
            nota = int(row['NF'])
            
            # Verificar qual coluna de série/sequência existe
            serie_col = 'Sequência' if 'Sequência' in df_relatorio.columns else 'Série'
            serie = int(row[serie_col])
            
            status = str(row['Status']).strip()
            
            chave = (loja, nota, serie)
            notas_existentes[chave] = status
        except KeyError as e:
            print(f"    AVISO: Coluna não encontrada - {e}")
            print(f"    Colunas disponíveis: {list(df_relatorio.columns)}")
            raise
        except Exception as e:
            print(f"    AVISO processando linha em extrair_notas: {e}")
            continue
    
    return notas_existentes


def validar_pulos(df_pulos: pd.DataFrame, df_relatorio: pd.DataFrame, 
                 contexto_numeracao: Dict, notas_existentes: Dict, 
                 apenas_modelo_65: bool = False, lojas_filtro: List[str] = None) -> Tuple[pd.DataFrame, Dict]:
    """Valida os pulos contra o relatório - VERSÃO OTIMIZADA COM VETORIZAÇÃO
    
    Args:
        apenas_modelo_65: Se True, filtra apenas NFCe (modelo 65)
        lojas_filtro: Lista de lojas a validar. Se None, valida todas
    
    Returns:
        Tupla com (DataFrame de análise, Dict com estatísticas de modelos)
    """
    print("\n[*] Validando pulos...")
    if apenas_modelo_65:
        print("    [FILTRO] Apenas modelo 65 (NFCe) será considerado")
    if lojas_filtro:
        print(f"    [FILTRO] Apenas lojas: {', '.join(lojas_filtro)}")
    
    # Preparar cópia de trabalho do df_pulos
    df_trabalho = df_pulos.copy()
    
    # Normalizar nomes de colunas
    loja_col = 'Loja.' if 'Loja.' in df_trabalho.columns else 'Loja'
    serie_col = 'Serie' if 'Serie' in df_trabalho.columns else 'Série'
    
    # Converter para tipos corretos
    df_trabalho['Loja_Clean'] = df_trabalho[loja_col].astype(str).str.strip()
    df_trabalho['Nota_Clean'] = pd.to_numeric(df_trabalho['Nota'], errors='coerce').fillna(0).astype(int)
    df_trabalho['Serie_Clean'] = pd.to_numeric(df_trabalho[serie_col], errors='coerce').fillna(0).astype(int)
    df_trabalho['Modelo_Clean'] = df_trabalho['Modelo'].astype(str).str.strip()
    
    # Extrair número do modelo (vetorizado)
    df_trabalho['Modelo_Num'] = df_trabalho['Modelo_Clean'].apply(
        lambda x: "65" if "65" in x else ("55" if "55" in x else "outros")
    )
    
    # Filtro de modelo 65
    if apenas_modelo_65:
        df_trabalho = df_trabalho[df_trabalho['Modelo_Num'] == "65"].copy()
    
    # Filtro de lojas
    if lojas_filtro:
        df_trabalho = df_trabalho[df_trabalho['Loja_Clean'].isin(lojas_filtro)].copy()
    
    # Remover linhas inválidas
    df_trabalho = df_trabalho[df_trabalho['Loja_Clean'] != 'nan'].copy()
    df_trabalho = df_trabalho[(df_trabalho['Nota_Clean'] > 0) & (df_trabalho['Serie_Clean'] > 0)].copy()
    
    # Criar chaves para lookup
    df_trabalho['Chave'] = list(zip(df_trabalho['Loja_Clean'], df_trabalho['Nota_Clean'], df_trabalho['Serie_Clean']))
    
    # Validação vetorizada
    def validar_pulo(row):
        """Valida um pulo individual"""
        loja = row['Loja_Clean']
        nota = row['Nota_Clean']
        serie = row['Serie_Clean']
        chave = row['Chave']
        
        tipo_pulo = "[PULO REAL]"
        validacao = "Numeração não existe no relatório"
        contexto = "Sem dados da série no relatório"
        status_relatorio = "NÃO ENCONTRADA"
        
        # Verificar contexto de numeração
        if loja in contexto_numeracao and serie in contexto_numeracao[loja]:
            min_nota = contexto_numeracao[loja][serie]['min']
            max_nota = contexto_numeracao[loja][serie]['max']
            
            if nota < min_nota:
                contexto = f"ANTES da série (min={min_nota})"
            elif nota > max_nota:
                contexto = f"APÓS da série (max={max_nota})"
            else:
                contexto = f"DENTRO da série (min={min_nota}, max={max_nota})"
        
        # Verificar se existe no relatório
        if chave in notas_existentes:
            status_relatorio = notas_existentes[chave]
            if "CANCELADA" in status_relatorio and status_relatorio.startswith("CANCELADA"):
                tipo_pulo = "[CANCELADA - NÃO É PULO]"
                validacao = f"Nota existe no relatório com status: {status_relatorio}"
            else:
                tipo_pulo = "[FALSO POSITIVO]"
                validacao = "Nota existe no relatório"
        
        return pd.Series({
            'Tipo_Validação': tipo_pulo,
            'Status_Relatório': status_relatorio,
            'Contexto': contexto,
            'Observação': validacao
        })
    
    # Aplicar validação vetorizada
    resultados_val = df_trabalho.apply(validar_pulo, axis=1)
    
    # Combinar resultados
    df_resultado = pd.DataFrame({
        'Loja': df_trabalho['Loja_Clean'].values,
        'Nota': df_trabalho['Nota_Clean'].values,
        'Sequência': df_trabalho['Serie_Clean'].values,
        'Modelo': df_trabalho['Modelo_Clean'].values,
        'Tipo_Validação': resultados_val['Tipo_Validação'].values,
        'Status_Relatório': resultados_val['Status_Relatório'].values,
        'Contexto': resultados_val['Contexto'].values,
        'Observação': resultados_val['Observação'].values
    })
    
    # Calcular estatísticas de modelos
    stats_modelos = {
        '65': len(df_pulos[df_pulos['Modelo'].astype(str).str.contains('65', na=False)]),
        '55': len(df_pulos[df_pulos['Modelo'].astype(str).str.contains('55', na=False)]),
        'outros': len(df_pulos[~df_pulos['Modelo'].astype(str).str.contains('65|55', na=False, regex=True)])
    }
    
    print(f"    OK - {len(df_resultado)} pulos analisados")
    print(f"    Modelos encontrados: Modelo 65 (NFCe): {stats_modelos['65']}, Modelo 55 (NFe): {stats_modelos['55']}, Outros: {stats_modelos['outros']}")
    
    return df_resultado, stats_modelos


def gerar_relatorio_summary(analise_resultado: pd.DataFrame, stats_modelos: Dict = None) -> Dict:
    """Gera sumário detalhado da análise"""
    if analise_resultado is None or len(analise_resultado) == 0:
        return {}
    
    if stats_modelos is None:
        stats_modelos = {'65': 0, '55': 0, 'outros': 0}
    
    total_pulos = len(analise_resultado)
    pulos_reais = analise_resultado[analise_resultado['Tipo_Validação'].str.contains('[PULO REAL]', regex=False)]
    falsos_positivos = analise_resultado[analise_resultado['Tipo_Validação'].str.contains('[FALSO POSITIVO]', regex=False)]
    canceladas = analise_resultado[analise_resultado['Tipo_Validação'].str.contains('[CANCELADA', regex=False)]
    
    # Análise de pulos reais por contexto
    contextos_detalhes = {}
    if len(pulos_reais) > 0:
        contextos_contagem = pulos_reais['Contexto'].value_counts()
        for contexto, qtd in contextos_contagem.items():
            # Extrair tipo de contexto
            if 'ANTES' in contexto:
                tipo = 'ANTES da sequência'
            elif 'DENTRO' in contexto:
                tipo = 'DENTRO da sequência'
            elif 'APÓS' in contexto:
                tipo = 'APÓS da sequência'
            else:
                tipo = 'SEM DADOS'
            
            contextos_detalhes[tipo] = qtd
    
    summary = {
        'total_pulos_detectados': total_pulos,
        'pulos_reais': len(pulos_reais),
        'falsos_positivos': len(falsos_positivos),
        'notas_canceladas': len(canceladas),
        'percentual_precisao': (len(pulos_reais) / total_pulos * 100) if total_pulos > 0 else 0,
        'contextos': contextos_detalhes,
        'lojas_afetadas': len(analise_resultado['Loja'].unique()) if not analise_resultado.empty else 0,
        'sequencias_afetadas': len(analise_resultado['Sequência'].unique()) if not analise_resultado.empty else 0,
        'modelos': stats_modelos
    }
    
    return summary


def gerar_grafico_ascii(analise_resultado: pd.DataFrame) -> str:
    """Gera gráfico em ASCII de pulos reais por loja"""
    if analise_resultado is None or len(analise_resultado) == 0:
        return ""
    
    # Filtrar apenas pulos reais
    pulos_reais = analise_resultado[analise_resultado['Tipo_Validação'].str.contains('[PULO REAL]', regex=False)]
    
    if len(pulos_reais) == 0:
        return ""
    
    # Contar por loja
    lojas_pulos = pulos_reais['Loja'].value_counts().sort_values(ascending=False)
    
    # Encontrar valor máximo para escala
    max_valor = lojas_pulos.max()
    largura_barra = 50  # Largura máxima da barra em caracteres
    
    # Construir gráfico
    linhas = [
        "\n" + "=" * 90,
        "📊 GRÁFICO: PULOS REAIS DETECTADOS POR LOJA".center(90),
        "=" * 90,
        ""
    ]
    
    for loja, qtd in lojas_pulos.items():
        # Calcular tamanho da barra proporcional
        tamanho_barra = max(1, int((qtd / max_valor) * largura_barra))
        barra = "█" * tamanho_barra
        percentual = (qtd / len(pulos_reais)) * 100
        
        # Formatar linha com números primeiro, depois barra
        # Isso garante alinhamento visual melhor
        linha = f"  Loja {loja:5} │ {qtd:3} │ {barra:50} ({percentual:5.1f}%)"
        linhas.append(linha)
    
    linhas.extend([
        "",
        "  " + "─" * 86,
        "  Total de pulos reais: " + str(len(pulos_reais)),
        "=" * 90,
        ""
    ])
    
    return "\n".join(linhas)


def gerar_texto_sumario(summary: Dict) -> str:
    """Gera texto descritivo do sumário para exibição"""
    if not summary:
        return ""
    
    modelos_info = summary.get('modelos', {})
    linhas = [
        "=" * 80,
        "📋 RESUMO EXECUTIVO DA VALIDAÇÃO".center(80),
        "=" * 80,
        "",
        "🔍 ESTATÍSTICAS GERENCIADAS:",
        f"",
        f"  Total de pulos detectados pelo validador:      {summary['total_pulos_detectados']:>6} registros",
        f"  Pulos REAIS (cruzamento com relatório):        {summary['pulos_reais']:>6} registros",
        f"  Falsos positivos:                               {summary['falsos_positivos']:>6} registros",
        f"  Notas CANCELADA (não são pulos):               {summary.get('notas_canceladas', 0):>6} registros",
        f"  Taxa de precisão:                               {summary['percentual_precisao']:>5.1f}%",
        "",
        "📍 CONFORMIDADE:",
        f"  Lojas analisadas:                               {summary['lojas_afetadas']:>6} lojas",
        f"  Sequências/Séries afetadas:                     {summary['sequencias_afetadas']:>6} séries",
        "",
        "📦 DISTRIBUIÇÃO POR MODELO DE DOCUMENTO:",
        f"  • Modelo 65 (NFCe):                             {modelos_info.get('65', 0):>6} pulos",
        f"  • Modelo 55 (NFe):                              {modelos_info.get('55', 0):>6} pulos",
        f"  • Outros modelos:                               {modelos_info.get('outros', 0):>6} pulos",
        "",
        "⚠️  LOCALIZAÇÃO DOS PULOS REAIS NA SEQUÊNCIA:",
    ]
    
    if summary['pulos_reais'] > 0:
        if summary['contextos']:
            for contexto, qtd in summary['contextos'].items():
                percentual = (qtd / summary['pulos_reais'] * 100) if summary['pulos_reais'] > 0 else 0
                linhas.append(f"  • {contexto:40} {qtd:>6} pulos ({percentual:>5.1f}%)")
        else:
            linhas.append("  • Nenhum pulo real encontrado")
    else:
        linhas.append("  • Nenhum pulo real detectado (excelente!)")
    
    linhas.extend([
        "",
        "=" * 80,
    ])
    
    return "\n".join(linhas)


def exportar_resultado(caminho_base: Path, analise_resultado: pd.DataFrame, summary: Dict, apenas_modelo_65: bool = False, nome_validador: str = None, nome_relatorio: str = None) -> Path:
    """Exporta resultado para arquivo Excel em pasta organizada por data
    
    Args:
        caminho_base: Caminho base para salvar resultados
        analise_resultado: DataFrame com análise dos pulos
        summary: Dicionário com sumário
        apenas_modelo_65: Se True, adiciona sufixo _NFCE
        nome_validador: Nome do arquivo validador (para naming)
        nome_relatorio: Nome do arquivo relatório (para naming)
    """
    if analise_resultado is None or analise_resultado.empty:
        print("[ERRO] Nenhuma análise para exportar")
        return None
    
    try:
        # Converter para Path se for string
        if isinstance(caminho_base, str):
            caminho_base = Path(caminho_base)
        
        # Garantir que o caminho base existe
        caminho_base.mkdir(parents=True, exist_ok=True)
        
        # Criar subpasta com data (AAAA-MM-DD)
        data_pasta = datetime.now().strftime("%Y-%m-%d")
        caminho_data = caminho_base / data_pasta
        caminho_data.mkdir(parents=True, exist_ok=True)
        
        print(f"\n[*] Criando pasta: {caminho_data}")
        print(f"    Pasta existe: {caminho_data.exists()}")
        
        sufixo = "_NFCE" if apenas_modelo_65 else ""
        
        # Se temos nomes dos arquivos, usar para naming mais descritivo
        if nome_validador and nome_relatorio:
            # Remover extensões e caracteres inválidos
            val_clean = nome_validador.replace('.xlsx', '').replace('.xls', '').replace(' ', '_')[:30]
            rel_clean = nome_relatorio.replace('.xlsx', '').replace('.xls', '').replace(' ', '_')[:30]
            timestamp = datetime.now().strftime("%H%M%S")
            nome_arquivo = f"Validacao{sufixo}_Val{val_clean}_Rel{rel_clean}_{timestamp}.xlsx"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"Validacao_Pulos{sufixo}_{timestamp}.xlsx"
        
        caminho_saida = caminho_data / nome_arquivo
        
        print(f"[*] Exportando resultado para: {caminho_saida}")
        print(f"    Caminho absoluto: {caminho_saida.absolute()}")
        
        # Criar writer para Excel
        with pd.ExcelWriter(caminho_saida, engine='openpyxl') as writer:
            # Aba 1: Resultado detalhado
            analise_resultado.to_excel(writer, sheet_name='Validação Detalhada', index=False)
            
            # Aba 2: Sumário
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='Sumário', index=False)
            
            # Aba 3: Apenas pulos reais com análise de contexto
            pulos_reais = analise_resultado[
                analise_resultado['Tipo_Validação'].str.contains('[PULO REAL]', regex=False)
            ].sort_values(['Loja', 'Contexto'])
            if not pulos_reais.empty:
                pulos_reais.to_excel(writer, sheet_name='Pulos Reais', index=False)
            
            # Aba 4: Sumário por contexto
            if len(pulos_reais) > 0:
                contexto_summary = pulos_reais['Contexto'].value_counts().reset_index()
                contexto_summary.columns = ['Contexto', 'Quantidade']
                contexto_summary.to_excel(writer, sheet_name='Resumo por Contexto', index=False)
            
            # Aba 5: Informações sobre o relatório
            info_data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            info_items = {
                'Informação': ['Validador', 'Criado por', 'Data de Execução', 'Versão'],
                'Valor': ['Validador de Pulos de NFCe v3.0', 'João Nogueira', info_data, '3.0']
            }
            
            if nome_validador:
                info_items['Informação'].append('Arquivo Validador')
                info_items['Valor'].append(nome_validador)
            
            if nome_relatorio:
                info_items['Informação'].append('Arquivo Relatório')
                info_items['Valor'].append(nome_relatorio)
            
            info_df = pd.DataFrame(info_items)
            info_df.to_excel(writer, sheet_name='Informações', index=False)
            
            # Ajustar largura das colunas
            for sheet in writer.sheets.values():
                for column in sheet.columns:
                    max_length = max(len(str(cell.value)) for cell in column)
                    adjusted_width = min(max_length + 2, 50)
                    sheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        # Verificar se arquivo foi criado
        if caminho_saida.exists():
            print(f"    ✓ OK - Arquivo salvo: {caminho_saida}")
            print(f"    ✓ Tamanho do arquivo: {caminho_saida.stat().st_size / 1024:.2f} KB")
            return caminho_saida
        else:
            print(f"    ✗ ERRO - Arquivo não foi criado: {caminho_saida}")
            return None
    
    except Exception as e:
        print(f"    ✗ ERRO ao salvar arquivo: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None


def main():
    """Função principal"""
    caminho_base = Path("C:/Users/João/Desktop/Valida pulo/planilhas")
    
    print("=" * 70)
    print("VALIDADOR DE PULOS DE NUMERAÇÃO DE NFCe".center(70))
    print("=" * 70)
    
    # Pergunta ao usuário se quer filtrar apenas modelo 65
    print("\n[?] Validação APENAS sobre modelo 65 (NFCe)?")
    print("    (Relatório 3.2.22 contém apenas NFCe)")
    print("    [S] Sim - Validar apenas NFCe (modelo 65)")
    print("    [N] Não - Incluir modelo 55 (NFe) também")
    
    resposta = input("\nEscolha [S/N]: ").strip().upper()
    apenas_modelo_65 = resposta in ['S', 'SIM', '']  # Default é sim
    
    try:
        # Localizar e carregar validadores de quebra (MÚLTIPLOS)
        print("\n[*] Procurando validadores de quebra...")
        # Padrões possíveis de nomes
        padroes_pulos = [
            "ListaPuloNotas_*.xlsx",
            "*ListaPulo*.xlsx",
            "*pulos*.xlsx",
        ]
        
        arquivos_pulos = []
        for padrao in padroes_pulos:
            encontrados = list(caminho_base.glob(padrao))
            for arquivo in encontrados:
                if arquivo not in arquivos_pulos:
                    arquivos_pulos.append(arquivo)
        
        if not arquivos_pulos:
            print("    AVISO - Nenhum arquivo de validador encontrado")
            print("    Usando método manual...")
            arquivo_pulos_manual = caminho_base / "ListaPuloNotas_20260408_092156.xlsx"
            if arquivo_pulos_manual.exists():
                arquivos_pulos = [arquivo_pulos_manual]
            else:
                raise Exception("Nenhum arquivo de validador encontrado")
        
        print(f"    OK - {len(arquivos_pulos)} validador(es) encontrado(s)")
        for arq in arquivos_pulos:
            print(f"        • {arq.name}")
        
        # Localizar relatórios 3.2.22 (MÚLTIPLOS)
        arquivos_relatorio = localizar_arquivos_relatorio(caminho_base)
        
        print(f"\n[✓] CONFIGURAÇÃO:")
        print(f"    Validadores: {len(arquivos_pulos)}")
        print(f"    Relatórios: {len(arquivos_relatorio)}")
        print(f"    Total de validações: {len(arquivos_pulos) * len(arquivos_relatorio)}")
        
        # ===== VERSÃO OTIMIZADA =====
        # [1] CARREGAR TODOS EM MEMÓRIA
        print(f"\n[1/5] Carregando TODOS os validadores em memória...")
        validadores = carregar_todos_validadores(arquivos_pulos)
        
        # [2] EXTRAIR IDs DE LOJA
        print(f"[2/5] Extraindo IDs de loja do validador...")
        lojas_do_validador = extrair_lojas_do_validador(validadores)
        
        print(f"[3/5] Carregando TODOS os relatórios em memória...")
        relatorios, contextos = carregar_todos_relatorios_otimizado(arquivos_relatorio, lojas_esperadas=lojas_do_validador)
        
        # [4] VALIDAÇÃO CRUZADA OTIMIZADA
        print(f"[4/5] Executando validação cruzada otimizada...")
        resultados = validar_cruzado_otimizado(
            validadores, relatorios, contextos,
            apenas_modelo_65=apenas_modelo_65
        )
        
        if not resultados:
            print("\n⚠ AVISO: Nenhuma validação foi concluída")
            return
        
        # [5] EXPORTAR TODOS OS RESULTADOS
        print(f"[5/5] Exportando resultados...")
        todos_os_resultados = []
        
        for idx, resultado in enumerate(resultados, 1):
            try:
                summary = gerar_relatorio_summary(resultado['df_analise'], resultado['stats_modelos'])
                
                arquivo_saida = exportar_resultado(
                    caminho_base,
                    resultado['df_analise'],
                    summary,
                    apenas_modelo_65=apenas_modelo_65,
                    nome_validador=resultado['validador_nome'],
                    nome_relatorio=resultado['relatorio_nome']
                )
                
                if arquivo_saida:
                    todos_os_resultados.append({
                        'validador': resultado['validador_nome'],
                        'relatorio': resultado['relatorio_nome'],
                        'pulos_detectados': resultado['total_pulos'],
                        'pulos_reais': resultado['pulos_reais'],
                        'arquivo_saida': arquivo_saida.name
                    })
            
            except Exception as e:
                print(f"    ERRO ao exportar resultado {idx}: {str(e)}")
                continue
        
        # SUMÁRIO FINAL
        print(f"\n\n{'='*70}")
        print("SUMÁRIO FINAL DA VALIDAÇÃO CRUZADA OTIMIZADA".center(70))
        print(f"{'='*70}\n")
        
        if todos_os_resultados:
            print(f"✅ Total de {len(todos_os_resultados)} validação(ões) concluída(s)\n")
            
            # Tabela de resultados
            print(f"{'Validador':30} | {'Relatório':30} | {'Detectados':>10} | {'Reais':>6}")
            print("-" * 80)
            
            for resultado in todos_os_resultados:
                print(f"{resultado['validador']:30} | {resultado['relatorio']:30} | {resultado['pulos_detectados']:>10} | {resultado['pulos_reais']:>6}")
            
            print(f"\n{'='*70}")
            print("Arquivos gerados:")
            for idx, resultado in enumerate(todos_os_resultados, 1):
                print(f"[{idx}] {resultado['arquivo_saida']}")
        
        data_execucao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"\n{'='*70}")
        print("✅ VALIDAÇÃO CRUZADA OTIMIZADA CONCLUÍDA!")
        print(f"Executado em: {data_execucao}")
        print(f"{'='*70}")
    
    except Exception as e:
        print(f"\n[ERRO] Erro durante a validação: {e}")
        raise


if __name__ == "__main__":
    main()
