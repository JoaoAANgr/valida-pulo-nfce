#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para gerar executável do Validador de Pulos NFCe
Converte a aplicação Tkinter em um .exe standalone
"""

import subprocess
import sys
import os
from pathlib import Path

def gerar_executavel():
    """Gera executável usando PyInstaller"""
    
    print("=" * 60)
    print("Gerando Executável - Validador de Pulos NFCe v3.0")
    print("=" * 60)
    
    # Instalar PyInstaller se não estiver instalado
    print("\n[1/4] Verificando PyInstaller...")
    try:
        import pyinstaller
        print("      ✓ PyInstaller já está instalado")
    except ImportError:
        print("      Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pyinstaller"])
        print("      ✓ PyInstaller instalado")
    
    # Limpar executável antigo se existir
    print("\n[1.5/4] Limpando arquivos antigos...")
    exe_path = Path("dist/Validador_Pulos_NFCe.exe")
    if exe_path.exists():
        try:
            exe_path.unlink()
            print("      ✓ Arquivo antigo removido")
        except PermissionError:
            print("      ⚠ Arquivo ainda está em uso, tentaremos sobrescrever...")
    
    # Detectar o caminho do venv
    venv_path = Path(".venv/Lib/site-packages")
    if not venv_path.exists():
        print("      ⚠ ERRO: Ambiente virtual não encontrado!")
        print("      Execute antes: python -m venv .venv")
        print("      Depois: .venv\\Scripts\\pip install -r requirements.txt")
        return False
    
    print(f"      ✓ Usando: {venv_path}")
    
    # Criar pasta de saída
    print("\n[2/4] Preparando pasta de saída...")
    output_dir = Path("dist")
    build_dir = Path("build")
    spec_dir = Path("build")
    
    print(f"      ✓ Executável em: {output_dir}")
    
    # Comando PyInstaller
    print("\n[3/4] Gerando executável (pode levar alguns minutos)...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                                  # Um arquivo único
        "--windowed",                                 # Sem console
        "--clean",                                    # Limpar antes de compilar
        "--name", "Validador_Pulos_NFCe",           # Nome do exe
        f"--distpath={output_dir}",
        f"--workpath={build_dir}",
        f"--specpath={spec_dir}",
        "interface_validador.py"
    ]
    
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"      ✗ ERRO ao gerar: {e}")
        return False
    
    # Confirmar sucesso
    print("\n[4/4] Verificando resultado...")
    exe_path = output_dir / "Validador_Pulos_NFCe.exe"
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"      ✓ Sucesso!")
        print(f"      ✓ Arquivo: {exe_path}")
        print(f"      ✓ Tamanho: {size_mb:.1f} MB")
        print("\n" + "=" * 60)
        print("✅ EXECUTÁVEL GERADO COM SUCESSO!")
        print("=" * 60)
        print(f"\nClique 2x em: dist/Validador_Pulos_NFCe.exe")
        print("\nOu execute via terminal:")
        print(f"  {exe_path}")
        return True
    else:
        print(f"      ✗ Arquivo não encontrado: {exe_path}")
        return False

if __name__ == "__main__":
    sucesso = gerar_executavel()
    sys.exit(0 if sucesso else 1)
