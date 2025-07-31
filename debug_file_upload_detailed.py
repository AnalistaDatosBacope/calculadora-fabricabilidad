#!/usr/bin/env python3
"""
Script de diagnóstico detallado para problemas de carga de archivos
"""
import requests
import os
import sys
from pathlib import Path
import pandas as pd
import io

def create_test_files():
    """Crear archivos de prueba válidos"""
    
    # Archivo de ventas (formato correcto)
    sales_data = {
        'FECHA': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'COD_PROD': ['A001', 'A002', 'A001'],
        'Descripción': ['Producto A', 'Producto B', 'Producto A'],
        'VENTA': [100, 150, 120]
    }
    sales_df = pd.DataFrame(sales_data)
    
    # Archivo de proveedores (formato correcto)
    suppliers_data = {
        'Artículo': ['A001', 'A002'],
        'Descripción': ['Producto A', 'Producto B'],
        'Código': ['PROV001', 'PROV002'],
        'Razón Social': ['Proveedor 1', 'Proveedor 2'],
        'Precio': [10.50, 15.75]
    }
    suppliers_df = pd.DataFrame(suppliers_data)
    
    # Archivo histórico de costos (formato correcto)
    historico_data = {
        'Artículo': ['A001', 'A002'],
        '2023': [10.00, 15.00],
        '2024': [10.50, 15.75]
    }
    historico_df = pd.DataFrame(historico_data)
    
    # Guardar archivos
    sales_df.to_excel('test_sales.xlsx', index=False)
    suppliers_df.to_excel('test_suppliers.xlsx', index=False)
    historico_df.to_excel('test_historico.xlsx', index=False)
    
    print("✅ Archivos de prueba creados:")
    print("   - test_sales.xlsx")
    print("   - test_suppliers.xlsx") 
    print("   - test_historico.xlsx")

def test_file_upload_detailed():
    """Prueba detallada de carga de archivos"""
    
    base_url = "https://calculadora-fabricabilidad.onrender.com"
    session = requests.Session()
    
    print("🔍 Iniciando diagnóstico detallado...")
    print(f"🌐 URL: {base_url}")
    print("-" * 60)
    
    # Paso 1: Login
    print("1️⃣ Realizando login...")
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
        else:
            print(f"   ❌ Error en login: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    # Paso 2: Crear archivos de prueba
    print("\n2️⃣ Creando archivos de prueba...")
    create_test_files()
    
    # Paso 3: Probar cada tipo de archivo
    print("\n3️⃣ Probando carga de archivos...")
    
    files_to_test = [
        ('sales_file', 'test_sales.xlsx', 'Ventas'),
        ('suppliers_file', 'test_suppliers.xlsx', 'Proveedores'),
        ('historico_costos_file', 'test_historico.xlsx', 'Histórico de Costos')
    ]
    
    for file_key, filename, description in files_to_test:
        print(f"\n   📁 Probando {description}...")
        
        try:
            with open(filename, 'rb') as f:
                files = {file_key: (filename, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                
                # Hacer la petición POST
                response = session.post(base_url, files=files, allow_redirects=False)
                
                print(f"      Status: {response.status_code}")
                print(f"      Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                print(f"      Content-Length: {response.headers.get('Content-Length', 'N/A')}")
                
                if response.status_code == 302:
                    print(f"      ✅ {description} procesado (redirección)")
                    # Verificar la página después de la redirección
                    redirect_url = response.headers.get('Location')
                    if redirect_url:
                        follow_response = session.get(f"{base_url}{redirect_url}")
                        print(f"      Redirección a: {redirect_url}")
                        print(f"      Status después de redirección: {follow_response.status_code}")
                        
                        # Buscar indicadores de éxito en el HTML
                        html_content = follow_response.text
                        if 'Cargado' in html_content:
                            print(f"      ✅ {description} marcado como 'Cargado'")
                        else:
                            print(f"      ⚠️  {description} no aparece como 'Cargado'")
                            
                        if 'success' in html_content.lower():
                            print(f"      ✅ Mensaje de éxito encontrado")
                        else:
                            print(f"      ⚠️  No se encontró mensaje de éxito")
                            
                elif response.status_code == 200:
                    print(f"      ✅ {description} procesado (sin redirección)")
                    # Buscar indicadores de éxito
                    html_content = response.text
                    if 'Cargado' in html_content:
                        print(f"      ✅ {description} marcado como 'Cargado'")
                    else:
                        print(f"      ⚠️  {description} no aparece como 'Cargado'")
                else:
                    print(f"      ❌ Error: {response.status_code}")
                    print(f"      Respuesta: {response.text[:500]}...")
                    
        except Exception as e:
            print(f"      ❌ Error cargando {description}: {e}")
    
    # Paso 4: Verificar estado final
    print("\n4️⃣ Verificando estado final...")
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
        
        for indicator, name in indicators:
            if indicator in html_content:
                print(f"   ✅ {name}: Encontrado en HTML")
            else:
                print(f"   ❌ {name}: No encontrado en HTML")
                
    except Exception as e:
        print(f"   ❌ Error verificando estado: {e}")
    
    # Limpiar archivos
    print("\n5️⃣ Limpiando archivos de prueba...")
    for filename in ['test_sales.xlsx', 'test_suppliers.xlsx', 'test_historico.xlsx']:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"   🗑️  Eliminado: {filename}")
    
    print("\n✅ Diagnóstico completado")

if __name__ == "__main__":
    test_file_upload_detailed() 