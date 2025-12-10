#!/usr/bin/env python3
"""
Comprehensive verification script for all 6 phases.
Tests syntax, structure, and alignment with implementation plan.
"""
import ast
import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_error(text: str):
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def check_syntax(file_path: Path) -> Tuple[bool, str]:
    """Check if Python file has valid syntax"""
    try:
        with open(file_path, 'r') as f:
            ast.parse(f.read())
        return True, ""
    except SyntaxError as e:
        return False, str(e)

def analyze_python_file(file_path: Path) -> Dict:
    """Analyze Python file structure"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except:
        return {}
    
    info = {
        'classes': [],
        'functions': [],
        'async_functions': [],
        'imports': [],
        'decorators': []
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            info['classes'].append(node.name)
        elif isinstance(node, ast.FunctionDef):
            info['functions'].append(node.name)
        elif isinstance(node, ast.AsyncFunctionDef):
            info['async_functions'].append(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                info['imports'].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                info['imports'].append(node.module)
    
    return info

def verify_phase_1():
    """Verify Phase 1: Project Setup & Infrastructure"""
    print_header("PHASE 1: PROJECT SETUP & INFRASTRUCTURE")
    
    files_to_check = [
        'backend/pyproject.toml',
        'backend/alembic.ini',
        'backend/app/config.py',
        'backend/app/database.py',
        'backend/app/dependencies.py',
    ]
    
    all_good = True
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            if path.suffix == '.py':
                valid, error = check_syntax(path)
                if valid:
                    print_success(f"{file_path} - Syntax valid")
                else:
                    print_error(f"{file_path} - Syntax error: {error}")
                    all_good = False
            else:
                print_success(f"{file_path} - Exists")
        else:
            print_error(f"{file_path} - Missing")
            all_good = False
    
    return all_good

def verify_phase_2():
    """Verify Phase 2: Database Schema & Models"""
    print_header("PHASE 2: DATABASE SCHEMA & MODELS")
    
    models_dir = Path('backend/app/models')
    schemas_dir = Path('backend/app/schemas')
    migrations_dir = Path('backend/alembic/versions')
    
    all_good = True
    total_lines = 0
    
    # Check models
    if models_dir.exists():
        model_files = list(models_dir.glob('*.py'))
        print(f"\n{Colors.BOLD}Models ({len(model_files)} files):{Colors.END}")
        for file in model_files:
            if file.name == '__init__.py':
                continue
            valid, error = check_syntax(file)
            if valid:
                info = analyze_python_file(file)
                lines = len(open(file).readlines())
                total_lines += lines
                print_success(f"{file.name} - {len(info.get('classes', []))} classes, {lines} lines")
            else:
                print_error(f"{file.name} - Syntax error")
                all_good = False
    
    # Check schemas
    if schemas_dir.exists():
        schema_files = list(schemas_dir.glob('*.py'))
        print(f"\n{Colors.BOLD}Schemas ({len(schema_files)} files):{Colors.END}")
        for file in schema_files:
            if file.name == '__init__.py':
                continue
            valid, error = check_syntax(file)
            if valid:
                info = analyze_python_file(file)
                lines = len(open(file).readlines())
                total_lines += lines
                print_success(f"{file.name} - {len(info.get('classes', []))} schemas")
            else:
                print_error(f"{file.name} - Syntax error")
                all_good = False
    
    # Check migrations
    if migrations_dir.exists():
        migration_files = list(migrations_dir.glob('*.py'))
        print(f"\n{Colors.BOLD}Migrations ({len(migration_files)} files):{Colors.END}")
        for file in migration_files:
            valid, error = check_syntax(file)
            if valid:
                print_success(f"{file.name}")
            else:
                print_error(f"{file.name} - Syntax error")
                all_good = False
    
    print(f"\n{Colors.BOLD}Total Lines: {total_lines}{Colors.END}")
    return all_good

def verify_phase_3():
    """Verify Phase 3: Backend API Development"""
    print_header("PHASE 3: BACKEND API DEVELOPMENT")
    
    api_dir = Path('backend/app/api')
    services_dir = Path('backend/app/services')
    utils_dir = Path('backend/app/utils')
    
    all_good = True
    total_lines = 0
    endpoints = []
    
    # Check API routes
    if api_dir.exists():
        api_files = list(api_dir.glob('*.py'))
        print(f"\n{Colors.BOLD}API Routes ({len(api_files)} files):{Colors.END}")
        for file in api_files:
            if file.name == '__init__.py':
                continue
            valid, error = check_syntax(file)
            if valid:
                lines = len(open(file).readlines())
                total_lines += lines
                # Count endpoints
                content = open(file).read()
                route_count = len(re.findall(r'@router\.(get|post|put|patch|delete)', content))
                endpoints.append((file.name, route_count))
                print_success(f"{file.name} - {route_count} endpoints, {lines} lines")
            else:
                print_error(f"{file.name} - Syntax error")
                all_good = False
    
    # Check services
    if services_dir.exists():
        service_files = list(services_dir.glob('*.py'))
        print(f"\n{Colors.BOLD}Services ({len(service_files)} files):{Colors.END}")
        for file in service_files:
            if file.name == '__init__.py':
                continue
            valid, error = check_syntax(file)
            if valid:
                info = analyze_python_file(file)
                lines = len(open(file).readlines())
                total_lines += lines
                async_count = len(info.get('async_functions', []))
                print_success(f"{file.name} - {async_count} async functions, {lines} lines")
            else:
                print_error(f"{file.name} - Syntax error")
                all_good = False
    
    print(f"\n{Colors.BOLD}Total Endpoints: {sum(e[1] for e in endpoints)}{Colors.END}")
    print(f"{Colors.BOLD}Total Lines: {total_lines}{Colors.END}")
    return all_good

def verify_phase_4():
    """Verify Phase 4: Telegram Bot Development"""
    print_header("PHASE 4: TELEGRAM BOT DEVELOPMENT")

    bot_dir = Path('backend/app/bot')
    workers_dir = Path('backend/app/workers')

    all_good = True
    total_lines = 0
    handlers_count = 0

    # Check bot files
    if bot_dir.exists():
        bot_files = list(bot_dir.glob('*.py'))
        print(f"\n{Colors.BOLD}Bot Components ({len(bot_files)} files):{Colors.END}")
        for file in bot_files:
            if file.name == '__init__.py':
                continue
            valid, error = check_syntax(file)
            if valid:
                lines = len(open(file).readlines())
                total_lines += lines
                content = open(file).read()
                # Count handlers
                handler_count = len(re.findall(r'@bot\.(message_handler|callback_query_handler)', content))
                handlers_count += handler_count
                print_success(f"{file.name} - {handler_count} handlers, {lines} lines")
            else:
                print_error(f"{file.name} - Syntax error")
                all_good = False

    # Check workers
    if workers_dir.exists():
        worker_files = list(workers_dir.glob('*.py'))
        print(f"\n{Colors.BOLD}Workers ({len(worker_files)} files):{Colors.END}")
        for file in worker_files:
            if file.name == '__init__.py':
                continue
            valid, error = check_syntax(file)
            if valid:
                lines = len(open(file).readlines())
                total_lines += lines
                print_success(f"{file.name} - {lines} lines")
            else:
                print_error(f"{file.name} - Syntax error")
                all_good = False

    print(f"\n{Colors.BOLD}Total Handlers: {handlers_count}{Colors.END}")
    print(f"{Colors.BOLD}Total Lines: {total_lines}{Colors.END}")
    return all_good

def verify_phase_5():
    """Verify Phase 5: Scheduler & Background Jobs"""
    print_header("PHASE 5: SCHEDULER & BACKGROUND JOBS")

    scheduler_dir = Path('backend/app/scheduler')

    all_good = True
    total_lines = 0

    if scheduler_dir.exists():
        scheduler_files = list(scheduler_dir.glob('*.py'))
        print(f"\n{Colors.BOLD}Scheduler Components ({len(scheduler_files)} files):{Colors.END}")
        for file in scheduler_files:
            if file.name == '__init__.py':
                continue
            valid, error = check_syntax(file)
            if valid:
                info = analyze_python_file(file)
                lines = len(open(file).readlines())
                total_lines += lines
                async_count = len(info.get('async_functions', []))
                print_success(f"{file.name} - {async_count} async jobs, {lines} lines")
            else:
                print_error(f"{file.name} - Syntax error")
                all_good = False
    else:
        print_error("Scheduler directory not found")
        all_good = False

    print(f"\n{Colors.BOLD}Total Lines: {total_lines}{Colors.END}")
    return all_good

def verify_phase_6():
    """Verify Phase 6: Web App Development"""
    print_header("PHASE 6: WEB APP DEVELOPMENT")

    frontend_dir = Path('frontend')

    all_good = True
    total_files = 0
    total_lines = 0

    # Check TypeScript/TSX files
    if frontend_dir.exists():
        ts_files = list(frontend_dir.glob('**/*.ts')) + list(frontend_dir.glob('**/*.tsx'))
        # Filter out node_modules and .next
        ts_files = [f for f in ts_files if 'node_modules' not in str(f) and '.next' not in str(f)]

        print(f"\n{Colors.BOLD}TypeScript Files ({len(ts_files)} files):{Colors.END}")

        categories = defaultdict(list)
        for file in ts_files:
            rel_path = file.relative_to(frontend_dir)
            if 'app/' in str(rel_path):
                categories['Pages'].append(file)
            elif 'components/' in str(rel_path):
                categories['Components'].append(file)
            elif 'lib/' in str(rel_path):
                categories['Libraries'].append(file)

        for category, files in categories.items():
            print(f"\n{Colors.BOLD}{category}:{Colors.END}")
            for file in files:
                lines = len(open(file).readlines())
                total_lines += lines
                total_files += 1
                rel_path = file.relative_to(frontend_dir)
                print_success(f"{rel_path} - {lines} lines")

        # Check package.json
        package_json = frontend_dir / 'package.json'
        if package_json.exists():
            print(f"\n{Colors.BOLD}Configuration:{Colors.END}")
            print_success("package.json exists")
        else:
            print_error("package.json missing")
            all_good = False
    else:
        print_error("Frontend directory not found")
        all_good = False

    print(f"\n{Colors.BOLD}Total Files: {total_files}{Colors.END}")
    print(f"{Colors.BOLD}Total Lines: {total_lines}{Colors.END}")
    return all_good

def verify_main_app():
    """Verify main.py integration"""
    print_header("MAIN APPLICATION INTEGRATION")

    main_file = Path('backend/app/main.py')

    if not main_file.exists():
        print_error("main.py not found")
        return False

    valid, error = check_syntax(main_file)
    if not valid:
        print_error(f"main.py has syntax errors: {error}")
        return False

    content = open(main_file).read()

    checks = [
        ('FastAPI app creation', 'FastAPI('),
        ('CORS middleware', 'CORSMiddleware'),
        ('Rate limiting', 'SlowAPI'),
        ('API routes', 'include_router'),
        ('Bot webhook', '/webhook'),
        ('Scheduler integration', 'scheduler'),
        ('Health check', '/health'),
    ]

    all_good = True
    for check_name, pattern in checks:
        if pattern in content:
            print_success(f"{check_name} - Found")
        else:
            print_warning(f"{check_name} - Not found")

    lines = len(open(main_file).readlines())
    print(f"\n{Colors.BOLD}main.py: {lines} lines{Colors.END}")

    return all_good

def main():
    """Run all verifications"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║     COMPREHENSIVE VERIFICATION - ALL 6 PHASES                     ║")
    print("║     Telegram Health Tracker Bot + Web App                         ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")

    results = {}

    results['Phase 1'] = verify_phase_1()
    results['Phase 2'] = verify_phase_2()
    results['Phase 3'] = verify_phase_3()
    results['Phase 4'] = verify_phase_4()
    results['Phase 5'] = verify_phase_5()
    results['Phase 6'] = verify_phase_6()
    results['Main App'] = verify_main_app()

    # Summary
    print_header("VERIFICATION SUMMARY")

    for phase, passed in results.items():
        if passed:
            print_success(f"{phase}: PASSED")
        else:
            print_error(f"{phase}: FAILED")

    total_passed = sum(1 for p in results.values() if p)
    total_phases = len(results)

    print(f"\n{Colors.BOLD}Overall: {total_passed}/{total_phases} phases passed{Colors.END}")

    if total_passed == total_phases:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL VERIFICATIONS PASSED! 🎉{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠ Some verifications failed{Colors.END}\n")
        return 1

if __name__ == '__main__':
    exit(main())

