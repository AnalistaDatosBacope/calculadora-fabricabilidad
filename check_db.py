#!/usr/bin/env python3
"""
Script para verificar y reparar la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Role, create_tables_and_roles
from werkzeug.security import generate_password_hash

def check_database():
    """Verificar el estado de la base de datos"""
    
    print("=== Verificando base de datos ===\n")
    
    with app.app_context():
        # Verificar si las tablas existen
        try:
            # Intentar crear las tablas
            db.create_all()
            print("✓ Tablas creadas/verificadas correctamente")
        except Exception as e:
            print(f"✗ Error al crear tablas: {e}")
            return
        
        # Verificar roles
        print("\n--- Verificando roles ---")
        roles = Role.query.all()
        if roles:
            print(f"✓ Encontrados {len(roles)} roles:")
            for role in roles:
                print(f"  - {role.name}: {role.description}")
        else:
            print("✗ No se encontraron roles")
            print("Creando roles...")
            create_tables_and_roles()
            roles = Role.query.all()
            print(f"✓ Roles creados: {len(roles)}")
        
        # Verificar usuarios
        print("\n--- Verificando usuarios ---")
        users = User.query.all()
        if users:
            print(f"✓ Encontrados {len(users)} usuarios:")
            for user in users:
                print(f"  - {user.username} ({user.email}) - Rol: {user.role.name}")
        else:
            print("✗ No se encontraron usuarios")
            print("Creando usuario admin...")
            create_tables_and_roles()
            users = User.query.all()
            print(f"✓ Usuarios creados: {len(users)}")
        
        # Verificar usuario admin específicamente
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print(f"\n✓ Usuario admin encontrado:")
            print(f"  - Username: {admin_user.username}")
            print(f"  - Email: {admin_user.email}")
            print(f"  - Rol: {admin_user.role.name}")
            print(f"  - Activo: {admin_user.is_active}")
            
            # Verificar permisos
            print(f"  - Permisos:")
            permissions = admin_user.role.get_permissions()
            for perm, value in permissions.items():
                print(f"    * {perm}: {value}")
        else:
            print("\n✗ Usuario admin no encontrado")
            print("Creando usuario admin...")
            
            # Crear usuario admin manualmente
            super_admin_role = Role.query.filter_by(name='super_admin').first()
            if super_admin_role:
                admin_user = User(
                    username='admin',
                    email='admin@sistema.com',
                    first_name='Administrador',
                    last_name='Sistema',
                    role_id=super_admin_role.id,
                    is_active=True
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Usuario admin creado exitosamente")
            else:
                print("✗ No se pudo encontrar el rol super_admin")
        
        print("\n=== Verificación completada ===")

if __name__ == "__main__":
    check_database() 