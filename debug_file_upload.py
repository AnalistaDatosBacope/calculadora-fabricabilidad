#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de carga de archivos
"""
import requests
import os
import sys
from pathlib import Path

def test_file_upload():
    """Prueba la carga de archivos y muestra información detallada"""
    
    # URL de la aplicación
    base_url = "https://calculadora-fabricabilidad.onrender.com"
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    print("🔍 Iniciando diagnóstico de carga de archivos...")
    print(f"🌐 URL: {base_url}")
    print("-" * 50)
    
    # Paso 1: Intentar acceder a la página principal
    print("1️⃣ Probando acceso a la página principal...")
    try:
        response = session.get(base_url)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ⚠️  Redirigido a login (esperado)")
        elif response.status_code == 200:
            print("   ✅ Página accesible")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False
    
    # Paso 2: Intentar login
    print("\n2️⃣ Probando login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✅ Login exitoso")
            # Seguir la redirección
            redirect_url = response.headers.get('Location')
            if redirect_url:
                response = session.get(f"{base_url}{redirect_url}")
                print(f"   Redirección a: {redirect_url}")
        else:
            print("   ❌ Error en login")
            print(f"   Respuesta: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"   ❌ Error en login: {e}")
        return False
    
    # Paso 3: Verificar que estamos logueados
    print("\n3️⃣ Verificando sesión...")
    try:
        response = session.get(base_url)
        if response.status_code == 200:
            print("   ✅ Sesión activa")
        else:
            print(f"   ❌ Error de sesión: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error verificando sesión: {e}")
        return False
    
    # Paso 4: Crear archivos de prueba
    print("\n4️⃣ Creando archivos de prueba...")
    
    # Crear archivo de ventas de prueba
    sales_content = """FECHA	COD_PROD	Descripción	VENTA
2024-01-01	A001	Producto A	100
2024-01-02	A002	Producto B	150
2024-01-03	A001	Producto A	120"""
    
    with open('test_sales.xlsx', 'w', encoding='utf-8') as f:
        f.write(sales_content)
    
    # Crear archivo de proveedores de prueba
    suppliers_content = """Artículo	Descripción	Código	Razón Social	Precio
A001	Producto A	PROV001	Proveedor 1	10.50
A002	Producto B	PROV002	Proveedor 2	15.75"""
    
    with open('test_suppliers.xlsx', 'w', encoding='utf-8') as f:
        f.write(suppliers_content)
    
    # Crear archivo histórico de costos de prueba
    historico_content = """Artículo	2023	2024
A001	10.00	10.50
A002	15.00	15.75"""
    
    with open('test_historico.xlsx', 'w', encoding='utf-8') as f:
        f.write(historico_content)
    
    print("   ✅ Archivos de prueba creados")
    
    # Paso 5: Probar carga de archivos
    print("\n5️⃣ Probando carga de archivos...")
    
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
                
                response = session.post(base_url, files=files, allow_redirects=False)
                
                print(f"      Status: {response.status_code}")
                print(f"      Headers: {dict(response.headers)}")
                
                if response.status_code == 302:
                    print(f"      ✅ {description} procesado (redirección)")
                elif response.status_code == 200:
                    print(f"      ✅ {description} procesado")
                else:
                    print(f"      ❌ Error: {response.status_code}")
                    print(f"      Respuesta: {response.text[:300]}...")
                    
        except Exception as e:
            print(f"      ❌ Error cargando {description}: {e}")
    
    # Limpiar archivos de prueba
    print("\n6️⃣ Limpiando archivos de prueba...")
    for filename in ['test_sales.xlsx', 'test_suppliers.xlsx', 'test_historico.xlsx']:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"   🗑️  Eliminado: {filename}")
    
    print("\n✅ Diagnóstico completado")
    return True

if __name__ == "__main__":
    test_file_upload() 