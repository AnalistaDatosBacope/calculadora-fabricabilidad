#!/usr/bin/env python3
"""
Script para inicializar la base de datos y crear usuario admin
"""

import os
import sys

# Agregar el directorio actual al path para importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Role
from werkzeug.security import generate_password_hash

def init_database():
    """Inicializa la base de datos y crea el usuario admin"""
    
    print("🔧 Inicializando base de datos...")
    
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # Verificar si ya existe el rol admin
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                print("📝 Creando rol admin...")
                admin_role = Role(name='admin', description='Administrador del sistema')
                db.session.add(admin_role)
                db.session.commit()
                print("✅ Rol admin creado")
            else:
                print("✅ Rol admin ya existe")
            
            # Verificar si ya existe el usuario admin
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                print("📝 Creando usuario admin...")
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    password=generate_password_hash('admin123'),
                    role=admin_role
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Usuario admin creado exitosamente")
                print("   Username: admin")
                print("   Password: admin123")
            else:
                print("✅ Usuario admin ya existe")
                # Verificar si el password es correcto
                if not admin_user.check_password('admin123'):
                    print("🔧 Corrigiendo password del usuario admin...")
                    admin_user.password = generate_password_hash('admin123')
                    db.session.commit()
                    print("✅ Password corregido")
            
            # Verificar usuarios existentes
            users = User.query.all()
            print(f"📊 Usuarios en la base de datos: {len(users)}")
            for user in users:
                print(f"   - {user.username} ({user.email}) - Rol: {user.role.name}")
            
            print("\n🎉 Base de datos inicializada correctamente")
            print("💡 Ahora puedes hacer login con admin/admin123")
            
        except Exception as e:
            print(f"❌ Error al inicializar la base de datos: {e}")

if __name__ == "__main__":
    init_database() 