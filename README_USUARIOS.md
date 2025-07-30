# Sistema de Usuarios y Control de Acceso

## Descripción General

El sistema implementa un control de acceso granular basado en roles y permisos para proteger los datos sensibles de la aplicación.

## Roles Disponibles

### 1. Super Administrador (`super_admin`)
- **Descripción**: Administrador del sistema con acceso completo
- **Permisos**: Todos los permisos disponibles
- **Funcionalidades**: Gestión completa de usuarios, roles, y todas las funcionalidades del sistema

### 2. Administrador (`admin`)
- **Descripción**: Administrador con acceso a la mayoría de funcionalidades
- **Permisos**: Todos excepto `admin_access`
- **Funcionalidades**: Gestión de usuarios, análisis, reportes, pero sin acceso a configuración del sistema

### 3. Analista (`analyst`)
- **Descripción**: Analista con acceso a análisis y reportes
- **Permisos**: Dashboard, análisis de ventas, carga de datos, exportación, reportes, análisis de costos y demanda
- **Funcionalidades**: Análisis completo de datos y generación de reportes

### 4. Visualizador (`viewer`)
- **Descripción**: Usuario con acceso de solo lectura
- **Permisos**: Dashboard, análisis de ventas, exportación de datos
- **Funcionalidades**: Solo visualización de datos, sin capacidad de modificación

## Permisos Disponibles

| Permiso | Descripción | Roles con Acceso |
|---------|-------------|------------------|
| `dashboard_view` | Ver dashboard ejecutivo | Todos |
| `sales_analysis` | Análisis de ventas | Todos excepto viewer |
| `data_upload` | Subir archivos de datos | super_admin, admin, analyst |
| `data_export` | Exportar datos y reportes | Todos |
| `user_management` | Gestionar usuarios | super_admin, admin |
| `system_admin` | Administración del sistema | super_admin |
| `reports_generate` | Generar reportes | super_admin, admin, analyst |
| `cost_analysis` | Análisis de costos | super_admin, admin, analyst |
| `demand_analysis` | Análisis de demanda | super_admin, admin, analyst |
| `supplier_management` | Gestión de proveedores | super_admin, admin, analyst |
| `admin_access` | Acceso completo de administrador | super_admin |

## Usuario por Defecto

Al iniciar la aplicación por primera vez, se crea automáticamente un usuario super administrador:

- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Rol**: `super_admin`
- **Email**: `admin@sistema.com`

**⚠️ IMPORTANTE**: Cambia la contraseña del usuario admin después del primer inicio de sesión.

## Gestión de Usuarios

### Acceso a la Gestión
1. Inicia sesión como administrador
2. Haz clic en tu nombre en la barra superior
3. Selecciona "Gestionar Usuarios"

### Funcionalidades Disponibles

#### Crear Usuario
- Nombre de usuario (único)
- Email (único)
- Nombre y apellido
- Contraseña
- Rol asignado

#### Editar Usuario
- Modificar información personal
- Cambiar contraseña (opcional)
- Cambiar rol
- Activar/desactivar cuenta

#### Eliminar Usuario
- Confirmación requerida
- No se puede eliminar el propio usuario

### Auditoría de Actividad

El sistema registra automáticamente:
- Inicios y cierres de sesión
- Creación, edición y eliminación de usuarios
- Acceso a funcionalidades sensibles
- IP y User-Agent del navegador

## Seguridad

### Contraseñas
- Hasheadas con PBKDF2-SHA256
- No se almacenan en texto plano
- Cambio de contraseña opcional al editar usuarios

### Sesiones
- Sesiones de Flask-Login
- Limpieza automática al cerrar sesión
- Protección CSRF implícita

### Control de Acceso
- Decoradores `@permission_required()` para rutas específicas
- Decoradores `@admin_required()` para funciones administrativas
- Verificación de permisos en tiempo real

## Implementación Técnica

### Modelos de Base de Datos

#### User
- Información personal y credenciales
- Relación con Role
- Campos de auditoría (created_at, last_login)
- Estado activo/inactivo

#### Role
- Nombre y descripción
- Permisos almacenados como JSON
- Relación con usuarios

#### UserActivity
- Registro de todas las actividades
- Detalles en formato JSON
- Información de IP y User-Agent

### Decoradores Personalizados

```python
@permission_required('dashboard_view')
def api_dashboard_data():
    # Solo usuarios con permiso dashboard_view pueden acceder
    pass

@admin_required
def admin_users():
    # Solo administradores pueden acceder
    pass
```

## Migración de Datos

Si ya tienes una base de datos existente:

1. **Respaldar datos actuales**
2. **Eliminar archivo `site.db`** (si existe)
3. **Reiniciar la aplicación** - se creará la nueva estructura
4. **Crear usuarios con los roles apropiados**

## Recomendaciones de Seguridad

1. **Cambiar contraseña por defecto** del usuario admin
2. **Crear usuarios específicos** para cada persona
3. **Asignar roles mínimos** necesarios
4. **Revisar actividad** regularmente
5. **Desactivar usuarios** en lugar de eliminarlos
6. **Usar contraseñas fuertes** para todos los usuarios

## Solución de Problemas

### Usuario bloqueado
- Verificar que `is_active = True`
- Contactar al administrador

### Sin permisos para funcionalidad
- Verificar rol asignado
- Solicitar permisos al administrador

### Error de base de datos
- Verificar que `site.db` existe
- Reiniciar aplicación para recrear estructura

## Comandos Útiles

### Verificar usuarios en la base de datos
```python
from app import db, User, Role
with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"{user.username} - {user.role.name}")
```

### Crear usuario desde consola
```python
from app import db, User, Role
with app.app_context():
    role = Role.query.filter_by(name='analyst').first()
    user = User(username='nuevo_usuario', email='usuario@empresa.com', role=role)
    user.set_password('contraseña_segura')
    db.session.add(user)
    db.session.commit()
``` 