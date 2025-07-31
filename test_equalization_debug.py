#!/usr/bin/env python3
"""
Script de prueba para diagnosticar el problema del equilibrado de stock
"""

import requests
import json
import sys

def login_and_get_session():
    """Inicia sesión y obtiene la sesión"""
    
    base_url = "http://localhost:5000"
    
    # Datos de login
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    print("=== INICIANDO SESIÓN ===")
    print(f"URL: {base_url}/login")
    print(f"Datos de login: {login_data}")
    
    try:
        # Crear sesión
        session = requests.Session()
        
        # Hacer login
        response = session.post(
            f"{base_url}/login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"URL después del login: {response.url}")
        
        if response.status_code == 200 and '/login' not in response.url:
            print("✅ Login exitoso")
            return session
        else:
            print("❌ Login falló")
            print(f"Content: {response.text[:500]}...")
            return None
            
    except Exception as e:
        print(f"ERROR en login: {e}")
        return None

def test_equalization_endpoint(session):
    """Prueba el endpoint de equilibrado de stock"""
    
    # URL base (ajustar según donde esté corriendo la app)
    base_url = "http://localhost:5000"
    
    # Datos de prueba
    test_data = {
        'selected_models_equalization': json.dumps(['Modelo1', 'Modelo2']),
        'start_date_equalization': '2024-01-01',
        'end_date_equalization': '2024-12-31'
    }
    
    print("\n=== PRUEBA DE EQUILIBRADO DE STOCK ===")
    print(f"URL: {base_url}/calculate_stock_equalization")
    print(f"Datos enviados: {test_data}")
    print(f"JSON string: '{test_data['selected_models_equalization']}'")
    
    try:
        # Hacer la petición POST con la sesión autenticada
        response = session.post(
            f"{base_url}/calculate_stock_equalization",
            data=test_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"\n=== RESPUESTA ===")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"JSON Response: {json_response}")
            except json.JSONDecodeError as e:
                print(f"Error decodificando JSON de respuesta: {e}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def test_models_api(session):
    """Prueba el endpoint de modelos"""
    
    base_url = "http://localhost:5000"
    
    print("\n=== PRUEBA DE API DE MODELOS ===")
    print(f"URL: {base_url}/api/models")
    
    try:
        response = session.get(f"{base_url}/api/models")
        print(f"Status Code: {response.status_code}")
        print(f"Content: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Modelos disponibles: {data.get('models', [])}")
            except json.JSONDecodeError as e:
                print(f"Error decodificando JSON: {e}")
                
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print("Iniciando pruebas de diagnóstico...")
    
    # Iniciar sesión
    session = login_and_get_session()
    
    if session:
        test_models_api(session)
        test_equalization_endpoint(session)
    else:
        print("❌ No se pudo iniciar sesión. Abortando pruebas.")
    
    print("\n=== FIN DE PRUEBAS ===") 