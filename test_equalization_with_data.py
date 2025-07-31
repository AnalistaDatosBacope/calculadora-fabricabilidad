#!/usr/bin/env python3
"""
Script para probar el equilibrado de stock con datos reales
"""
import os
import sys
import pandas as pd
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app
from calculadora_core import CalculadoraCore

def test_equalization_with_real_data():
    """Prueba el equilibrado con datos reales"""
    print("=== PRUEBA DE EQUILIBRADO CON DATOS REALES ===")
    
    # Buscar archivos de datos
    data_cache_dir = "data_cache"
    if not os.path.exists(data_cache_dir):
        print("❌ Directorio data_cache no encontrado")
        return
    
    # Buscar archivos más recientes
    suppliers_files = [f for f in os.listdir(data_cache_dir) if 'suppliers' in f and f.endswith('.feather')]
    sales_files = [f for f in os.listdir(data_cache_dir) if 'sales' in f and f.endswith('.feather')]
    boms_files = [f for f in os.listdir(data_cache_dir) if 'boms' in f and f.endswith('.pkl')]
    stock_files = [f for f in os.listdir(data_cache_dir) if 'stock' in f and f.endswith('.pkl')]
    costs_files = [f for f in os.listdir(data_cache_dir) if 'costs' in f and f.endswith('.pkl')]
    
    print(f"Archivos encontrados:")
    print(f"  - Suppliers: {suppliers_files}")
    print(f"  - Sales: {sales_files}")
    print(f"  - BOMs: {boms_files}")
    print(f"  - Stock: {stock_files}")
    print(f"  - Costs: {costs_files}")
    
    # Cargar datos
    test_data = {}
    
    # Cargar suppliers
    if suppliers_files:
        latest_suppliers = max(suppliers_files, key=lambda f: os.path.getmtime(os.path.join(data_cache_dir, f)))
        suppliers_path = os.path.join(data_cache_dir, latest_suppliers)
        test_data['suppliers_df'] = pd.read_feather(suppliers_path)
        print(f"✅ Suppliers cargado: {test_data['suppliers_df'].shape}")
    else:
        print("❌ No se encontraron archivos de suppliers")
        return
    
    # Cargar sales
    if sales_files:
        latest_sales = max(sales_files, key=lambda f: os.path.getmtime(os.path.join(data_cache_dir, f)))
        sales_path = os.path.join(data_cache_dir, latest_sales)
        test_data['sales_df'] = pd.read_feather(sales_path)
        print(f"✅ Sales cargado: {test_data['sales_df'].shape}")
    else:
        print("❌ No se encontraron archivos de sales")
        test_data['sales_df'] = pd.DataFrame()
    
    # Cargar BOMs
    if boms_files:
        latest_boms = max(boms_files, key=lambda f: os.path.getmtime(os.path.join(data_cache_dir, f)))
        boms_path = os.path.join(data_cache_dir, latest_boms)
        import pickle
        with open(boms_path, 'rb') as f:
            test_data['boms'] = pickle.load(f)
        print(f"✅ BOMs cargado: {len(test_data['boms'])} modelos")
    else:
        print("❌ No se encontraron archivos de BOMs")
        test_data['boms'] = {}
    
    # Cargar stock
    if stock_files:
        latest_stock = max(stock_files, key=lambda f: os.path.getmtime(os.path.join(data_cache_dir, f)))
        stock_path = os.path.join(data_cache_dir, latest_stock)
        import pickle
        with open(stock_path, 'rb') as f:
            test_data['stock'] = pickle.load(f)
        print(f"✅ Stock cargado: {len(test_data['stock'])} artículos")
    else:
        print("❌ No se encontraron archivos de stock")
        test_data['stock'] = {}
    
    # Cargar costs
    if costs_files:
        latest_costs = max(costs_files, key=lambda f: os.path.getmtime(os.path.join(data_cache_dir, f)))
        costs_path = os.path.join(data_cache_dir, latest_costs)
        import pickle
        with open(costs_path, 'rb') as f:
            test_data['costs'] = pickle.load(f)
        print(f"✅ Costs cargado: {len(test_data['costs'])} artículos")
    else:
        print("❌ No se encontraron archivos de costs")
        test_data['costs'] = {}
    
    # Crear instancia de CalculadoraCore
    print(f"\nCreando instancia de CalculadoraCore...")
    core = CalculadoraCore(test_data)
    print(f"✅ CalculadoraCore creada")
    print(f"  - Suppliers_df vacío: {core.suppliers_df.empty}")
    print(f"  - Sales_df vacío: {core.sales_df.empty}")
    print(f"  - BOMs vacío: {len(core.boms) == 0}")
    print(f"  - Stock vacío: {len(core.stock) == 0}")
    print(f"  - Costs vacío: {len(core.costs) == 0}")
    
    # Probar equilibrado
    print(f"\nProbando equilibrado de stock...")
    try:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        # Obtener modelos disponibles
        available_models = list(core.boms.keys()) if core.boms else ['TEST_MODEL']
        if not available_models:
            available_models = ['TEST_MODEL']
        
        print(f"Modelos disponibles: {available_models[:5]}...")  # Mostrar solo los primeros 5
        
        result = core.calculate_stock_equalization(available_models[:1], start_date, end_date)
        print(f"✅ Equilibrado ejecutado")
        print(f"Resultado: {result.message}")
        
        if hasattr(result, 'component_summaries') and result.component_summaries:
            print(f"Componentes procesados: {len(result.component_summaries)}")
        if hasattr(result, 'total_cost_after_equalization'):
            print(f"Costo total: {result.total_cost_after_equalization}")
            
    except Exception as e:
        print(f"❌ Error en equilibrado: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== FIN DE PRUEBA ===")

if __name__ == "__main__":
    test_equalization_with_real_data() 