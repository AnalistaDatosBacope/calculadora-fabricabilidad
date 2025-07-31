from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, make_response
import os, pandas as pd, pickle, sys, uuid, calendar, logging
from datetime import datetime, timedelta # Importar datetime y timedelta para parsear fechas y obtener el año actual
import json # Importar la librería json
from dataclasses import asdict # Importar asdict para convertir dataclasses a diccionarios
import numpy as np # Importar numpy para análisis de estacionalidad

# Importaciones de tus módulos existentes
from file_parser import FileParser
from calculadora_core import CalculadoraCore
from report_generator import ReportGenerator

# --- NUEVAS IMPORTACIONES PARA AUTENTICACIÓN Y BASE DE DATOS ---
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash # Para hashear contraseñas

# Importa las clases de data_models para poder referenciarlas
from data_models import DemandProjectionResult, IndividualCalculationResult, LotCalculationResult, ComponentDemandDetail, EqualizationComponentSummary, EqualizationResult, SupplierItem, ModelFullCostResult, PurchaseSuggestion # Asegúrate de importar todas las clases que uses directamente

app = Flask(__name__)
# Es CRÍTICO que esta clave sea muy segura y no esté hardcodeada en producción.
# ¡Cámbiala por una cadena aleatoria y compleja!
app.secret_key = 'Laprida2375' # Usando la clave que me proporcionaste

# Configuración de sesiones para Render.com
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = True  # Para HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_CACHE_FOLDER'] = 'data_cache'
app.config['REPORTS_FOLDER'] = 'reports' # Asegúrate de que esta carpeta exista

# --- NUEVA CONFIGURACIÓN DE BASE DE DATOS SQLITE ---
# 'sqlite:///site.db' creará un archivo de base de datos llamado site.db en la raíz de tu proyecto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Deshabilita el seguimiento de modificaciones para reducir la sobrecarga

db = SQLAlchemy(app) # Inicializa la instancia de SQLAlchemy
login_manager = LoginManager(app) # Inicializa el gestor de login
login_manager.login_view = 'login' # La vista a la que se redirige si se intenta acceder a una ruta protegida sin autenticar

# Asegurarse de que las carpetas existan
for folder in [app.config['UPLOAD_FOLDER'], app.config['DATA_CACHE_FOLDER'], app.config['REPORTS_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Crear carpeta para sesiones de archivos
session_folder = 'flask_session'
if not os.path.exists(session_folder):
    os.makedirs(session_folder)
app.config['SESSION_FILE_DIR'] = session_folder

# Removido SESSION_SIZE_LIMIT ya que ahora siempre se guardarán en archivo

# --- MODELOS DE BASE DE DATOS PARA USUARIOS Y ROLES ---
# Sistema mejorado de roles y permisos

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text)  # JSON string con permisos específicos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_permissions(self):
        """Retorna los permisos como diccionario"""
        if self.permissions:
            return json.loads(self.permissions)
        return {}
    
    def has_permission(self, permission):
        """Verifica si el rol tiene un permiso específico"""
        perms = self.get_permissions()
        return perms.get(permission, False)
    
    def __repr__(self):
        return f"Role('{self.name}')"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref='users', lazy=True)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Métodos para manejar contraseñas
    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def has_permission(self, permission):
        """Verifica si el usuario tiene un permiso específico"""
        return self.role.has_permission(permission)
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def __repr__(self):
        return f"User('{self.username}', '{self.role.name}')"

class UserActivity(db.Model):
    """Modelo para registrar actividad de usuarios"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='activities')
    action = db.Column(db.String(100), nullable=False)  # login, logout, data_access, etc.
    details = db.Column(db.Text)  # JSON con detalles adicionales
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"UserActivity('{self.action}', '{self.timestamp}')"

class UserFileStatus(db.Model):
    """Modelo para almacenar el estado de archivos cargados por usuario"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='file_status')
    file_type = db.Column(db.String(50), nullable=False)  # bom, stock, costs, sales, suppliers, historico
    file_path = db.Column(db.String(500), nullable=False)  # Ruta del archivo guardado
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"UserFileStatus('{self.file_type}', '{self.uploaded_at}')"

# --- FUNCIÓN DE CARGA DE USUARIO PARA FLASK-LOGIN ---
# Esta función es requerida por Flask-Login para recargar el usuario desde la sesión
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- FILTROS PERSONALIZADOS PARA JINJA2 ---
@app.template_filter('from_json')
def from_json(value):
    """Filtro para convertir JSON string a diccionario en templates"""
    try:
        return json.loads(value)
    except:
        return {}

# --- FUNCIONES PARA MANEJO DE PERMISOS ---
def permission_required(permission):
    """Decorador para verificar permisos específicos"""
    def decorator(f):
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                flash('No tienes permisos para acceder a esta funcionalidad.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

def admin_required(f):
    """Decorador para verificar que el usuario sea administrador"""
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.has_permission('admin_access'):
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def log_activity(action, details=None):
    """Registra actividad del usuario en la base de datos"""
    if current_user.is_authenticated:
        try:
            activity = UserActivity(
                user_id=current_user.id,
                action=action,
                details=json.dumps(details) if details else None,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(activity)
            db.session.commit()
        except Exception as e:
            logging.error(f"Error logging activity: {e}")

def make_session_permanent():
    """Hace la sesión permanente para persistir en Render.com"""
    session.permanent = True
    session.modified = True

def get_loaded_files_status():
    """Retorna el estado de los archivos cargados en la sesión"""
    calculadora_data = session.get('calculadora_core', {})
    return {
        'bom_loaded': 'boms' in calculadora_data,
        'stock_loaded': 'stock' in calculadora_data,
        'cost_loaded': 'costs' in calculadora_data,
        'sales_loaded': 'sales_df' in calculadora_data,
        'suppliers_loaded': 'suppliers_df' in calculadora_data,
        'historico_costos_loaded': 'historico_costos_df' in calculadora_data
    }

def save_file_status_to_db(file_type, file_path):
    """Guarda el estado de un archivo cargado en la base de datos"""
    if current_user.is_authenticated:
        try:
            # Eliminar registro anterior si existe
            UserFileStatus.query.filter_by(
                user_id=current_user.id, 
                file_type=file_type
            ).delete()
            
            # Crear nuevo registro
            file_status = UserFileStatus(
                user_id=current_user.id,
                file_type=file_type,
                file_path=file_path
            )
            db.session.add(file_status)
            db.session.commit()
            logging.info(f"Archivo {file_type} guardado en DB para usuario {current_user.id}")
        except Exception as e:
            logging.error(f"Error guardando estado de archivo en DB: {e}")

def get_file_status_from_db():
    """Obtiene el estado de archivos cargados desde la base de datos"""
    if not current_user.is_authenticated:
        return {}
    
    try:
        file_statuses = UserFileStatus.query.filter_by(user_id=current_user.id).all()
        status = {}
        for fs in file_statuses:
            if os.path.exists(fs.file_path):
                status[f"{fs.file_type}_loaded"] = True
                status[f"{fs.file_type}_path"] = fs.file_path
            else:
                # Si el archivo no existe, eliminar el registro
                db.session.delete(fs)
        db.session.commit()
        return status
    except Exception as e:
        logging.error(f"Error obteniendo estado de archivos desde DB: {e}")
        return {}

# --- PERMISOS DEFINIDOS ---
PERMISSIONS = {
    'dashboard_view': 'Ver dashboard ejecutivo',
    'sales_analysis': 'Análisis de ventas',
    'data_upload': 'Subir archivos de datos',
    'data_export': 'Exportar datos y reportes',
    'user_management': 'Gestionar usuarios',
    'system_admin': 'Administración del sistema',
    'reports_generate': 'Generar reportes',
    'cost_analysis': 'Análisis de costos',
    'demand_analysis': 'Análisis de demanda',
    'supplier_management': 'Gestión de proveedores',
    'admin_access': 'Acceso completo de administrador'
}

# --- Creación de la base de datos y roles/usuario iniciales ---
def create_tables_and_roles():
    db.create_all() # Crea todas las tablas definidas por db.Model

    # Definir roles con permisos específicos
    roles_data = {
        'super_admin': {
            'description': 'Administrador del sistema con acceso completo',
            'permissions': {
                'dashboard_view': True,
                'sales_analysis': True,
                'data_upload': True,
                'data_export': True,
                'user_management': True,
                'system_admin': True,
                'reports_generate': True,
                'cost_analysis': True,
                'demand_analysis': True,
                'supplier_management': True,
                'admin_access': True
            }
        },
        'admin': {
            'description': 'Administrador con acceso a la mayoría de funcionalidades',
            'permissions': {
                'dashboard_view': True,
                'sales_analysis': True,
                'data_upload': True,
                'data_export': True,
                'user_management': True,
                'reports_generate': True,
                'cost_analysis': True,
                'demand_analysis': True,
                'supplier_management': True,
                'admin_access': False
            }
        },
        'analyst': {
            'description': 'Analista con acceso a análisis y reportes',
            'permissions': {
                'dashboard_view': True,
                'sales_analysis': True,
                'data_upload': True,
                'data_export': True,
                'reports_generate': True,
                'cost_analysis': True,
                'demand_analysis': True,
                'supplier_management': True,
                'admin_access': False
            }
        },
        'viewer': {
            'description': 'Usuario con acceso de solo lectura',
            'permissions': {
                'dashboard_view': True,
                'sales_analysis': True,
                'data_export': True,
                'admin_access': False
            }
        }
    }

    # Crear roles si no existen
    for role_name, role_data in roles_data.items():
        if not Role.query.filter_by(name=role_name).first():
            role = Role(
                name=role_name,
                description=role_data['description'],
                permissions=json.dumps(role_data['permissions'])
            )
            db.session.add(role)
    
    db.session.commit()

    # Crear usuario super administrador por defecto si no existe
    if not User.query.filter_by(username='admin').first():
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
            admin_user.set_password('admin123')  # Contraseña por defecto
            db.session.add(admin_user)
            db.session.commit()
            logging.info("Usuario administrador creado: admin/admin123")
            print("¡POR FAVOR, CAMBIA ESTA CONTRASEÑA INMEDIATAMENTE DESPUÉS DE INICIAR SESIÓN POR PRIMERA VEZ!")

# --- FUNCIONES AUXILIARES (EXISTENTES) ---
def get_core_instance():
    calculadora_data_raw = session.get('calculadora_core', {})
    if not calculadora_data_raw: return None
    loaded_data = {}
    for key, value in calculadora_data_raw.items():
        if isinstance(value, str) and (value.endswith('.feather') or value.endswith('.pkl')):
            try:
                if os.path.exists(value):
                    if value.endswith('.feather'): loaded_data[key] = pd.read_feather(value)
                    elif value.endswith('.pkl'):
                        with open(value, 'rb') as f: loaded_data[key] = pickle.load(f)
                else:
                    flash(f"Error: El archivo cacheado {value} no fue encontrado.", "danger"); return None
            except Exception as e:
                flash(f"Error crítico al leer el archivo de datos {value}: {e}", "danger"); return None
        else: loaded_data[key] = value
    return CalculadoraCore(loaded_data)

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # Si el usuario ya está logueado, redirigir al inicio
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user) # Inicia sesión el usuario
            
            # Hacer la sesión permanente para Render.com
            make_session_permanent()
            
            # Actualizar último login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Registrar actividad
            log_activity('login', {'username': username})
            
            flash(f'¡Bienvenido, {user.get_full_name()}!', 'success')
            next_page = request.args.get('next') # Redirige a la página que intentaba acceder antes del login
            return redirect(next_page or url_for('index'))
        elif user and not user.is_active:
            flash('Tu cuenta está desactivada. Contacta al administrador.', 'error')
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html', title='Iniciar Sesión')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Por ahora, permitimos que cualquiera se registre como 'viewer'.
    # En una aplicación real, solo los admins deberían poder crear usuarios o tener un proceso de aprobación.
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ese nombre de usuario ya existe. Por favor, elige otro.', 'warning')
        else:
            viewer_role = Role.query.filter_by(name='viewer').first()
            if viewer_role:
                new_user = User(username=username, role=viewer_role)
                new_user.set_password(password) # Hashea la contraseña
                db.session.add(new_user)
                db.session.commit()
                flash('¡Tu cuenta ha sido creada! Ahora puedes iniciar sesión.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error al crear usuario: Rol "viewer" no encontrado.', 'danger')
    return render_template('register.html', title='Registrarse')

@app.route('/logout')
@login_required # Solo usuarios logueados pueden cerrar sesión
def logout():
    # Registrar actividad antes de cerrar sesión
    log_activity('logout', {'username': current_user.username})
    
    logout_user() # Cierra la sesión del usuario
    session.clear() # Limpia la sesión de Flask (incluyendo datos cacheados)
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('index'))

