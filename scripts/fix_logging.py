#!/usr/bin/env python3
"""
Script automático de Refixação: Converte print(f"Error...") para logger.error()
Uso: python scripts/fix_logging.py [--dry-run] [--file path/to/file.py]
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple


class LoggingFixer:
    """Automaticamente fixa logging deficiente"""
    
    # Padrão para detectar print() de erro
    PRINT_ERROR_PATTERN = re.compile(
        r'print\s*\(\s*f?"Error[:\s]*\{.*\}\s*"\s*\)',
        re.MULTILINE | re.IGNORECASE
    )

    @staticmethod
    def needs_logger(file_content: str) -> bool:
        """Verifica se arquivo precisa adicionar 'import logging'"""
        return 'import logging' not in file_content and 'logger = ' not in file_content

    @staticmethod
    def add_imports(file_content: str) -> str:
        """Adiciona imports necessários"""
        if LoggingFixer.needs_logger(file_content):
            # Adicionar após imports existentes
            lines = file_content.split('\n')
            import_end = 0
            
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_end = i + 1
            
            if import_end > 0:
                lines.insert(import_end, 'import logging')
                # Encontrar primeira classe/função e adicionar logger setup
                for i in range(import_end + 1, len(lines)):
                    if lines[i].startswith('class ') or (lines[i].startswith('def ') and not lines[i].startswith('def _')):
                        logger_setup = f"\nlogger = logging.getLogger(__name__)"
                        lines.insert(i, logger_setup)
                        break
                
                file_content = '\n'.join(lines)
        
        return file_content

    @staticmethod
    def fix_print_statements(file_content: str) -> Tuple[str, int]:
        """Converte print(f"Error...") para logger.error()"""
        
        # Padrão para print de erro mais flexível
        pattern = r'print\s*\(\s*f?"([^"]*Error[^"]*:\s*\{[^}]*\}[^"]*)"\s*\)'
        
        matches = list(re.finditer(pattern, file_content, re.IGNORECASE | re.MULTILINE))
        
        for match in reversed(matches):  # Reverter para não deslocar indices
            full_match = match.group(0)
            msg_content = match.group(1)
            
            # Converter para logger
            # E.g.: 'User not found: {e}' → 'User not found: {e}', exc_info=True
            new_statement = f'logger.error(f"{msg_content}", exc_info=True)'
            
            file_content = file_content[:match.start()] + new_statement + file_content[match.end():]
        
        return file_content, len(matches)

    @staticmethod
    def fix_except_pass(file_content: str) -> Tuple[str, int]:
        """Fixa except: pass sem logging"""
        
        # Padrão: except SomeError:\n            pass (sem logging)
        pattern = r'except\s+(\w+(?:\s*,\s*\w+)*)\s*:\s*(?!.*logger|.*print)(\n\s+pass)'
        
        matches = list(re.finditer(pattern, file_content, re.MULTILINE))
        count = len(matches)
        
        for match in reversed(matches):
            exception_type = match.group(1)
            
            new_code = f'except {exception_type}:\n            logger.debug(f"Handled {{exception_type}}: {{e}}")'
            
            file_content = file_content[:match.start()] + new_code + file_content[match.end():]
        
        return file_content, count

    @classmethod
    def fix_file(cls, file_path: Path) -> Tuple[bool, int]:
        """Fixa um arquivo individual"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # 1. Adicionar imports
            content = cls.add_imports(content)
            
            # 2. Fixar print statements
            content, print_count = cls.fix_print_statements(content)
            
            # 3. Fixar except pass
            content, except_count = cls.fix_except_pass(content)
            
            # Escrever se algo mudou
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True, print_count + except_count
            
            return False, 0
            
        except Exception as e:
            print(f"❌ Erro processing {file_path}: {e}")
            return False, 0


def find_python_files(root_path: Path = None) -> List[Path]:
    """Encontra todos os arquivos .py no projeto"""
    if root_path is None:
        root_path = Path.cwd()
    
    # Ignorar: __pycache__, .git, venv
    ignore_dirs = {'__pycache__', '.git', 'venv', '.venv', 'node_modules', '.env'}
    
    python_files = []
    for py_file in root_path.rglob('*.py'):
        if not any(part in ignore_dirs for part in py_file.parts):
            python_files.append(py_file)
    
    return sorted(python_files)


async def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix logging issues automatically')
    parser.add_argument('--dry-run', action='store_true', help='Não fazer mudanças, apenas mostrar')
    parser.add_argument('--file', type=Path, help='Fixar arquivo específico')
    
    args = parser.parse_args()
    
    if args.file:
        files = [args.file]
    else:
        files = find_python_files(Path('cogs')) + find_python_files(Path('utils')) + find_python_files(Path('scripts'))
    
    print("="*60)
    print("🔧 LOGGING FIXER")
    print("="*60)
    print(f"Arquivos encontrados: {len(files)}")
    print()
    
    total_fixes = 0
    files_changed = 0
    
    for file_path in files:
        changed, fixes = LoggingFixer.fix_file(file_path)
        
        if changed:
            files_changed += 1
            total_fixes += fixes
            status = "✅" if not args.dry_run else "🔍"
            print(f"{status} {file_path.relative_to(Path.cwd())} → {fixes} correções")
    
    print()
    print("="*60)
    print(f"📊 RESUMO")
    print(f"   Arquivos alterados: {files_changed}/{len(files)}")
    print(f"   Total de correções: {total_fixes}")
    print(f"   Modo: {'DRY-RUN' if args.dry_run else 'APLICADO'}")
    print("="*60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
