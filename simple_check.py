#!/usr/bin/env python3
"""
Script simple para verificar la base de datos
"""

import sqlite3
import os

def check_simple():
    """Verificación simple de la base de datos"""
    
    print("=== Verificación simple de la base de datos ===\n")
    
    db_path = "instance/site.db"
    
    if not os.path.exists(db_path):
        print(f"✗ Base de datos no encontrada en {db_path}")
        return
    
    print(f"✓ Base de datos encontrada: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n--- Tablas encontradas ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Verificar usuarios
        try:
            cursor.execute("SELECT username, email, role_id FROM user;")
            users = cursor.fetchall()
            print(f"\n--- Usuarios encontrados ({len(users)}):")
            for user in users:
                print(f"  - {user[0]} ({user[1]}) - Rol ID: {user[2]}")
        except Exception as e:
            print(f"\n✗ Error al consultar usuarios: {e}")
        
        # Verificar roles
        try:
            cursor.execute("SELECT name, description FROM role;")
            roles = cursor.fetchall()
            print(f"\n--- Roles encontrados ({len(roles)}):")
            for role in roles:
                print(f"  - {role[0]}: {role[1]}")
        except Exception as e:
            print(f"\n✗ Error al consultar roles: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Error al conectar con la base de datos: {e}")
    
    print("\n=== Verificación completada ===")

if __name__ == "__main__":
    check_simple() 