# --- RUTAS EXISTENTES (CON PROTECCIÓN DE LOGIN Y MEJORA DE ERRORES DE ARCHIVO) ---

@app.route('/', methods=['GET', 'POST'])
@login_required # Requiere que el usuario esté logueado para acceder a la página principal
def index():
    """Página principal de la aplicación"""
    # Hacer la sesión permanente para Render.com
    make_session_permanent()
    
    # Obtener el parámetro section para activar una pestaña específica
    section = request.args.get('section', 'dashboard')
    
    # Registrar actividad
    log_activity('page_access', {'page': 'index', 'section': section})
    
    if request.method == 'POST':
        # Verificar permisos para carga de archivos
        if not current_user.has_permission('data_upload'):
            flash('No tienes permisos para cargar archivos.', 'danger')
            return redirect(url_for('index'))
            
        logging.info(f"DEBUG: Request method is POST.")
        logging.info(f"DEBUG: request.files content: {request.files}")
        # Asegurarse de que la sesión tenga un ID si no lo tiene (para el cacheo de archivos)
        if 'session_id' not in session: session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
        logging.info(f"DEBUG: Session ID: {session_id}")

        parser = FileParser(app.config['UPLOAD_FOLDER'])
        session_data = session.get('calculadora_core', {})

        files_to_process = {
            'bom_file': 'boms',
            'stock_file': 'stock',
            'lot_file': 'lots',
            'cost_file': 'costs',
            'sales_file': 'sales_df',
            'suppliers_file': 'suppliers_df' # Nuevo archivo de proveedores
        }

        # Procesar archivos estándar
        for file_key, data_key in files_to_process.items():
            file = request.files.get(file_key)
            logging.info(f"DEBUG: Processing file_key: {file_key}, file object: {file}, filename: {file.filename if file else 'None'}")
            if file and file.filename != '':
                try:
                    parsed_data = parser.parse_file(file, file_key)
                    if parsed_data is not None:
                        # Para boms, costs, y lots (que son dicts/lists de objetos), siempre guardar como pkl
                        if data_key in ['boms', 'costs', 'lots']:
                            data_filename = f"{session_id}_{data_key}.pkl"
                            data_path = os.path.join(app.config['DATA_CACHE_FOLDER'], data_filename)
                            with open(data_path, 'wb') as f:
                                pickle.dump(parsed_data, f)
                            session_data[data_key] = data_path
                        # Para DataFrames (stock_df, sales_df, suppliers_df), siempre guardar como feather
                        elif isinstance(parsed_data, pd.DataFrame):
                            data_filename = f"{session_id}_{data_key}.feather"
                            data_path = os.path.join(app.config['DATA_CACHE_FOLDER'], data_filename)
                            parsed_data.reset_index(drop=True).to_feather(data_path)
                            session_data[data_key] = data_path
                        else:
                            data_filename = f"{session_id}_{data_key}.pkl"
                            data_path = os.path.join(app.config['DATA_CACHE_FOLDER'], data_filename)
                            with open(data_path, 'wb') as f: pickle.dump(parsed_data, f)
                            session_data[data_key] = data_path
                        
                        # Guardar estado en base de datos
                        save_file_status_to_db(file_key, data_path)

                        flash(f'Archivo "{file.filename}" procesado correctamente.', 'success')
                except ValueError as ve:
                    flash(f'Error de formato en el archivo "{file.filename}": {ve}', 'danger')
                except Exception as e:
                    flash(f'Error inesperado al procesar el archivo "{file.filename}": {e}', 'danger')

        # Procesar archivo de Historico Costos
        historico_costos_file = request.files.get('historico_costos_file')
        if historico_costos_file and historico_costos_file.filename != '':
            logging.info(f"DEBUG: Procesando archivo histórico de costos: {historico_costos_file.filename}")
            try:
                parsed_data = parser.parse_file(historico_costos_file, 'historico_costos_file')
                logging.info(f"DEBUG: Datos parseados: {type(parsed_data)}, shape: {parsed_data.shape if hasattr(parsed_data, 'shape') else 'N/A'}")
                if parsed_data is not None and isinstance(parsed_data, pd.DataFrame):
                    data_filename = f"{session_id}_historico_costos_df.feather"
                    data_path = os.path.join(app.config['DATA_CACHE_FOLDER'], data_filename)
                    parsed_data.reset_index(drop=True).to_feather(data_path)
                    session_data['historico_costos_df'] = data_path
                    
                    # Guardar estado en base de datos
                    save_file_status_to_db('historico_costos_file', data_path)
                    
                    logging.info(f"DEBUG: Archivo guardado en: {data_path}")
                    flash(f'Archivo "{historico_costos_file.filename}" procesado correctamente.', 'success')
                else:
                    logging.error(f"DEBUG: parsed_data no es DataFrame: {type(parsed_data)}")
                    flash(f'Error: El archivo "{historico_costos_file.filename}" no contiene datos válidos.', 'danger')
            except Exception as e:
                logging.error(f"DEBUG: Error procesando histórico de costos: {e}")
                flash(f'Error inesperado al procesar el archivo "{historico_costos_file.filename}": {e}', 'danger')

        session['calculadora_core'] = session_data
        session.modified = True # Marca la sesión como modificada para que se guarde
        return redirect(url_for('index'))

    # Lógica GET para renderizar la página
    calculadora_data_raw = session.get('calculadora_core', {})
    model_options, sales_years = [], []

    # Cargar modelos desde BOM si está en caché
    boms_data = calculadora_data_raw.get('boms', {})
    if isinstance(boms_data, str) and boms_data.endswith('.pkl'):
        try:
            if os.path.exists(boms_data):
                with open(boms_data, 'rb') as f:
                    loaded_boms = pickle.load(f)
                model_options = list(loaded_boms.keys())
        except Exception as e:
            logging.error(f"No se pudo cargar la lista de modelos desde el archivo BOM cacheado: {e}")
    elif isinstance(boms_data, dict): # Esto ya no debería ocurrir si siempre se guarda como pkl
        model_options = list(boms_data.keys())

    # Cargar años de ventas y modelos de venta si el archivo de ventas está en caché
    sales_data_path = calculadora_data_raw.get('sales_df')
    if sales_data_path and isinstance(sales_data_path, str) and os.path.exists(sales_data_path):
        try:
            sales_df = pd.read_feather(sales_data_path)
            if not sales_df.empty and 'FECHA' in sales_df.columns:
                sales_years = sorted(sales_df['FECHA'].dt.year.unique(), reverse=True)
                # También añadimos los modelos de venta a las opciones de filtrado
                model_options.extend(sales_df['COD_PROD'].unique())
                model_options = sorted(list(set(model_options))) # Eliminar duplicados y ordenar
        except Exception as e:
            logging.error(f"No se pudo cargar la lista de años/modelos desde el archivo de ventas cacheado: {e}")

    # Obtener estado de archivos cargados desde base de datos
    files_status = get_file_status_from_db()
    
    # Si no hay datos en DB, usar sesión como fallback
    if not files_status:
        files_status = get_loaded_files_status()
    
    # Contexto para la plantilla
    context = {
        'model_options': model_options,
        'sales_years': sales_years,
        'bom_loaded': files_status['bom_loaded'],
        'stock_loaded': files_status['stock_loaded'],
        'lot_loaded': 'lots' in calculadora_data_raw, # Mantener por si se reintroduce la funcionalidad
        'cost_loaded': files_status['cost_loaded'],
        'sales_loaded': files_status['sales_loaded'],
        'suppliers_loaded': files_status['suppliers_loaded'],
        'historico_costos_loaded': files_status['historico_costos_loaded'],
        'individual_result': session.get('individual_result_path'), # Ahora se guarda la ruta
        'lot_calculation_results': session.get('lot_results_path'), # Ahora se guarda la ruta
        'aggregate_purchase_suggestions': session.get('lot_suggestions_path'), # Ahora se guarda la ruta
        'model_full_cost_result': session.get('model_full_cost_result_path'), # Ahora se guarda la ruta
        'current_year': datetime.now().year, # Pasa el año actual a la plantilla
        'active_section': section # Pasa la sección activa a la plantilla
    }
    
    # Debug: Log del estado de los archivos
    logging.info(f"DEBUG: Estado de archivos en sesión: {list(calculadora_data_raw.keys())}")
    logging.info(f"DEBUG: historico_costos_loaded: {'historico_costos_df' in calculadora_data_raw}")
    logging.info(f"DEBUG: Context completo: {context}")
    return render_template('index.html', **context)

