# Calculadora de Fabricabilidad - Sistema de Gestión

## Descripción

Sistema completo de análisis de fabricabilidad con control de acceso granular y gestión de usuarios. Permite analizar costos, demanda, estacionalidad de ventas y generar reportes detallados.

## Características Principales

### 🔐 **Sistema de Usuarios y Control de Acceso**
- **4 Roles de Usuario**: Super Admin, Admin, Analista, Visualizador
- **Permisos Granulares**: Control específico por funcionalidad
- **Auditoría Completa**: Registro de todas las actividades
- **Gestión de Usuarios**: Crear, editar, activar/desactivar usuarios

### 📊 **Análisis Avanzado**
- **Dashboard Ejecutivo**: KPIs en tiempo real
- **Análisis de Estacionalidad**: Patrones temporales en ventas
- **Predicciones**: Modelo de forecasting con métricas de precisión
- **Análisis de Costos**: Histórico y proyecciones
- **Gestión de Proveedores**: Comparación y optimización

### 📈 **Reportes y Exportación**
- **Reportes PDF/Excel**: Generación automática
- **Exportación de Datos**: Múltiples formatos
- **Gráficos Interactivos**: Chart.js con tema oscuro

## Instalación

### Requisitos
- Python 3.8+
- pip

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd calculadora-fabricabilidad
```

2. **Crear entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
python app.py
```

5. **Acceder al sistema**
- URL: `http://localhost:5000`
- Usuario: `admin`
- Contraseña: `admin123`

## Estructura del Proyecto

```
├── app.py                 # Aplicación principal Flask
├── data_models.py         # Modelos de datos
├── calculadora_core.py    # Lógica de cálculo
├── file_parser.py         # Parser de archivos
├── report_generator.py    # Generador de reportes
├── templates/             # Plantillas HTML
│   ├── admin/            # Plantillas de administración
│   └── ...
├── static/               # Archivos estáticos
│   ├── css/
│   └── js/
├── requirements.txt       # Dependencias Python
├── README.md            # Este archivo
└── README_USUARIOS.md   # Documentación del sistema de usuarios
```

## Sistema de Usuarios

### Roles Disponibles

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **Super Admin** | Administrador completo | Todos los permisos |
| **Admin** | Administrador general | Gestión de usuarios + análisis |
| **Analista** | Analista de datos | Análisis y reportes |
| **Visualizador** | Solo lectura | Dashboard y exportación |

### Usuario por Defecto
- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Rol**: Super Administrador

⚠️ **IMPORTANTE**: Cambia la contraseña del admin después del primer acceso.

## Funcionalidades

### 📁 **Carga de Archivos**
- Soporte para Excel (.xlsx, .xls)
- Validación automática de formatos
- Caché de datos para sesiones

### 📊 **Dashboard Ejecutivo**
- KPIs en tiempo real
- Gráficos de tendencias
- Alertas automáticas
- Análisis de estacionalidad

### 🔍 **Análisis Avanzado**
- **Estacionalidad**: Identificación de patrones temporales
- **Predicciones**: Modelo de forecasting con intervalos de confianza
- **Costos**: Análisis histórico y proyecciones
- **Demanda**: Proyecciones basadas en datos históricos

### 👥 **Gestión de Usuarios**
- Crear/editar/eliminar usuarios
- Asignar roles y permisos
- Activar/desactivar cuentas
- Auditoría de actividades

## Seguridad

### Contraseñas
- Hasheadas con PBKDF2-SHA256
- No se almacenan en texto plano
- Cambio opcional al editar usuarios

### Control de Acceso
- Decoradores de permisos personalizados
- Verificación en tiempo real
- Protección CSRF implícita

### Auditoría
- Registro de todas las actividades
- IP y User-Agent del navegador
- Timestamp de cada acción

## Despliegue

### Desarrollo Local
```bash
python app.py
```

### Producción
1. Configurar variables de entorno
2. Usar servidor WSGI (Gunicorn, uWSGI)
3. Configurar proxy reverso (Nginx)
4. Configurar SSL/TLS

## Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte técnico o preguntas:
- Crear un Issue en GitHub
- Revisar la documentación en `README_USUARIOS.md`
- Consultar los logs en `debug.log`

## Changelog

### v2.0.0
- ✅ Sistema completo de usuarios y control de acceso
- ✅ Auditoría de actividades
- ✅ Análisis de estacionalidad y predicciones
- ✅ Dashboard ejecutivo mejorado
- ✅ Gestión de usuarios desde interfaz web

### v1.0.0
- ✅ Funcionalidades básicas de análisis
- ✅ Carga de archivos
=======
# Calculadora de Fabricabilidad - Sistema de Gestión

