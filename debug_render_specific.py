#!/usr/bin/env python3
"""
Script de diagnóstico específico para Render.com
"""
import requests
import os
import sys
from pathlib import Path
import pandas as pd
import json

def test_render_specific():
    """Diagnóstico específico para problemas en Render.com"""
    
    base_url = "https://calculadora-fabricabilidad.onrender.com"
    session = requests.Session()
    
    print("🔍 Diagnóstico específico para Render.com")
    print(f"🌐 URL: {base_url}")
    print("-" * 60)
    
    # Paso 1: Verificar que la aplicación responde
    print("1️⃣ Verificando respuesta de la aplicación...")
    try:
        response = session.get(base_url)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Aplicación responde (redirección a login)")
        elif response.status_code == 200:
            print("   ✅ Aplicación responde directamente")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False
    
    # Paso 2: Login
    print("\n2️⃣ Realizando login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        if response.status_code == 302:
            print("   ✅ Login exitoso")
            # Seguir redirección
            redirect_url = response.headers.get('Location')
            if redirect_url:
                response = session.get(f"{base_url}{redirect_url}")
                print(f"   Redirección a: {redirect_url}")
        else:
            print(f"   ❌ Error en login: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    # Paso 3: Verificar cookies de sesión
    print("\n3️⃣ Verificando cookies de sesión...")
    cookies = session.cookies
    print(f"   Cookies: {dict(cookies)}")
    
    if 'session' in cookies:
        print("   ✅ Cookie de sesión presente")
    else:
        print("   ❌ Cookie de sesión no encontrada")
    
    # Paso 4: Crear archivo de prueba simple
    print("\n4️⃣ Creando archivo de prueba simple...")
    
    # Archivo de ventas simple
    sales_data = {
        'FECHA': ['2024-01-01'],
        'COD_PROD': ['A001'],
        'Descripción': ['Producto A'],
        'VENTA': [100]
    }
    sales_df = pd.DataFrame(sales_data)
    sales_df.to_excel('test_simple.xlsx', index=False)
    print("   ✅ Archivo test_simple.xlsx creado")
    
    # Paso 5: Probar carga de archivo
    print("\n5️⃣ Probando carga de archivo...")
    
    try:
        with open('test_simple.xlsx', 'rb') as f:
            files = {'sales_file': ('test_simple.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            response = session.post(base_url, files=files, allow_redirects=False)
            
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 302:
                print("   ✅ Archivo procesado (redirección)")
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    follow_response = session.get(f"{base_url}{redirect_url}")
                    print(f"   Redirección a: {redirect_url}")
                    print(f"   Status después de redirección: {follow_response.status_code}")
                    
                    # Analizar el HTML de respuesta
                    html_content = follow_response.text
                    
                    # Buscar indicadores específicos
                    indicators = [
                        ('Cargado', 'Texto "Cargado"'),
                        ('success', 'Mensaje de éxito'),
                        ('sales_loaded', 'Variable sales_loaded'),
                        ('bom_loaded', 'Variable bom_loaded'),
                        ('stock_loaded', 'Variable stock_loaded'),
                        ('cost_loaded', 'Variable cost_loaded'),
                        ('suppliers_loaded', 'Variable suppliers_loaded'),
                        ('historico_costos_loaded', 'Variable historico_costos_loaded')
                    ]
                    
                    print("\n   📊 Análisis del HTML:")
                    for indicator, description in indicators:
                        if indicator in html_content:
                            print(f"      ✅ {description}: Encontrado")
                        else:
                            print(f"      ❌ {description}: No encontrado")
                    
                    # Buscar el contexto de la plantilla
                    if 'bom_loaded' in html_content or 'stock_loaded' in html_content:
                        print("   ✅ Variables de estado encontradas en HTML")
                    else:
                        print("   ❌ Variables de estado NO encontradas en HTML")
                        
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Respuesta: {response.text[:500]}...")
                
    except Exception as e:
        print(f"   ❌ Error cargando archivo: {e}")
    
    # Paso 6: Verificar estado después de carga
    print("\n6️⃣ Verificando estado después de carga...")
    try:
        response = session.get(base_url)
        html_content = response.text
        
        # Buscar indicadores de archivos cargados
        indicators = [
            ('bom_status', 'BOM'),
            ('stock_status', 'Stock'),
            ('costs_status', 'Costos'),
            ('sales_status', 'Ventas'),
            ('suppliers_status', 'Proveedores'),
            ('historico_status', 'Histórico')
        ]
        
        print("   📊 Estado final:")
        for indicator, name in indicators:
            if indicator in html_content:
                print(f"      ✅ {name}: Encontrado en HTML")
            else:
                print(f"      ❌ {name}: No encontrado en HTML")
                
    except Exception as e:
        print(f"   ❌ Error verificando estado: {e}")
    
    # Limpiar archivo
    if os.path.exists('test_simple.xlsx'):
        os.remove('test_simple.xlsx')
        print("\n   🗑️  Archivo de prueba eliminado")
    
    print("\n✅ Diagnóstico completado")

if __name__ == "__main__":
    test_render_specific() 