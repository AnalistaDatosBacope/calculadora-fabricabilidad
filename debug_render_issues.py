#!/usr/bin/env python3
"""
Script para diagnosticar problemas específicos de Render.com
"""

import os
import sys
import logging
from datetime import datetime

def check_render_configuration():
    """Verificar configuración específica de Render.com"""
    print("🔍 Diagnosticando configuración de Render.com...")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # 1. Verificar variables de entorno
    print("1️⃣ Verificando variables de entorno...")
    render_env_vars = [
        'RENDER',
        'RENDER_EXTERNAL_HOSTNAME',
        'RENDER_EXTERNAL_URL',
        'PORT',
        'PYTHON_VERSION'
    ]
    
    for var in render_env_vars:
        value = os.environ.get(var, 'NO DEFINIDA')
        print(f"   {var}: {value}")
    
    # 2. Verificar configuración de la aplicación
    print("\n2️⃣ Verificando configuración de la aplicación...")
    
    try:
        # Importar la aplicación
        import app
        
        print("   ✅ app.py se importa correctamente")
        
        # Verificar configuración de Flask
        print(f"   DEBUG: {app.app.config.get('DEBUG', 'NO DEFINIDO')}")
        print(f"   SECRET_KEY: {'DEFINIDO' if app.app.config.get('SECRET_KEY') else 'NO DEFINIDO'}")
        print(f"   UPLOAD_FOLDER: {app.app.config.get('UPLOAD_FOLDER', 'NO DEFINIDO')}")
        print(f"   DATA_CACHE_FOLDER: {app.app.config.get('DATA_CACHE_FOLDER', 'NO DEFINIDO')}")
        
        # Verificar configuraciones específicas de Render
        print(f"   PERMANENT_SESSION_LIFETIME: {app.app.config.get('PERMANENT_SESSION_LIFETIME', 'NO DEFINIDO')}")
        print(f"   SESSION_COOKIE_SECURE: {app.app.config.get('SESSION_COOKIE_SECURE', 'NO DEFINIDO')}")
        print(f"   SESSION_COOKIE_HTTPONLY: {app.app.config.get('SESSION_COOKIE_HTTPONLY', 'NO DEFINIDO')}")
        print(f"   SESSION_COOKIE_SAMESITE: {app.app.config.get('SESSION_COOKIE_SAMESITE', 'NO DEFINIDO')}")
        
    except Exception as e:
        print(f"   ❌ Error importando app.py: {e}")
        return False
    
    # 3. Verificar dependencias
    print("\n3️⃣ Verificando dependencias...")
    
    required_packages = [
        'flask',
        'flask_login',
        'flask_sqlalchemy',
        'pandas',
        'numpy',
        'openpyxl',
        'gunicorn',
        'werkzeug'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NO INSTALADO")
    
    # 4. Verificar archivos críticos
    print("\n4️⃣ Verificando archivos críticos...")
    
    critical_files = [
        'app.py',
        'requirements.txt',
        'render.yaml',
        'data_models.py',
        'calculadora_core.py',
        'file_parser.py',
        'report_generator.py'
    ]
    
    for file in critical_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - NO ENCONTRADO")
    
    # 5. Verificar estructura de carpetas
    print("\n5️⃣ Verificando estructura de carpetas...")
    
    required_folders = [
        'templates',
        'static',
        'static/css',
        'static/js',
        'uploads',
        'data_cache'
    ]
    
    for folder in required_folders:
        if os.path.exists(folder):
            print(f"   ✅ {folder}/")
        else:
            print(f"   ❌ {folder}/ - NO ENCONTRADO")
    
    # 6. Verificar permisos de escritura
    print("\n6️⃣ Verificando permisos de escritura...")
    
    writable_folders = [
        'uploads',
        'data_cache',
        'instance'
    ]
    
    for folder in writable_folders:
        if os.path.exists(folder):
            try:
                test_file = os.path.join(folder, 'test_write.tmp')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"   ✅ {folder}/ - ESCRIBIBLE")
            except Exception as e:
                print(f"   ❌ {folder}/ - NO ESCRIBIBLE: {e}")
        else:
            print(f"   ⚠️  {folder}/ - NO EXISTE")
    
    print("-" * 60)
    print("📋 Recomendaciones para Render.com:")
    print("   1. Verificar logs en Render Dashboard")
    print("   2. Asegurar que todas las dependencias estén en requirements.txt")
    print("   3. Verificar que gunicorn esté configurado correctamente")
    print("   4. Comprobar variables de entorno en Render")
    print("   5. Verificar que la aplicación se inicie sin errores")
    
    return True

def check_gunicorn_config():
    """Verificar configuración de gunicorn"""
    print("\n🔧 Verificando configuración de gunicorn...")
    
    try:
        import gunicorn
        print(f"   ✅ Gunicorn instalado: {gunicorn.__version__}")
    except ImportError:
        print("   ❌ Gunicorn NO instalado")
        return False
    
    # Verificar que gunicorn pueda importar la aplicación
    try:
        import gunicorn.app.wsgiapp
        print("   ✅ Gunicorn puede importar correctamente")
    except Exception as e:
        print(f"   ❌ Error con gunicorn: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = check_render_configuration()
    gunicorn_ok = check_gunicorn_config()
    
    if success and gunicorn_ok:
        print("\n✅ Diagnóstico completado - Configuración parece correcta")
        print("🔍 Si la aplicación sigue fallando en Render.com:")
        print("   1. Revisar logs específicos en Render Dashboard")
        print("   2. Verificar build logs para errores de dependencias")
        print("   3. Comprobar que no haya errores de sintaxis")
    else:
        print("\n❌ Se encontraron problemas en la configuración")
        print("🔧 Corrige los problemas antes de hacer deploy") 