## Descripción

Sistema completo de análisis de fabricabilidad con control de acceso granular y gestión de usuarios. Permite analizar costos, demanda, estacionalidad de ventas y generar reportes detallados.

## Características Principales

### 🔐 **Sistema de Usuarios y Control de Acceso**
- **4 Roles de Usuario**: Super Admin, Admin, Analista, Visualizador
- **Permisos Granulares**: Control específico por funcionalidad
- **Auditoría Completa**: Registro de todas las actividades
- **Gestión de Usuarios**: Crear, editar, activar/desactivar usuarios

### 📊 **Análisis Avanzado**
- **Dashboard Ejecutivo**: KPIs en tiempo real
- **Análisis de Estacionalidad**: Patrones temporales en ventas
- **Predicciones**: Modelo de forecasting con métricas de precisión
- **Análisis de Costos**: Histórico y proyecciones
- **Gestión de Proveedores**: Comparación y optimización

### 📈 **Reportes y Exportación**
- **Reportes PDF/Excel**: Generación automática
- **Exportación de Datos**: Múltiples formatos
- **Gráficos Interactivos**: Chart.js con tema oscuro

## Instalación

### Requisitos
- Python 3.8+
- pip

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd calculadora-fabricabilidad
```

2. **Crear entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
python app.py
```

5. **Acceder al sistema**
- URL: `http://localhost:5000`
- Usuario: `admin`
- Contraseña: `admin123`

## Estructura del Proyecto

```
├── app.py                 # Aplicación principal Flask
├── data_models.py         # Modelos de datos
├── calculadora_core.py    # Lógica de cálculo
├── file_parser.py         # Parser de archivos
├── report_generator.py    # Generador de reportes
├── templates/             # Plantillas HTML
│   ├── admin/            # Plantillas de administración
│   └── ...
├── static/               # Archivos estáticos
│   ├── css/
│   └── js/
├── requirements.txt       # Dependencias Python
├── README.md            # Este archivo
└── README_USUARIOS.md   # Documentación del sistema de usuarios
```

## Sistema de Usuarios

### Roles Disponibles

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **Super Admin** | Administrador completo | Todos los permisos |
| **Admin** | Administrador general | Gestión de usuarios + análisis |
| **Analista** | Analista de datos | Análisis y reportes |
| **Visualizador** | Solo lectura | Dashboard y exportación |

### Usuario por Defecto
- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Rol**: Super Administrador

⚠️ **IMPORTANTE**: Cambia la contraseña del admin después del primer acceso.

## Funcionalidades

### 📁 **Carga de Archivos**
- Soporte para Excel (.xlsx, .xls)
- Validación automática de formatos
- Caché de datos para sesiones

### 📊 **Dashboard Ejecutivo**
- KPIs en tiempo real
- Gráficos de tendencias
- Alertas automáticas
- Análisis de estacionalidad

### 🔍 **Análisis Avanzado**
- **Estacionalidad**: Identificación de patrones temporales
- **Predicciones**: Modelo de forecasting con intervalos de confianza
- **Costos**: Análisis histórico y proyecciones
- **Demanda**: Proyecciones basadas en datos históricos

### 👥 **Gestión de Usuarios**
- Crear/editar/eliminar usuarios
- Asignar roles y permisos
- Activar/desactivar cuentas
- Auditoría de actividades

## Seguridad

### Contraseñas
- Hasheadas con PBKDF2-SHA256
- No se almacenan en texto plano
- Cambio opcional al editar usuarios

### Control de Acceso
- Decoradores de permisos personalizados
- Verificación en tiempo real
- Protección CSRF implícita

### Auditoría
- Registro de todas las actividades
- IP y User-Agent del navegador
- Timestamp de cada acción

## Despliegue

### Desarrollo Local
```bash
python app.py
```

### Producción
1. Configurar variables de entorno
2. Usar servidor WSGI (Gunicorn, uWSGI)
3. Configurar proxy reverso (Nginx)
4. Configurar SSL/TLS

## Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte técnico o preguntas:
- Crear un Issue en GitHub
- Revisar la documentación en `README_USUARIOS.md`
- Consultar los logs en `debug.log`

## Changelog

### v2.0.0
- ✅ Sistema completo de usuarios y control de acceso
- ✅ Auditoría de actividades
- ✅ Análisis de estacionalidad y predicciones
- ✅ Dashboard ejecutivo mejorado
- ✅ Gestión de usuarios desde interfaz web

### v1.0.0
- ✅ Funcionalidades básicas de análisis
- ✅ Carga de archivos
- ✅ Generación de reportes 