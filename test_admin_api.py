#!/usr/bin/env python3
"""
Script de prueba para verificar las API endpoints de administración
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_admin_apis():
    """Probar las API endpoints de administración"""
    
    print("=== Probando API endpoints de administración ===\n")
    
    # 1. Probar endpoint de usuarios
    print("1. Probando /api/admin/users...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', False)}")
            print(f"   Users count: {len(data.get('users', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # 2. Probar endpoint de roles
    print("2. Probando /api/admin/roles...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/roles")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', False)}")
            print(f"   Roles count: {len(data.get('roles', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # 3. Probar endpoint de actividad
    print("3. Probando /api/admin/activity...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/activity")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', False)}")
            print(f"   Activities count: {len(data.get('activities', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Fin de pruebas ===")

if __name__ == "__main__":
    test_admin_apis() 