# --- NUEVAS RUTAS DE RESULTADOS ---
@app.route('/individual_result')
@login_required
def individual_result_page():
    result_path = session.get('individual_result_path')
    if not result_path or not os.path.exists(result_path):
        flash("No se encontraron resultados individuales para mostrar o la sesión expiró.", "warning")
        return redirect(url_for('index'))
    try:
        with open(result_path, 'rb') as f:
            result_dict = pickle.load(f)
            result = IndividualCalculationResult(**result_dict) # Recrear el objeto desde el diccionario
    except Exception as e:
        flash(f"Error al cargar los resultados individuales: {e}", "danger")
        return redirect(url_for('index'))
    
    # Limpiar otros resultados para evitar confusión
    session.pop('lot_results_path', None)
    session.pop('lot_suggestions_path', None)
    session.pop('demand_results_path', None)
    session.pop('equalization_results_path', None)
    session.pop('suppliers_data_path', None)
    session.pop('model_full_cost_result_path', None)
    session.modified = True
    return render_template('individual_result.html', result=result)

@app.route('/lot_result')
@login_required
def lot_result_page():
    lot_results_path = session.get('lot_results_path')
    lot_suggestions_path = session.get('lot_suggestions_path')
    
    lot_results = None
    lot_suggestions = None

    if lot_results_path and os.path.exists(lot_results_path):
        try:
            with open(lot_results_path, 'rb') as f:
                lot_results_dict = pickle.load(f)
                lot_results = {k: LotCalculationResult(**v) for k, v in lot_results_dict.items()} # Recrear objetos
        except Exception as e:
            flash(f"Error al cargar los resultados de lote: {e}", "danger")
            return redirect(url_for('index'))
    
    if lot_suggestions_path and os.path.exists(lot_suggestions_path):
        try:
            with open(lot_suggestions_path, 'rb') as f:
                lot_suggestions_dict = pickle.load(f)
                lot_suggestions = {k: [PurchaseSuggestion(**item) for item in v] for k, v in lot_suggestions_dict.items()} # Recrear objetos
        except Exception as e:
            flash(f"Error al cargar las sugerencias de lote: {e}", "danger")
            return redirect(url_for('index'))

    if not lot_results and not lot_suggestions:
        flash("No se encontraron resultados de lote para mostrar o la sesión expiró.", "warning")
        return redirect(url_for('index'))
    
    # Limpiar otros resultados para evitar confusión
    session.pop('individual_result_path', None)
    session.pop('demand_results_path', None)
    session.pop('equalization_results_path', None)
    session.pop('suppliers_data_path', None)
    session.pop('model_full_cost_result_path', None)
    session.modified = True
    return render_template('lot_result.html', lot_results=lot_results, lot_suggestions=lot_suggestions)


@app.route('/api/sales_data')
@login_required # Protege esta API
def get_sales_data():
    core = get_core_instance()
    if not core or core.sales_df is None or core.sales_df.empty:
        return jsonify({'error': 'No hay datos de ventas cargados o la sesión expiró.'}), 404

    df = core.sales_df.copy()
    year = request.args.get('year', 'all')
    period = request.args.get('period', 'anual')
    models_str = request.args.get('models', '')

    # --- LÓGICA DE FILTRADO ---
    if models_str:
        selected_models = models_str.split(',')
        df = df[df['COD_PROD'].isin(selected_models)]
    else:
        # Si no se selecciona ningún modelo, devolvemos datos vacíos para no mostrar un gráfico confuso
        return jsonify({'labels': [], 'datasets': []})

    if year != 'all':
        df = df[df['FECHA'].dt.year == int(year)]

    if period == 's1': df = df[df['FECHA'].dt.month.isin(range(1, 7))]
    elif period == 's2': df = df[df['FECHA'].dt.month.isin(range(7, 13))]
    elif period == 'q1': df = df[df['FECHA'].dt.quarter == 1]
    elif period == 'q2': df = df[df['FECHA'].dt.quarter == 2]
    elif period == 'q3': df = df[df['FECHA'].dt.quarter == 3]
    elif period == 'q4': df = df[df['FECHA'].dt.quarter == 4]

    if df.empty:
        return jsonify({'labels': [], 'datasets': []})

    # --- LÓGICA REFACTORIZADA PARA CREAR DATASETS POR MODELO ---
    df.loc[:, 'MES'] = df['FECHA'].dt.month # Usamos .loc para evitar SettingWithCopyWarning
    sales_by_month_model = df.groupby(['MES', 'COD_PROD'])['VENTA'].sum().unstack(fill_value=0)

    all_months = sorted(df['MES'].unique())
    labels = [calendar.month_name[i].capitalize() for i in all_months]

    datasets = []
    colors = ['rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)', 'rgba(75, 192, 192, 0.6)', 'rgba(153, 102, 255, 0.6)', 'rgba(255, 159, 64, 0.6)']

    for i, model_code in enumerate(sales_by_month_model.columns):
        model_sales = sales_by_month_model[model_code]
        data_for_all_months = [float(model_sales.get(month, 0)) for month in all_months]

        dataset = {
            'label': model_code,
            'data': data_for_all_months,
            'backgroundColor': colors[i % len(colors)]
        }
        datasets.append(dataset)

    return jsonify({'labels': labels, 'datasets': datasets})

# --- NUEVA RUTA PARA OBTENER MODELOS ---
@app.route('/api/models')
@login_required
def get_models():
    try:
        calculadora_data_raw = session.get('calculadora_core', {})
        model_options = []
        boms_data = calculadora_data_raw.get('boms', {})
        if isinstance(boms_data, str) and boms_data.endswith('.pkl'):
            try:
                if os.path.exists(boms_data):
                    with open(boms_data, 'rb') as f:
                        loaded_boms = pickle.load(f)
                    model_options = list(loaded_boms.keys())
            except Exception as e:
                print(f"Error al cargar los modelos desde el archivo BOM cacheado para /api/models: {e}")
        elif isinstance(boms_data, dict):
            model_options = list(boms_data.keys())
        
        # También añadimos los modelos de venta si existen
        sales_data_path = calculadora_data_raw.get('sales_df')
        if sales_data_path and isinstance(sales_data_path, str) and os.path.exists(sales_data_path):
            try:
                sales_df = pd.read_feather(sales_data_path)
                if not sales_df.empty and 'COD_PROD' in sales_df.columns:
                    model_options.extend(sales_df['COD_PROD'].unique())
            except Exception as e:
                print(f"Error al cargar los modelos desde el archivo de ventas cacheado para /api/models: {e}")

        model_options = sorted(list(set(model_options))) # Eliminar duplicados y ordenar
        return jsonify({'success': True, 'models': model_options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'models': []})


@app.route('/clear_data', methods=['POST'])
@login_required # Protege esta ruta
def clear_data():
    cache_folder = app.config['DATA_CACHE_FOLDER']
    if 'session_id' in session:
        session_id = session['session_id']
        for item in os.listdir(cache_folder):
            if item.startswith(session_id):
                try:
                    os.remove(os.path.join(cache_folder, item))
                except Exception as e:
                    pass # No mostrar error al usuario si no es crítico
    session.pop('calculadora_core', None) # Solo borra los datos de la calculadora, no toda la sesión
    session.pop('individual_result_path', None) # Limpiar la ruta
    session.pop('lot_results_path', None) # Limpiar la ruta
    session.pop('lot_suggestions_path', None) # Limpiar la ruta
    session.pop('demand_results_path', None)
    session.pop('equalization_results_path', None) # Limpiar también el resultado de equilibrado
    session.pop('suppliers_data_path', None) # Limpiar también los datos de proveedores
    session.pop('model_full_cost_result_path', None) # Nuevo: Limpiar resultado de costo total de modelo
    flash('Todos los datos de la sesión y la caché han sido eliminados.', 'info')
    return redirect(url_for('index'))

@app.route('/calculate_individual', methods=['POST'])
@login_required # Protege esta ruta
def calculate_individual():
    calculadora_core = get_core_instance()
    if not calculadora_core:
        flash('No hay datos cargados o la sesión expiró. Por favor, recarga los archivos.', 'warning')
        return redirect(url_for('index'))

    model_name = request.form.get('model_name')
    desired_qty_str = request.form.get('desired_qty')

    if not model_name or not desired_qty_str:
        flash('Debes seleccionar un modelo y una cantidad deseada.', 'warning')
        return redirect(url_for('index'))

    try:
        desired_qty = int(desired_qty_str)
        if desired_qty <= 0:
            flash('La cantidad deseada debe ser un número positivo.', 'warning')
            return redirect(url_for('index'))
    except ValueError:
        flash('La cantidad deseada debe ser un número entero válido.', 'danger')
        return redirect(url_for('index'))

    result = calculadora_core.calculate_individual_fabricability(model_name, desired_qty)
    
    session_id = session.get('session_id', str(uuid.uuid4()))
    result_filename = f"{session_id}_individual_result.pkl"
    result_path = os.path.join(app.config['DATA_CACHE_FOLDER'], result_filename)

    with open(result_path, 'wb') as f:
        pickle.dump(result.to_dict(), f)

    session['individual_result_path'] = result_path
    session.modified = True
    flash(f'Cálculo de fabricabilidad individual para {model_name} completado.', 'success')
    return jsonify({'success': True, 'redirect_url': url_for('individual_result_page')})


