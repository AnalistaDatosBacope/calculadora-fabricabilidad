#!/usr/bin/env python3
"""
Script para verificar el estado de la aplicación web en Render.com
"""

import requests
import time
import json
from datetime import datetime

def check_web_status():
    """Verificar el estado de la aplicación web"""
    url = "https://calculadora-fabricabilidad.onrender.com/"
    
    print(f"🔍 Verificando estado de la aplicación web...")
    print(f"📡 URL: {url}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    try:
        # Verificar respuesta básica
        print("1️⃣ Verificando respuesta básica...")
        response = requests.get(url, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("   ✅ La aplicación responde correctamente")
            
            # Verificar si es la página de login
            if "login" in response.text.lower() or "iniciar sesión" in response.text.lower():
                print("   📝 Detectada página de login - aplicación funcionando")
            else:
                print("   ⚠️  No se detectó página de login - verificar contenido")
                
        elif response.status_code == 500:
            print("   ❌ Error 500 - Error interno del servidor")
            print("   🔧 Posibles causas:")
            print("      - Error en el código de la aplicación")
            print("      - Problema con la base de datos")
            print("      - Error en las dependencias")
            
        elif response.status_code == 404:
            print("   ❌ Error 404 - Página no encontrada")
            
        elif response.status_code == 502:
            print("   ❌ Error 502 - Bad Gateway")
            print("   🔧 Posibles causas:")
            print("      - La aplicación no se inició correctamente")
            print("      - Problema con gunicorn")
            print("      - Error en el build")
            
        else:
            print(f"   ⚠️  Status code inesperado: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ⏰ Timeout - La aplicación no responde en 30 segundos")
        print("   🔧 Posibles causas:")
        print("      - La aplicación está iniciando (cold start)")
        print("      - Problema de conectividad")
        print("      - La aplicación está caída")
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Error de conexión")
        print("   🔧 Posibles causas:")
        print("      - La aplicación no está desplegada")
        print("      - Problema de DNS")
        print("      - La aplicación está caída")
        
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
    
    print("-" * 60)
    
    # Verificar endpoints específicos
    print("2️⃣ Verificando endpoints específicos...")
    
    endpoints = [
        ("/login", "Página de login"),
        ("/register", "Página de registro"),
        ("/api/models", "API de modelos"),
    ]
    
    for endpoint, description in endpoints:
        try:
            full_url = url.rstrip('/') + endpoint
            response = requests.get(full_url, timeout=10)
            status = "✅" if response.status_code in [200, 302, 401] else "❌"
            print(f"   {status} {endpoint} ({description}): {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} ({description}): Error - {e}")
    
    print("-" * 60)
    print("3️⃣ Recomendaciones:")
    print("   📋 Si hay errores:")
    print("      1. Verificar logs en Render.com Dashboard")
    print("      2. Revisar build logs para errores de dependencias")
    print("      3. Verificar configuración de variables de entorno")
    print("      4. Comprobar que gunicorn esté en requirements.txt")
    print("      5. Verificar que app.py tenga la configuración correcta")
    
    print("\n   🔗 Enlaces útiles:")
    print("      - Dashboard Render.com: https://dashboard.render.com")
    print("      - Logs de la aplicación: https://dashboard.render.com/web/calculadora-fabricabilidad")
    print("      - Documentación Render.com: https://render.com/docs")

if __name__ == "__main__":
    check_web_status() 