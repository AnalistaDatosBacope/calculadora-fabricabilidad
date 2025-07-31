#!/usr/bin/env python3
"""
Script para diagnosticar el estado de los archivos de proveedores
"""
import os
import sys
import pickle
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app, db, User

def check_suppliers_status():
    """Verifica el estado de los archivos de proveedores"""
    print("=== DIAGNÓSTICO DE ARCHIVOS DE PROVEEDORES ===")
    
    # 1. Verificar archivos en data_cache
    print("\n1. ARCHIVOS EN DATA_CACHE:")
    data_cache_dir = "data_cache"
    if os.path.exists(data_cache_dir):
        suppliers_files = [f for f in os.listdir(data_cache_dir) if 'suppliers' in f]
        print(f"   Archivos de proveedores encontrados: {suppliers_files}")
        
        for file in suppliers_files:
            file_path = os.path.join(data_cache_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"   - {file}: {file_size} bytes")
            
            # Intentar leer el archivo
            try:
                if file.endswith('.feather'):
                    df = pd.read_feather(file_path)
                    print(f"     ✅ Leído correctamente: {df.shape[0]} filas, {df.shape[1]} columnas")
                    print(f"     Columnas: {list(df.columns)}")
                    if not df.empty:
                        print(f"     Primeras filas:")
                        print(df.head(3).to_string())
                else:
                    print(f"     ⚠️  Formato no esperado: {file}")
            except Exception as e:
                print(f"     ❌ Error al leer: {e}")
    else:
        print("   ❌ Directorio data_cache no encontrado")
    
    # 2. Verificar base de datos de estado de archivos
    print("\n2. ESTADO EN BASE DE DATOS:")
    with app.app_context():
        try:
            from app import UserFileStatus
            suppliers_status = UserFileStatus.query.filter(
                UserFileStatus.file_type.like('%suppliers%')
            ).all()
            
            if suppliers_status:
                for status in suppliers_status:
                    print(f"   - Usuario {status.user_id}: {status.file_type}")
                    print(f"     Ruta: {status.file_path}")
                    print(f"     Subido: {status.uploaded_at}")
                    print(f"     Existe archivo: {os.path.exists(status.file_path)}")
            else:
                print("   ❌ No hay registros de archivos de proveedores en la base de datos")
        except Exception as e:
            print(f"   ❌ Error consultando base de datos: {e}")
    
    # 3. Simular carga de datos sin contexto de request
    print("\n3. SIMULACIÓN DE CARGA DE DATOS:")
    with app.app_context():
        try:
            # Buscar el archivo más reciente de proveedores
            suppliers_files = [f for f in os.listdir(data_cache_dir) if 'suppliers' in f and f.endswith('.feather')]
            if suppliers_files:
                # Tomar el archivo más reciente
                latest_file = max(suppliers_files, key=lambda f: os.path.getmtime(os.path.join(data_cache_dir, f)))
                latest_path = os.path.join(data_cache_dir, latest_file)
                print(f"   Archivo más reciente: {latest_file}")
                
                # Cargar el DataFrame
                suppliers_df = pd.read_feather(latest_path)
                print(f"   ✅ DataFrame cargado: {suppliers_df.shape[0]} filas, {suppliers_df.shape[1]} columnas")
                print(f"   Columnas: {list(suppliers_df.columns)}")
                print(f"   Vacío: {suppliers_df.empty}")
                
                # Crear una instancia de CalculadoraCore con estos datos
                from calculadora_core import CalculadoraCore
                test_data = {
                    'suppliers_df': suppliers_df,
                    'boms': {},
                    'stock': {},
                    'costs': {},
                    'sales_df': pd.DataFrame(),
                    'historico_costos_df': pd.DataFrame()
                }
                
                core = CalculadoraCore(test_data)
                print(f"   ✅ CalculadoraCore creada exitosamente")
                print(f"   Core.suppliers_df vacío: {core.suppliers_df.empty}")
                print(f"   Core.suppliers_df shape: {core.suppliers_df.shape}")
                
                # Probar la función de equilibrado
                print(f"\n4. PRUEBA DE FUNCIÓN DE EQUILIBRADO:")
                try:
                    from datetime import datetime, timedelta
                    start_date = datetime.now()
                    end_date = start_date + timedelta(days=30)
                    
                    result = core.calculate_stock_equalization(['TEST_MODEL'], start_date, end_date)
                    print(f"   ✅ Función de equilibrado ejecutada")
                    print(f"   Resultado: {result.message}")
                except Exception as e:
                    print(f"   ❌ Error en equilibrado: {e}")
                
            else:
                print("   ❌ No se encontraron archivos de proveedores")
        except Exception as e:
            print(f"   ❌ Error en simulación: {e}")
    
    print("\n=== FIN DEL DIAGNÓSTICO ===")

if __name__ == "__main__":
    check_suppliers_status() 