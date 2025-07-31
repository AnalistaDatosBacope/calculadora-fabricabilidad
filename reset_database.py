#!/usr/bin/env python3
"""
Script para resetear la base de datos y recrear el usuario admin
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path para importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Role, User, create_tables_and_roles

def reset_database():
    """Resetea la base de datos y recrea las tablas y roles"""
    
    print("=== RESETEANDO BASE DE DATOS ===")
    
    # Verificar si existe la base de datos
    db_path = os.path.join('instance', 'site.db')
    if os.path.exists(db_path):
        print(f"Eliminando base de datos existente: {db_path}")
        os.remove(db_path)
    
    with app.app_context():
        print("Creando tablas...")
        db.create_all()
        
        print("Creando roles y usuarios...")
        create_tables_and_roles()
        
        # Verificar que el usuario admin existe
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print("✅ Usuario admin creado exitosamente")
            print(f"   Username: {admin_user.username}")
            print(f"   Role: {admin_user.role.name}")
            print(f"   Permissions: {admin_user.role.permissions}")
        else:
            print("❌ Error: Usuario admin no encontrado")
            
        # Verificar roles
        roles = Role.query.all()
        print(f"Roles creados: {[role.name for role in roles]}")
        
        # Verificar usuarios
        users = User.query.all()
        print(f"Usuarios creados: {[user.username for user in users]}")

if __name__ == "__main__":
    reset_database()
    print("\n=== BASE DE DATOS RESETEADA ===")
    print("Ahora puedes ejecutar la aplicación y hacer login con:")
    print("Username: admin")
    print("Password: admin123") 