@app.route('/calculate_lot', methods=['POST'])
@login_required # Protege esta ruta
def calculate_lot():
    calculadora_core = get_core_instance()
    if not calculadora_core:
        flash('No hay datos cargados o la sesión expiró. Por favor, recarga los archivos.', 'warning')
        return redirect(url_for('index'))

    results = calculadora_core.calculate_lot_fabricability()
    # Asegurarse de que results sea un diccionario con 'error' o 'results' y 'suggestions'
    if "error" in results: # Esto sigue siendo válido si calculate_lot_fabricability devuelve un diccionario de error
        flash(results["error"], "danger")
        return jsonify({'success': False, 'error': results["error"]})

    session_id = session.get('session_id', str(uuid.uuid4()))
    
    lot_results_filename = f"{session_id}_lot_results.pkl"
    lot_results_path = os.path.join(app.config['DATA_CACHE_FOLDER'], lot_results_filename)
    with open(lot_results_path, 'wb') as f:
        pickle.dump({k: v.to_dict() for k, v in results["results"].items()}, f)
    session['lot_results_path'] = lot_results_path

    lot_suggestions_filename = f"{session_id}_lot_suggestions.pkl"
    lot_suggestions_path = os.path.join(app.config['DATA_CACHE_FOLDER'], lot_suggestions_filename)
    with open(lot_suggestions_path, 'wb') as f:
        pickle.dump({k: [item.to_dict() for item in v] for k, v in results["suggestions"].items()}, f)
    session['lot_suggestions_path'] = lot_suggestions_path

    session.modified = True
    flash('Cálculo de fabricabilidad de lote completado.', 'success')
    return jsonify({'success': True, 'redirect_url': url_for('lot_result_page')})


@app.route('/calculate_model_demand', methods=['POST'])
@login_required # Protege esta ruta
def calculate_model_demand():
    calculadora_core = get_core_instance()
    if not calculadora_core:
        return jsonify({'success': False, 'error': 'No hay datos cargados o la sesión expiró. Por favor, recarga los archivos.'})

    # Obtener la cadena JSON de modelos y parsearla SIEMPRE como JSON
    selected_models_json = request.form.get('selected_models_demand')
    try:
        selected_models = json.loads(selected_models_json)
    except Exception:
        return jsonify({'success': False, 'error': 'Error al decodificar los modelos seleccionados para la demanda. Formato JSON inválido.'})

    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')

    if not selected_models:
        return jsonify({'success': False, 'error': 'No seleccionaste ningún modelo para calcular la demanda.'})
    if not start_date_str or not end_date_str:
        return jsonify({'success': False, 'error': 'Debes seleccionar una fecha de inicio y una fecha de fin para la proyección.'})

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        if start_date >= end_date:
            return jsonify({'success': False, 'error': 'La fecha de inicio debe ser anterior a la fecha de fin.'})
    except ValueError:
        return jsonify({'success': False, 'error': 'Formato de fecha inválido. Por favor, usa el formato `%Y-%m-%d`.'})

    print(f"🔍 LLAMANDO A PROYECCIÓN DE DEMANDA - Modelos: {selected_models}, Fechas: {start_date} a {end_date}")
    results = calculadora_core.proyectar_demanda_futura(selected_models, start_date, end_date)
    print(f"✅ PROYECCIÓN COMPLETADA - Resultado: {type(results)}")

    user_id = current_user.id
    results_filename = f"{user_id}_demand_results.pkl"
    results_path = os.path.join(app.config['DATA_CACHE_FOLDER'], results_filename)
    with open(results_path, 'wb') as f:
        pickle.dump(results, f)
    session['demand_results_path'] = results_path
    session.modified = True

    if results.mensaje:
        if "error" in results.mensaje.lower():
            return jsonify({'success': False, 'error': results.mensaje})
        else:
            return jsonify({'success': True, 'redirect_url': url_for('demand_result_page')})

    return jsonify({'success': True, 'redirect_url': url_for('demand_result_page')})

