#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de carga de archivos
"""

import requests
import os
import tempfile
import pandas as pd

BASE_URL = "http://localhost:5000"

def create_test_files():
    """Crear archivos de prueba"""
    test_files = {}
    
    # Crear archivo BOM de prueba
    bom_data = {
        'COD_PROD_PADRE': ['MODELO1', 'MODELO1', 'MODELO2'],
        'COD_PROD_HIJO': ['COMP1', 'COMP2', 'COMP1'],
        'CANTIDAD_HIJO': [2, 1, 3],
        'DESCRIPCION_MODELO': ['Modelo 1', 'Modelo 1', 'Modelo 2'],
        'DESCRIPCION_ARTICULO': ['Componente 1', 'Componente 2', 'Componente 1'],
        'UNIDAD': ['PZA', 'PZA', 'PZA']
    }
    bom_df = pd.DataFrame(bom_data)
    bom_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    bom_df.to_excel(bom_file.name, index=False)
    test_files['bom_file'] = bom_file.name
    bom_file.close()
    
    # Crear archivo Stock de prueba
    stock_data = {
        'Artículo': ['COMP1', 'COMP2', 'COMP3'],
        'Existencia': [100, 50, 200]
    }
    stock_df = pd.DataFrame(stock_data)
    stock_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    stock_df.to_excel(stock_file.name, index=False)
    test_files['stock_file'] = stock_file.name
    stock_file.close()
    
    # Crear archivo Costos de prueba
    cost_data = {
        'Código': ['COMP1', 'COMP2', 'COMP3'],
        'Importe': [10.50, 25.00, 15.75]
    }
    cost_df = pd.DataFrame(cost_data)
    cost_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    cost_df.to_excel(cost_file.name, index=False)
    test_files['cost_file'] = cost_file.name
    cost_file.close()
    
    return test_files

def test_file_upload():
    """Probar la carga de archivos"""
    
    print("=== Probando carga de archivos ===\n")
    
    # Crear archivos de prueba
    test_files = create_test_files()
    
    # Primero hacer login
    print("1. Haciendo login...")
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        if response.status_code == 302:
            print("   ✓ Login exitoso (redirección)")
            # Seguir la redirección
            redirect_url = response.headers.get('Location')
            if redirect_url:
                response = session.get(f"{BASE_URL}{redirect_url}")
                print(f"   ✓ Redirección completada: {response.status_code}")
        else:
            print(f"   ✗ Error en login: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
        return
    
    # Preparar archivos para upload
    print("\n2. Preparando archivos para upload...")
    files = {}
    for file_key, file_path in test_files.items():
        with open(file_path, 'rb') as f:
            files[file_key] = (os.path.basename(file_path), f.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    # Intentar cargar archivos
    print("\n3. Intentando cargar archivos...")
    try:
        response = session.post(f"{BASE_URL}/", files=files)
        print(f"   Status Code: {response.status_code}")
        print(f"   URL después de POST: {response.url}")
        
        if response.status_code == 200:
            print("   ✓ Archivos enviados correctamente")
            
            # Verificar si hay mensajes flash
            if 'Archivo' in response.text:
                print("   ✓ Mensajes de confirmación encontrados")
            else:
                print("   ⚠ No se encontraron mensajes de confirmación")
                
        else:
            print(f"   ✗ Error en la carga: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Error al cargar archivos: {e}")
    
    # Limpiar archivos temporales
    print("\n4. Limpiando archivos temporales...")
    for file_path in test_files.values():
        try:
            os.unlink(file_path)
        except:
            pass
    
    print("\n=== Fin de prueba ===")

if __name__ == "__main__":
    test_file_upload() 