@app.route('/demand_result')
@login_required # Protege esta ruta
def demand_result_page():
    # Cargar el resultado de la proyección de demanda desde el archivo de caché
    user_id = current_user.id
    if not user_id:
        flash('Sesión expirada. Por favor, vuelve a iniciar sesión.', 'warning')
        return redirect(url_for('index'))
    cache_file = f"data_cache/{user_id}_demand_results.pkl"
    if not os.path.exists(cache_file):
        flash('No hay resultados de proyección de demanda disponibles.', 'warning')
        return redirect(url_for('index'))
    try:
        with open(cache_file, 'rb') as f:
            results = pickle.load(f)
    except Exception as e:
        flash(f'Error al cargar los resultados: {e}', 'danger')
        return redirect(url_for('index'))

    # Validar que haya sugerencias agrupadas y días hábiles proyectados
    mostrar_mensaje = False
    if not results or not getattr(results, 'sugerencias_agrupadas', None):
        mostrar_mensaje = True
    else:
        # Verificar si todos los modelos tienen lista vacía de componentes necesarios
        all_empty = True
        for modelo, data in results.sugerencias_agrupadas.items():
            if data['componentes_necesarios']:
                all_empty = False
                break
        if all_empty:
            mostrar_mensaje = True

    # Si projection_period no existe o es None, ponerlo en 0
    projection_period = getattr(results, 'projection_period', 0)
    if projection_period is None:
        projection_period = 0

    response = make_response(render_template(
        'demand_result.html',
        results=results,
        mostrar_mensaje=mostrar_mensaje,
        projection_period=projection_period
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


# --- NUEVA RUTA PARA CALCULAR EQUILIBRADO DE STOCK ---
@app.route('/calculate_stock_equalization', methods=['POST'])
@login_required
def calculate_stock_equalization():
    # Protección extra: si la petición no es POST o faltan datos, redirigir
    if request.method != 'POST':
        flash('Acceso inválido al cálculo de equilibrado. Usa la interfaz de la aplicación.', 'warning')
        return redirect(url_for('index'))
    if not request.form or 'selected_models_equalization' not in request.form:
        flash('Faltan datos para calcular el equilibrado. Usa la interfaz de la aplicación.', 'warning')
        return redirect(url_for('index'))

    calculadora_core = get_core_instance()
    if not calculadora_core:
        flash('No hay datos cargados o la sesión expiró. Por favor, recarga los archivos.', 'warning')
        return redirect(url_for('index'))

    selected_models_json = request.form.get('selected_models_equalization')
    print(f"DEBUG (Backend - Equilibrado): selected_models_json RAW received: '{selected_models_json}' (Type: {type(selected_models_json)})")

    selected_models = []
    if selected_models_json is None or not selected_models_json.strip():
        print("DEBUG (Backend - Equilibrado): selected_models_json is None or empty/whitespace. Treating as no models selected.")
        selected_models = []
    else:
        try:
            if isinstance(selected_models_json, list):
                selected_models = selected_models_json
            else:
                decoded = json.loads(selected_models_json)
                if isinstance(decoded, list):
                    selected_models = decoded
                elif isinstance(decoded, str):
                    selected_models = [decoded]
                else:
                    selected_models = []
            print(f"DEBUG (Backend - Equilibrado): selected_models after decode: {selected_models} (Type: {type(selected_models)})")
        except Exception as e:
            print(f"DEBUG (Backend - Equilibrado): Error al decodificar modelos: {e} - Input was: '{selected_models_json}'")
            flash('Error al decodificar los modelos seleccionados para el equilibrado. Formato JSON inválido.', 'danger')
            return jsonify({'success': False, 'error': 'Error al decodificar los modelos seleccionados para el equilibrado. Formato JSON inválido.'})
    
    start_date_str = request.form.get('start_date_equalization')
    end_date_str = request.form.get('end_date_equalization')

    if not selected_models:
        flash('No seleccionaste ningún modelo para calcular el equilibrado de stock.', 'warning')
        return jsonify({'success': False, 'error': 'No seleccionaste ningún modelo para calcular el equilibrado de stock.'})
    
    if not start_date_str or not end_date_str:
        flash('Debes seleccionar una fecha de inicio y una fecha de fin para el equilibrado.', 'warning')
        return jsonify({'success': False, 'error': 'Debes seleccionar una fecha de inicio y una fecha de fin para el equilibrado.'})

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        if start_date >= end_date:
            flash('La fecha de inicio debe ser anterior a la fecha de fin para el equilibrado.', 'warning')
            return jsonify({'success': False, 'error': 'La fecha de inicio debe ser anterior a la fecha de fin para el equilibrado.'})
    except ValueError:
        flash('Formato de fecha inválido para el equilibrado. Por favor, usa el formato `%Y-%m-%d`.', 'danger')
        return jsonify({'success': False, 'error': 'Formato de fecha inválido para el equilibrado. Por favor, usa el formato `%Y-%m-%d`.'})

    results = calculadora_core.calculate_stock_equalization(selected_models, start_date, end_date)

    session_id = session.get('session_id', str(uuid.uuid4()))
    results_filename = f"{session_id}_equalization_results.pkl"
    results_path = os.path.join(app.config['DATA_CACHE_FOLDER'], results_filename)

    with open(results_path, 'wb') as f:
        pickle.dump(results.to_dict(), f)
    print(f"DEBUG: Archivo de resultados de equilibrado guardado en: {results_path}")
    print(f"DEBUG: Tamaño del archivo guardado: {os.path.getsize(results_path)} bytes")

    session['equalization_results_path'] = results_path
    session.modified = True
    flash('Cálculo de equilibrado de stock completado.', 'success')
    return jsonify({'success': True, 'redirect_url': url_for('equalization_result_page')})


# --- NUEVA RUTA PARA MOSTRAR RESULTADOS DE EQUILIBRADO DE STOCK ---
@app.route('/equalization_result')
@login_required
def equalization_result_page():
    results_path = session.get('equalization_results_path')
    print(f"DEBUG: Intentando cargar resultados de equilibrado desde: {results_path}")
    if not results_path or not os.path.exists(results_path):
        flash("No se encontraron resultados de equilibrado para mostrar o la sesión expiró.", "warning")
        return redirect(url_for('index'))
    try:
        file_size = os.path.getsize(results_path)
        print(f"DEBUG: Tamaño del archivo de resultados: {file_size} bytes")
        if file_size == 0:
            flash("El archivo de resultados de equilibrado está vacío. Por favor, repite el cálculo.", "danger")
            return redirect(url_for('index'))
        with open(results_path, 'rb') as f:
            results_dict = pickle.load(f)
            if not results_dict or not results_dict.get('component_summaries'):
                flash("El archivo de resultados de equilibrado no contiene datos válidos. Por favor, repite el cálculo.", "danger")
                return redirect(url_for('index'))
            formatted_component_summaries = []
            for comp_data in results_dict.get('component_summaries', []):
                # Convertir los valores numéricos a float si son string
                for key in ['demanda_total', 'stock_disponible', 'cantidad_faltante_original', 'costo_unitario_proveedor_final', 'cantidad_a_comprar_final', 'costo_total_compra_final']:
                    if key in comp_data and isinstance(comp_data[key], str):
                        try:
                            comp_data[key] = float(comp_data[key].replace(',', '.').replace('$','').strip())
                        except Exception:
                            comp_data[key] = 0.0
                formatted_component_summaries.append(comp_data)
            results_dict['component_summaries'] = formatted_component_summaries
            
            # Asegurarse de que el mensaje sea verdaderamente vacío si solo contiene espacios en blanco
            cleaned_message = results_dict.get('message', '').strip()
            if not cleaned_message:
                cleaned_message = "No se encontraron componentes faltantes después de la proyección de demanda para la igualación, o el stock actual cubre todas las necesidades."

            results = EqualizationResult(
                component_summaries=formatted_component_summaries,
                total_cost_after_equalization=results_dict.get('total_cost_after_equalization', 0.0), # Dejar como float para formatear en la plantilla
                message=cleaned_message, # Usar el mensaje limpio
                projection_period_months=results_dict.get('projection_period_months', 0)
            )
            
    except Exception as e:
        print(f"DEBUG: Error al cargar o procesar el archivo de resultados de equilibrado: {e}")
        flash("Ocurrió un error al cargar los resultados de equilibrado. Por favor, repite el cálculo.", "danger")
        return redirect(url_for('index'))

    session.pop('individual_result_path', None)
    session.pop('lot_results_path', None)
    session.pop('lot_suggestions_path', None)
    session.pop('demand_results_path', None) # Limpiar otros resultados
    session.pop('suppliers_data_path', None) # Limpiar también los datos de proveedores
    session.pop('model_full_cost_result_path', None) # Limpiar también el resultado de costo total de modelo
    session.modified = True
    return render_template('equalization_result.html', results=results)

# --- NUEVAS RUTAS PARA PROVEEDORES ---
@app.route('/view_suppliers')
@login_required
def view_suppliers():
    calculadora_core = get_core_instance()
    if not calculadora_core or calculadora_core.suppliers_df is None or calculadora_core.suppliers_df.empty:
        flash('No hay datos de proveedores cargados o la sesión expiró. Por favor, carga el archivo de proveedores.', 'warning')
        return redirect(url_for('index'))
    
    # Esto es crucial porque get_core_instance() carga el DataFrame, pero no lo modifica.
    # El DataFrame ya debería tener las columnas en minúsculas si se procesó correctamente en la carga.
    # Sin embargo, para mayor seguridad, podemos asegurar que las columnas estén en minúsculas justo antes de usarlo.
    suppliers_df_processed = calculadora_core.suppliers_df.copy() # Trabajar con una copia
    suppliers_df_processed.columns = suppliers_df_processed.columns.str.lower()
    
    # Convertir el DataFrame de proveedores a una lista de diccionarios para pasar a la plantilla
    # Esto asegura que los datos sean fácilmente iterables en Jinja2
    suppliers_data = suppliers_df_processed.to_dict(orient='records')
    
    # Opcional: Si quieres pasar los artículos únicos para un filtro en la página de proveedores
    # Asegúrate de que la columna 'articulo' exista y esté en minúsculas
    unique_articles = sorted(suppliers_df_processed['articulo'].unique().tolist())

    return render_template('suppliers_comparison.html', 
                           suppliers_data=suppliers_data,
                           unique_articles=unique_articles)

# --- NUEVA RUTA PARA CALCULAR EL COSTO TOTAL DE UN MODELO ---
@app.route('/calculate_model_full_cost', methods=['POST'])
@login_required
def calculate_model_full_cost():
    calculadora_core = get_core_instance()
    if not calculadora_core:
        flash('No hay datos cargados o la sesión expiró. Por favor, recarga los archivos.', 'warning')
        return redirect(url_for('index'))

    model_name = request.form.get('model_name_full_cost')
    quantity_str = request.form.get('quantity_full_cost')

    if not model_name or not quantity_str:
        flash('Debes seleccionar un modelo y una cantidad para el cálculo de costo total.', 'warning')
        return redirect(url_for('index'))

    try:
        quantity = int(quantity_str)
        if quantity <= 0:
            flash('La cantidad debe ser un número positivo.', 'warning')
            return redirect(url_for('index'))
    except ValueError:
        flash('La cantidad debe ser un número entero válido.', 'danger')
        return redirect(url_for('index'))

    result = calculadora_core.calculate_model_full_cost(model_name, quantity)

    session_id = session.get('session_id', str(uuid.uuid4()))
    result_filename = f"{session_id}_model_full_cost_result.pkl"
    result_path = os.path.join(app.config['DATA_CACHE_FOLDER'], result_filename)

    with open(result_path, 'wb') as f:
        pickle.dump(result.to_dict(), f)

    session['model_full_cost_result_path'] = result_path
    session.modified = True
    flash(f'Costo total de fabricación para {model_name} (x{quantity}) calculado exitosamente.', 'success')
    return jsonify({'success': True, 'redirect_url': url_for('model_full_cost_result_page')})


# --- NUEVA RUTA PARA MOSTRAR LOS RESULTADOS DEL COSTO TOTAL DE UN MODELO ---
@app.route('/model_full_cost_result')
@login_required
def model_full_cost_result_page():
    result_path = session.get('model_full_cost_result_path')
    if not result_path or not os.path.exists(result_path):
        flash("No se encontraron resultados de costo total de modelo para mostrar o la sesión expiró.", "warning")
        return redirect(url_for('index'))
    try:
        with open(result_path, 'rb') as f:
            result_dict = pickle.load(f)
            result = ModelFullCostResult(**result_dict) # Recrear el objeto desde el diccionario
            # Formatear los valores numéricos dentro de detalle_componentes
            if result.detalle_componentes:
                formatted_details = []
                for comp in result.detalle_componentes:
                    if hasattr(comp, 'to_dict'):
                        formatted_comp = comp.to_dict() # Obtener el diccionario base
                    else:
                        formatted_comp = comp # Ya es un dict
                    formatted_comp['cantidad_requerida_total'] = f"{float(formatted_comp['cantidad_requerida_total']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    formatted_comp['cantidad_disponible_stock'] = f"{float(formatted_comp['cantidad_disponible_stock']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    formatted_comp['cantidad_faltante'] = f"{float(formatted_comp['cantidad_faltante']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    formatted_comp['costo_unitario'] = f"$ {float(formatted_comp['costo_unitario']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    formatted_comp['costo_total'] = f"$ {float(formatted_comp['costo_total']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    formatted_details.append(formatted_comp)
                result.detalle_componentes = formatted_details # Asignar la lista formateada
            
            # Formatear el costo total de fabricación
            result.costo_total_fabricacion = f"{result.costo_total_fabricacion:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    except Exception as e:
        flash(f"Error al cargar los resultados de costo total de modelo: {e}", "danger")
        return redirect(url_for('index'))
    
    # Limpiar otros resultados para evitar confusión
    session.pop('individual_result_path', None)
    session.pop('lot_results_path', None)
    session.pop('lot_suggestions_path', None)
    session.pop('demand_results_path', None)
    session.pop('equalization_results_path', None)
    session.pop('suppliers_data_path', None)
    # session.pop('model_full_cost_result_path', None)  # NO eliminar aquí, se necesita para exportar
    session.modified = True
    return render_template('model_full_cost_result.html', result=result)


@app.route('/generate_report', methods=['POST'])
@permission_required('reports_generate') # Protege esta ruta
def generate_report():
    report_type = request.form.get('report_type')
    if not report_type:
        flash('Tipo de reporte no especificado.', 'danger')
        return redirect(url_for('index'))

    data = None
    if report_type == 'individual' and 'individual_result_path' in session:
        results_path = session.get('individual_result_path')
        if results_path and os.path.exists(results_path):
            with open(results_path, 'rb') as f:
                data = pickle.load(f)
    elif report_type == 'lot' and 'lot_results_path' in session:
        lot_results_path = session.get('lot_results_path')
        lot_suggestions_path = session.get('lot_suggestions_path')
        lot_results_data = {}
        lot_suggestions_data = {}
        if lot_results_path and os.path.exists(lot_results_path):
            with open(lot_results_path, 'rb') as f:
                lot_results_data = pickle.load(f)
        if lot_suggestions_path and os.path.exists(lot_suggestions_path):
            with open(lot_suggestions_path, 'rb') as f:
                lot_suggestions_data = pickle.load(f)
        data = {'results': lot_results_data, 'suggestions': lot_suggestions_data}

    elif report_type == 'demand' and 'demand_results_path' in session:
        results_path = session.get('demand_results_path')
        if results_path and os.path.exists(results_path):
             with open(results_path, 'rb') as f:
                 data = pickle.load(f)
    elif report_type == 'equalization' and 'equalization_results_path' in session: # NUEVO TIPO DE REPORTE
        results_path = session.get('equalization_results_path')
        print(f"DEBUG: Ruta de resultados de equilibrado para Excel: {results_path}")
        if results_path and os.path.exists(results_path):
             print(f"DEBUG: Tamaño del archivo: {os.path.getsize(results_path)} bytes")
             with open(results_path, 'rb') as f:
                 data = pickle.load(f)
                 print(f"DEBUG: Tipo de data: {type(data)}")
                 if isinstance(data, dict):
                     print(f"DEBUG: Claves de data: {list(data.keys())}")
                     if 'component_summaries' in data:
                         print(f"DEBUG: Cantidad de componentes: {len(data['component_summaries'])}")
                 elif hasattr(data, 'component_summaries'):
                     print(f"DEBUG: Cantidad de componentes (objeto): {len(data.component_summaries)}")
    elif report_type == 'suppliers' and 'calculadora_core' in session and 'suppliers_df' in session['calculadora_core']:
        suppliers_df_path = session['calculadora_core']['suppliers_df']
        if os.path.exists(suppliers_df_path):
            data = pd.read_feather(suppliers_df_path)
            data.columns = data.columns.str.lower()
        else:
            flash('Error: Archivo de proveedores no encontrado para generar el reporte.', 'danger')
            return redirect(url_for('index'))
    elif report_type == 'model_full_cost' and 'model_full_cost_result_path' in session: # Nuevo tipo de reporte
        results_path = session.get('model_full_cost_result_path')
        if results_path and os.path.exists(results_path):
            with open(results_path, 'rb') as f:
                data = pickle.load(f)
    elif report_type == 'costs' and 'calculadora_core' in session and 'historico_costos_df' in session['calculadora_core']:
        historico_costos_path = session['calculadora_core']['historico_costos_df']
        if os.path.exists(historico_costos_path):
            data = pd.read_feather(historico_costos_path)
        else:
            flash('Error: Archivo de histórico de costos no encontrado para generar el reporte.', 'danger')
            return redirect(url_for('index'))

    # ADVERTENCIA SI EL EXCEL VA A SALIR VACÍO
    if report_type == 'equalization' and data is not None:
        comp_count = 0
        if isinstance(data, dict) and 'component_summaries' in data:
            comp_count = len(data['component_summaries'])
        elif hasattr(data, 'component_summaries'):
            comp_count = len(data.component_summaries)
        if comp_count == 0:
            flash('No hay componentes para exportar en el reporte de equilibrado. El Excel estará vacío.', 'warning')

    if data is not None:
        generator = ReportGenerator(data)
        file_path = generator.generate_report(report_type)
        if os.path.exists(file_path):
            flash(f'Reporte de tipo "{report_type}" generado exitosamente.', 'success')
            return send_file(file_path, as_attachment=True)
        else:
            flash('Error: El archivo de reporte no se pudo generar o no se encontró.', 'danger')
            return redirect(url_for('index'))
    else:
        flash('No hay datos disponibles para generar el reporte solicitado.', 'warning')
        return redirect(url_for('index'))

@app.route('/api/historico_costos', methods=['GET'])
@login_required
def api_historico_costos():
    """
    Si se llama sin parámetros, devuelve la lista de artículos.
    Si se pasa ?articulo=XXX, devuelve los años y costos de ese artículo.
    """
    calculadora_data_raw = session.get('calculadora_core', {})
    path = calculadora_data_raw.get('historico_costos_df')
    if not path or not os.path.exists(path):
        return jsonify({'success': False, 'error': 'No hay archivo de histórico de costos cargado.'}), 404
    df = pd.read_feather(path)
    articulo = request.args.get('articulo')
    if not articulo:
        # Devolver lista de artículos
        articulos = df.iloc[:,0].dropna().unique().tolist()
        return jsonify({'success': True, 'articulos': articulos})
    else:
        # Devolver historial de costos del artículo
        row = df[df.iloc[:,0] == articulo]
        if row.empty:
            return jsonify({'success': False, 'error': 'Artículo no encontrado.'}), 404
        # Extraer años y costos
        data = row.iloc[0,1:].to_dict()
        # Filtrar solo años válidos y costos no nulos
        historial = [
            {'anio': str(col), 'costo': float(val) if pd.notna(val) else None}
            for col, val in data.items()
        ]
        return jsonify({'success': True, 'articulo': articulo, 'historial': historial})

@app.route('/api/sales_analysis', methods=['GET'])
@login_required
def api_sales_analysis():
    try:
        year = request.args.get('year', '')
        period = request.args.get('period', 'year')
        models = request.args.get('models', '').split(',') if request.args.get('models') else []
        
        print(f"DEBUG: api_sales_analysis - Parámetros recibidos:")
        print(f"  year: {year}")
        print(f"  period: {period}")
        print(f"  models: {models}")
        
        # Obtener datos de ventas
        calculadora_data_raw = session.get('calculadora_core', {})
        sales_path = calculadora_data_raw.get('sales_df')
        
        print(f"DEBUG: sales_path: {sales_path}")
        
        if not sales_path or not os.path.exists(sales_path):
            print("DEBUG: No hay datos de ventas cargados")
            return jsonify({'success': False, 'error': 'No hay datos de ventas cargados'})
        
        sales_df = pd.read_feather(sales_path)
        print(f"DEBUG: sales_df shape: {sales_df.shape}")
        print(f"DEBUG: sales_df columns: {list(sales_df.columns)}")
        print(f"DEBUG: sales_df dtypes: {sales_df.dtypes}")
        print(f"DEBUG: Primeras 5 filas:")
        print(sales_df.head())
        
        # Verificar que las columnas necesarias existen
        required_columns = ['FECHA', 'COD_PROD', 'VENTA']  # Cambiar a los nombres reales
        missing_columns = [col for col in required_columns if col not in sales_df.columns]
        
        if missing_columns:
            print(f"DEBUG: Columnas faltantes: {missing_columns}")
            print(f"DEBUG: Columnas disponibles: {list(sales_df.columns)}")
            
            # Buscar columnas similares
            print(f"DEBUG: Buscando columnas similares...")
            for col in sales_df.columns:
                print(f"  - {col}")
            
            # Sugerir posibles mapeos
            possible_mappings = {
                'FECHA': ['fecha', 'date', 'fecha_venta', 'fecha_ventas', 'fecha_compra', 'fecha_transaccion'],
                'COD_PROD': ['modelo', 'model', 'producto', 'articulo', 'codigo', 'codigo_producto', 'nombre_producto'],
                'VENTA': ['cantidad', 'quantity', 'qty', 'cant', 'unidades', 'ventas', 'total_ventas']
            }
            
            print(f"DEBUG: Posibles mapeos de columnas:")
            for required, alternatives in possible_mappings.items():
                if required in missing_columns:
                    found = [col for col in alternatives if col in sales_df.columns]
                    if found:
                        print(f"  {required} -> {found[0]}")
                    else:
                        print(f"  {required} -> NO ENCONTRADA")
            
            return jsonify({'success': False, 'error': f'Columnas faltantes en datos de ventas: {missing_columns}. Columnas disponibles: {list(sales_df.columns)}'})
        
        print(f"DEBUG: Todas las columnas requeridas están presentes")
        
        # Filtrar por año si se especifica
        if year:
            sales_df = sales_df[sales_df['FECHA'].dt.year == int(year)]  # Cambiar a FECHA
            print(f"DEBUG: Después de filtrar por año {year}: {sales_df.shape[0]} registros")
        
        # Filtrar por modelos si se especifican
        if models and models[0]:  # Verificar que no esté vacío
            print(f"DEBUG: Filtrando por modelos: {models}")
            print(f"DEBUG: Modelos únicos en datos: {sales_df['COD_PROD'].unique()}")  # Cambiar a COD_PROD
            sales_df = sales_df[sales_df['COD_PROD'].isin(models)]  # Cambiar a COD_PROD
            print(f"DEBUG: Después de filtrar por modelos {models}: {sales_df.shape[0]} registros")
        
        if sales_df.empty:
            print("DEBUG: DataFrame vacío después de filtros")
            return jsonify({
                'success': True,
                'chart_data': {'labels': [], 'datasets': []},
                'summary': {'total_sales': 0, 'avg_sales': 0, 'top_model': '', 'top_sales': 0},
                'distribution': {'labels': [], 'data': []},
                'details': []
            })
        
        print(f"DEBUG: Datos finales: {sales_df.shape[0]} registros")
        print(f"DEBUG: Modelos únicos: {sales_df['COD_PROD'].unique()}")  # Cambiar a COD_PROD
        
        # Preparar datos según el período
        if period == 'year':
            sales_df['period'] = sales_df['FECHA'].dt.year  # Cambiar a FECHA
            period_labels = sales_df['period'].unique()
        elif period == 'semester':
            sales_df['period'] = sales_df['FECHA'].dt.year.astype(str) + '-' + ((sales_df['FECHA'].dt.month > 6) + 1).astype(str)  # Cambiar a FECHA
            period_labels = sorted(sales_df['period'].unique())
        elif period == 'quarter':
            sales_df['period'] = sales_df['FECHA'].dt.year.astype(str) + '-Q' + sales_df['FECHA'].dt.quarter.astype(str)  # Cambiar a FECHA
            period_labels = sorted(sales_df['period'].unique())
        else:  # month
            sales_df['period'] = sales_df['FECHA'].dt.strftime('%Y-%m')  # Cambiar a FECHA
            period_labels = sorted(sales_df['period'].unique())
        
        print(f"DEBUG: Períodos únicos: {period_labels}")
        
        # Agrupar datos
        grouped_sales = sales_df.groupby(['period', 'COD_PROD'])['VENTA'].sum().reset_index()  # Cambiar a COD_PROD y VENTA
        print(f"DEBUG: Datos agrupados: {grouped_sales.shape[0]} registros")
        
        # Preparar datos para el gráfico principal
        chart_data = {
            'labels': [str(label) for label in period_labels],  # Convertir a strings
            'datasets': []
        }
        
        # Crear dataset para cada modelo
        for modelo in grouped_sales['COD_PROD'].unique():  # Cambiar a COD_PROD
            model_data = []
            for period in period_labels:
                sales = float(grouped_sales[(grouped_sales['period'] == period) & (grouped_sales['COD_PROD'] == modelo)]['VENTA'].sum())  # Convertir a float
                model_data.append(sales)
            
            chart_data['datasets'].append({
                'label': str(modelo),  # Convertir a string
                'data': model_data,
                'borderColor': f'#{hash(str(modelo)) % 0xFFFFFF:06x}',
                'backgroundColor': f'rgba({hash(str(modelo)) % 255}, {hash(str(modelo)) % 100 + 100}, {hash(str(modelo)) % 100 + 150}, 0.2)',
                'fill': False
            })
        
        print(f"DEBUG: Datasets creados: {len(chart_data['datasets'])}")
        
        # Calcular resumen estadístico
        total_sales = float(sales_df['VENTA'].sum())  # Convertir a float
        avg_sales = float(sales_df['VENTA'].mean())  # Convertir a float
        top_model_sales = sales_df.groupby('COD_PROD')['VENTA'].sum().sort_values(ascending=False)  # Cambiar a COD_PROD y VENTA
        top_model = str(top_model_sales.index[0]) if not top_model_sales.empty else ''  # Convertir a string
        top_sales = float(top_model_sales.iloc[0]) if not top_model_sales.empty else 0.0  # Convertir a float
        
        summary = {
            'total_sales': int(total_sales),
            'avg_sales': round(avg_sales, 2),
            'top_model': top_model,
            'top_sales': int(top_sales)
        }
        
        print(f"DEBUG: Resumen calculado: {summary}")
        
        # Preparar datos para el gráfico de distribución
        model_distribution = sales_df.groupby('COD_PROD')['VENTA'].sum().sort_values(ascending=False) # Cambiar a COD_PROD y VENTA
        distribution = {
            'labels': [str(label) for label in model_distribution.index.tolist()],  # Convertir a strings
            'data': [float(value) for value in model_distribution.values.tolist()]  # Convertir a floats
        }
        
        print(f"DEBUG: Distribución calculada: {len(distribution['labels'])} modelos")
        
        # Preparar datos detallados para la tabla
        details = []
        for period in period_labels:
            period_sales = grouped_sales[grouped_sales['period'] == period]
            for _, row in period_sales.iterrows():
                percentage = (float(row['VENTA']) / total_sales * 100) if total_sales > 0 else 0.0  # Convertir a float
                details.append({
                    'period': str(period),  # Convertir a string
                    'model': str(row['COD_PROD']),  # Convertir a string
                    'quantity': int(float(row['VENTA'])),  # Convertir a int
                    'percentage': round(percentage, 2)
                })
        
        print(f"DEBUG: Detalles calculados: {len(details)} registros")
        
        result = {
            'success': True,
            'chart_data': chart_data,
            'summary': summary,
            'distribution': distribution,
            'details': details
        }
        
        print("DEBUG: Respuesta enviada exitosamente")
        return jsonify(result)
        
    except Exception as e:
        print(f"DEBUG: Error en api_sales_analysis: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dashboard_data', methods=['GET'])
@permission_required('dashboard_view')
def api_dashboard_data():
    """Endpoint para obtener datos del dashboard ejecutivo"""
    try:
        logging.info("DEBUG: Iniciando api_dashboard_data")
        
        # Verificar si hay datos de ventas cargados
        # Correctly access sales_df from calculadora_core in session
        calculadora_data_raw = session.get('calculadora_core', {})
        sales_path = calculadora_data_raw.get('sales_df')

        if not sales_path or not os.path.exists(sales_path):
            logging.info("DEBUG: No hay datos de ventas cargados")
            return jsonify({
                'success': False,
                'error': 'No hay datos de ventas cargados'
            })
        
        # Load sales_df using pd.read_feather as it's stored as feather
        sales_df = pd.read_feather(sales_path)
        logging.info(f"DEBUG: Datos de ventas cargados: {sales_df.shape}")
        logging.info(f"DEBUG: Columnas disponibles: {sales_df.columns.tolist()}")
        
        # Verificar columnas requeridas
        required_columns = ['FECHA', 'COD_PROD', 'VENTA']
        missing_columns = [col for col in required_columns if col not in sales_df.columns]
        if missing_columns:
            logging.info(f"DEBUG: Columnas faltantes: {missing_columns}")
            return jsonify({
                'success': False,
                'error': f'Columnas faltantes en datos de ventas: {missing_columns}'
            })
        
        # Convertir fecha
        sales_df['FECHA'] = pd.to_datetime(sales_df['FECHA'])
        
        # Encontrar el año más reciente en los datos
        max_year = sales_df['FECHA'].dt.year.max()
        previous_year = max_year - 1
        
        # Filtrar datos del último año disponible
        sales_df_filtered = sales_df[sales_df['FECHA'].dt.year >= previous_year]
        
        # Calcular KPIs principales
        total_sales = float(sales_df_filtered['VENTA'].sum())
        total_models = int(sales_df_filtered['COD_PROD'].nunique())
        avg_sales = float(sales_df_filtered['VENTA'].mean())
        
        # Modelo top
        top_model_data = sales_df_filtered.groupby('COD_PROD')['VENTA'].sum().sort_values(ascending=False)
        top_model = str(top_model_data.index[0]) if not top_model_data.empty else 'N/A'
        top_sales = float(top_model_data.iloc[0]) if not top_model_data.empty else 0.0
        
        # Calcular cambios (comparar año más reciente vs año anterior)
        current_year_sales = sales_df[sales_df['FECHA'].dt.year == max_year]['VENTA'].sum()
        previous_year_sales = sales_df[sales_df['FECHA'].dt.year == previous_year]['VENTA'].sum()
        
        logging.info(f"DEBUG: Ventas año más reciente ({max_year}): {current_year_sales}")
        logging.info(f"DEBUG: Ventas año anterior ({previous_year}): {previous_year_sales}")
        
        # Lógica mejorada para el cálculo del cambio de ventas
        if previous_year_sales == 0 and current_year_sales == 0:
            # No hay ventas en ningún año
            sales_change = 0.0
            logging.info("DEBUG: No hay ventas en ningún año")
        elif previous_year_sales == 0 and current_year_sales > 0:
            # No había ventas el año anterior, pero sí este año (incremento infinito)
            sales_change = 100.0  # Mostrar como +100% en lugar de infinito
            logging.info("DEBUG: Incremento desde cero ventas")
        elif previous_year_sales > 0 and current_year_sales == 0:
            # Había ventas el año anterior, pero no este año (decremento total)
            sales_change = -100.0
            logging.info("DEBUG: Decremento total a cero ventas")
        else:
            # Caso normal: calcular el porcentaje de cambio
            sales_change = ((current_year_sales - previous_year_sales) / previous_year_sales) * 100
            logging.info(f"DEBUG: Cambio normal: {sales_change:.1f}%")
        
        logging.info(f"DEBUG: Cambio de ventas calculado: {sales_change:.1f}%")
        
        # Calcular tendencia de ventas (últimos 12 meses desde el año más reciente)
        end_date = sales_df['FECHA'].max()
        start_date = end_date - timedelta(days=365)
        last_12_months = sales_df[sales_df['FECHA'] >= start_date]
        monthly_trend = last_12_months.groupby(last_12_months['FECHA'].dt.strftime('%Y-%m'))['VENTA'].sum()
        
        trend_data = {
            'labels': [str(month) for month in monthly_trend.index],
            'data': [float(value) for value in monthly_trend.values]
        }
        
        # Calcular distribución por período (último año)
        period_distribution = sales_df_filtered.groupby(sales_df_filtered['FECHA'].dt.quarter)['VENTA'].sum()
        
        period_distribution_data = {
            'labels': [f'Q{quarter}' for quarter in period_distribution.index],
            'data': [float(value) for value in period_distribution.values]
        }
        
        # Generar alertas
        alerts = []
        
        # Alerta si las ventas han bajado
        if sales_change < -10:
            alerts.append({
                'type': 'warning',
                'title': 'Ventas en Declive',
                'message': f'Las ventas han disminuido un {abs(sales_change):.1f}% respecto al año anterior'
            })
        
        # Alerta si hay pocos modelos activos
        if total_models < 5:
            alerts.append({
                'type': 'info',
                'title': 'Pocos Modelos',
                'message': f'Solo hay {total_models} modelos activos en el sistema'
            })
        
        # Alerta si el modelo top domina las ventas
        top_percentage = (top_sales / total_sales * 100) if total_sales > 0 else 0
        if top_percentage > 50:
            alerts.append({
                'type': 'warning',
                'title': 'Concentración de Ventas',
                'message': f'El modelo {top_model} representa el {top_percentage:.1f}% de las ventas totales'
            })
        
        # Si no hay alertas, agregar mensaje positivo
        if not alerts:
            alerts.append({
                'type': 'success',
                'title': 'Rendimiento Óptimo',
                'message': 'Todos los indicadores están dentro de los rangos esperados'
            })
        
        # Preparar respuesta
        kpis = {
            'total_sales': total_sales,
            'total_models': total_models,
            'avg_sales': avg_sales,
            'top_model': top_model,
            'top_sales': top_sales,
            'sales_change': round(sales_change, 1),
            'models_change': 0,  # Por ahora fijo, se puede calcular después
            'avg_change': 0,  # Por ahora fijo, se puede calcular después
        }
        
        charts = {
            'trend': trend_data,
            'period_distribution': period_distribution_data
        }
        
        result = {
            'success': True,
            'kpis': kpis,
            'charts': charts,
            'alerts': alerts
        }
        
        logging.info("DEBUG: Datos del dashboard enviados exitosamente")
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"DEBUG: Error en api_dashboard_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/seasonal_analysis', methods=['GET'])
@permission_required('sales_analysis')
def api_seasonal_analysis():
    """Endpoint para análisis de estacionalidad de ventas"""
    try:
        logging.info("DEBUG: Iniciando análisis de estacionalidad")
        
        # Verificar si hay datos de ventas cargados
        sales_path = session.get('calculadora_core', {}).get('sales_df')
        if not sales_path or not os.path.exists(sales_path):
            logging.info("DEBUG: No hay datos de ventas cargados")
            return jsonify({
                'success': False,
                'error': 'No hay datos de ventas cargados'
            })
        
        # Load sales_df
        sales_df = pd.read_feather(sales_path)
        logging.info(f"DEBUG: Datos de ventas cargados para estacionalidad: {sales_df.shape}")
        
        # Verificar columnas requeridas
        required_columns = ['FECHA', 'COD_PROD', 'VENTA']
        missing_columns = [col for col in required_columns if col not in sales_df.columns]
        if missing_columns:
            logging.info(f"DEBUG: Columnas faltantes: {missing_columns}")
            return jsonify({
                'success': False,
                'error': f'Columnas faltantes en datos de ventas: {missing_columns}'
            })
        
        # Convertir fecha
        sales_df['FECHA'] = pd.to_datetime(sales_df['FECHA'])
        
        # Análisis de estacionalidad por mes
        sales_df['MES'] = sales_df['FECHA'].dt.month
        sales_df['AÑO'] = sales_df['FECHA'].dt.year
        
        # Calcular ventas promedio por mes
        monthly_avg = sales_df.groupby('MES')['VENTA'].mean()
        monthly_std = sales_df.groupby('MES')['VENTA'].std()
        
        # Calcular índice de estacionalidad (promedio del mes / promedio general)
        overall_avg = sales_df['VENTA'].mean()
        seasonal_index = (monthly_avg / overall_avg * 100).round(2)
        
        # Identificar meses de alta y baja temporada
        high_season_months = seasonal_index[seasonal_index > 110].index.tolist()
        low_season_months = seasonal_index[seasonal_index < 90].index.tolist()
        
        # Calcular tendencia lineal
        sales_df['MES_NUM'] = sales_df['FECHA'].dt.to_period('M').astype(int)
        trend_data = sales_df.groupby('MES_NUM')['VENTA'].sum().reset_index()
        
        if len(trend_data) > 1:
            # Calcular línea de tendencia usando regresión lineal
            x = trend_data['MES_NUM'].values.reshape(-1, 1)
            y = trend_data['VENTA'].values
            
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(x, y)
            
            trend_slope = model.coef_[0]
            trend_intercept = model.intercept_
            
            # Calcular R² para evaluar la calidad de la tendencia
            y_pred = model.predict(x)
            r_squared = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2))
            
            # Generar predicción para los próximos 3 meses
            future_months = np.array(range(trend_data['MES_NUM'].max() + 1, trend_data['MES_NUM'].max() + 4)).reshape(-1, 1)
            future_predictions = model.predict(future_months)
            
            trend_analysis = {
                'slope': float(trend_slope),
                'intercept': float(trend_intercept),
                'r_squared': float(r_squared),
                'trend_direction': 'creciente' if trend_slope > 0 else 'decreciente',
                'trend_strength': 'fuerte' if abs(r_squared) > 0.7 else 'moderada' if abs(r_squared) > 0.4 else 'débil',
                'predictions': [float(pred) for pred in future_predictions]
            }
        else:
            trend_analysis = {
                'slope': 0,
                'intercept': 0,
                'r_squared': 0,
                'trend_direction': 'insuficientes datos',
                'trend_strength': 'insuficientes datos',
                'predictions': []
            }
        
        # Preparar datos para gráficos
        month_names = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        seasonal_data = {
            'labels': [month_names[i-1] for i in range(1, 13)],
            'seasonal_index': [float(seasonal_index.get(i, 0)) for i in range(1, 13)],
            'monthly_avg': [float(monthly_avg.get(i, 0)) for i in range(1, 13)],
            'monthly_std': [float(monthly_std.get(i, 0)) for i in range(1, 13)]
        }
        
        result = {
            'success': True,
            'seasonal_analysis': {
                'seasonal_data': seasonal_data,
                'high_season_months': [month_names[i-1] for i in high_season_months],
                'low_season_months': [month_names[i-1] for i in low_season_months],
                'overall_avg': float(overall_avg),
                'trend_analysis': trend_analysis
            }
        }
        
        logging.info("DEBUG: Análisis de estacionalidad completado exitosamente")
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"DEBUG: Error en análisis de estacionalidad: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/sales_forecast', methods=['GET'])
@permission_required('sales_analysis')
def api_sales_forecast():
    """Endpoint para predicciones de ventas"""
    try:
        logging.info("DEBUG: Iniciando predicción de ventas")
        
        # Verificar si hay datos de ventas cargados
        sales_path = session.get('calculadora_core', {}).get('sales_df')
        if not sales_path or not os.path.exists(sales_path):
            logging.info("DEBUG: No hay datos de ventas cargados")
            return jsonify({
                'success': False,
                'error': 'No hay datos de ventas cargados'
            })
        
        # Load sales_df
        sales_df = pd.read_feather(sales_path)
        logging.info(f"DEBUG: Datos de ventas cargados para predicción: {sales_df.shape}")
        
        # Verificar columnas requeridas
        required_columns = ['FECHA', 'COD_PROD', 'VENTA']
        missing_columns = [col for col in required_columns if col not in sales_df.columns]
        if missing_columns:
            logging.info(f"DEBUG: Columnas faltantes: {missing_columns}")
            return jsonify({
                'success': False,
                'error': f'Columnas faltantes en datos de ventas: {missing_columns}'
            })
        
        # Convertir fecha
        sales_df['FECHA'] = pd.to_datetime(sales_df['FECHA'])
        
        # Preparar datos para predicción
        sales_df['MES'] = sales_df['FECHA'].dt.to_period('M')
        monthly_sales = sales_df.groupby('MES')['VENTA'].sum().reset_index()
        monthly_sales['MES_NUM'] = monthly_sales['MES'].astype(int)
        
        if len(monthly_sales) < 3:
            return jsonify({
                'success': False,
                'error': 'Se necesitan al menos 3 meses de datos para realizar predicciones'
            })
        
        # Modelo de predicción simple usando promedio móvil y tendencia
        x = monthly_sales['MES_NUM'].values.reshape(-1, 1)
        y = monthly_sales['VENTA'].values
        
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(x, y)
        
        # Calcular predicciones para los próximos 6 meses
        last_month = monthly_sales['MES_NUM'].max()
        future_months = np.array(range(last_month + 1, last_month + 7)).reshape(-1, 1)
        predictions = model.predict(future_months)
        
        # Calcular intervalo de confianza (simplificado)
        residuals = y - model.predict(x)
        std_error = np.std(residuals)
        confidence_interval = 1.96 * std_error  # 95% de confianza
        
        # Preparar datos para gráfico
        historical_data = {
            'labels': [str(month) for month in monthly_sales['MES']],
            'data': [float(val) for val in monthly_sales['VENTA']]
        }
        
        forecast_data = {
            'labels': [f'Predicción {i+1}' for i in range(6)],
            'data': [float(pred) for pred in predictions],
            'upper_bound': [float(pred + confidence_interval) for pred in predictions],
            'lower_bound': [float(pred - confidence_interval) for pred in predictions]
        }
        
        # Calcular métricas de calidad del modelo
        y_pred_historical = model.predict(x)
        mse = np.mean((y - y_pred_historical) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y - y_pred_historical))
        
        result = {
            'success': True,
            'forecast': {
                'historical_data': historical_data,
                'forecast_data': forecast_data,
                'model_metrics': {
                    'rmse': float(rmse),
                    'mae': float(mae),
                    'confidence_interval': float(confidence_interval)
                },
                'predictions': [
                    {
                        'month': f'Predicción {i+1}',
                        'value': float(pred),
                        'upper': float(pred + confidence_interval),
                        'lower': float(pred - confidence_interval)
                    }
                    for i, pred in enumerate(predictions)
                ]
            }
        }
        
        logging.info("DEBUG: Predicción de ventas completada exitosamente")
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"DEBUG: Error en predicción de ventas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

# --- RUTAS DE GESTIÓN DE USUARIOS ---
@app.route('/admin/users')
@admin_required
def admin_users():
    """Redirigir a la página principal con la pestaña de administración"""
    return redirect(url_for('index', section='admin'))

@app.route('/admin/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Crear nuevo usuario"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role_id = request.form.get('role_id')
        
        # Validaciones
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe.', 'error')
            return redirect(url_for('create_user'))
        
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'error')
            return redirect(url_for('create_user'))
        
        # Crear usuario
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role_id=role_id,
            created_by=current_user.id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        log_activity('user_created', {
            'created_user': username,
            'role_id': role_id
        })
        
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('admin_users'))
    
    roles = Role.query.all()
    return render_template('admin/create_user.html', roles=roles)

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Editar usuario existente"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.role_id = request.form.get('role_id')
        user.is_active = 'is_active' in request.form
        
        # Cambiar contraseña si se proporciona
        new_password = request.form.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        
        log_activity('user_updated', {
            'updated_user': user.username,
            'role_id': user.role_id
        })
        
        flash('Usuario actualizado exitosamente.', 'success')
        return redirect(url_for('admin_users'))
    
    roles = Role.query.all()
    return render_template('admin/edit_user.html', user=user, roles=roles)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Eliminar usuario"""
    user = User.query.get_or_404(user_id)
    
    # No permitir eliminar el propio usuario
    if user.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta.', 'error')
        return redirect(url_for('admin_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    log_activity('user_deleted', {'deleted_user': username})
    
    flash(f'Usuario {username} eliminado exitosamente.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/roles')
@admin_required
def admin_roles():
    """Página de gestión de roles"""
    roles = Role.query.all()
    return render_template('admin/roles.html', roles=roles, permissions=PERMISSIONS)

@app.route('/admin/activity')
@admin_required
def admin_activity():
    """Redirigir a la página principal con la pestaña de administración"""
    return redirect(url_for('index', section='admin'))

# --- RUTAS API PARA ADMINISTRACIÓN ---
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def api_get_users():
    """API para obtener lista de usuarios"""
    users = User.query.all()
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
            'role_name': user.role.name,
            'role_id': user.role_id,
            'is_active': user.is_active,
            'last_login': user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else None,
            'created_at': user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else None
        })
    return jsonify({'success': True, 'users': users_data})

@app.route('/api/admin/roles', methods=['GET'])
@admin_required
def api_get_roles():
    """API para obtener lista de roles"""
    roles = Role.query.all()
    roles_data = []
    for role in roles:
        roles_data.append({
            'id': role.id,
            'name': role.name,
            'description': role.description
        })
    return jsonify({'success': True, 'roles': roles_data})

@app.route('/api/admin/activity', methods=['GET'])
@admin_required
def api_get_activity():
    """API para obtener actividad de usuarios"""
    activities = UserActivity.query.order_by(UserActivity.timestamp.desc()).limit(100).all()
    activity_data = []
    for activity in activities:
        activity_data.append({
            'id': activity.id,
            'username': activity.user.username,
            'full_name': activity.user.get_full_name(),
            'action': activity.action,
            'details': activity.details,
            'ip_address': activity.ip_address,
            'timestamp': activity.timestamp.strftime('%d/%m/%Y %H:%M:%S')
        })
    return jsonify({'success': True, 'activities': activity_data})

@app.route('/api/admin/users', methods=['POST'])
@admin_required
def api_create_user():
    """API para crear usuario"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        role_id = data.get('role_id')
        
        # Validaciones
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'error': 'El nombre de usuario ya existe'})
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'El email ya está registrado'})
        
        # Crear usuario
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role_id=role_id,
            created_by=current_user.id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        log_activity('user_created', {
            'created_user': username,
            'role_id': role_id
        })
        
        return jsonify({'success': True, 'message': 'Usuario creado exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def api_update_user(user_id):
    """API para actualizar usuario"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        user.username = data.get('username')
        user.email = data.get('email')
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.role_id = data.get('role_id')
        user.is_active = data.get('is_active', True)
        
        # Cambiar contraseña si se proporciona
        new_password = data.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        
        log_activity('user_updated', {
            'updated_user': user.username,
            'role_id': user.role_id
        })
        
        return jsonify({'success': True, 'message': 'Usuario actualizado exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    """API para eliminar usuario"""
    try:
        user = User.query.get_or_404(user_id)
        
        # No permitir eliminar el propio usuario
        if user.id == current_user.id:
            return jsonify({'success': False, 'error': 'No puedes eliminar tu propia cuenta'})
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        log_activity('user_deleted', {'deleted_user': username})
        
        return jsonify({'success': True, 'message': f'Usuario {username} eliminado exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    with app.app_context():
        create_tables_and_roles()
    app.run(debug=True, host='0.0.0.0', port=5000)
