#!/usr/bin/env python3
"""
Script para crear archivos Excel de prueba válidos
"""
import pandas as pd
import os

def create_test_files():
    """Crear archivos Excel de prueba válidos"""
    
    print("📁 Creando archivos Excel de prueba...")
    
    # Crear archivo de ventas
    sales_data = {
        'FECHA': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
        'COD_PROD': ['A001', 'A002', 'A001', 'A003'],
        'Descripción': ['Producto A', 'Producto B', 'Producto A', 'Producto C'],
        'VENTA': [100, 150, 120, 80]
    }
    sales_df = pd.DataFrame(sales_data)
    sales_df['FECHA'] = pd.to_datetime(sales_df['FECHA'])
    sales_df.to_excel('test_sales.xlsx', index=False)
    print("   ✅ test_sales.xlsx creado")
    
    # Crear archivo de proveedores
    suppliers_data = {
        'Artículo': ['A001', 'A002', 'A003'],
        'Descripción': ['Producto A', 'Producto B', 'Producto C'],
        'Código': ['PROV001', 'PROV002', 'PROV003'],
        'Razón Social': ['Proveedor 1', 'Proveedor 2', 'Proveedor 3'],
        'Precio': [10.50, 15.75, 12.25]
    }
    suppliers_df = pd.DataFrame(suppliers_data)
    suppliers_df.to_excel('test_suppliers.xlsx', index=False)
    print("   ✅ test_suppliers.xlsx creado")
    
    # Crear archivo de histórico de costos
    historico_data = {
        'Artículo': ['A001', 'A002', 'A003'],
        '2023': [10.00, 15.00, 12.00],
        '2024': [10.50, 15.75, 12.25]
    }
    historico_df = pd.DataFrame(historico_data)
    historico_df.to_excel('test_historico.xlsx', index=False)
    print("   ✅ test_historico.xlsx creado")
    
    print("\n📋 Archivos creados:")
    print("   - test_sales.xlsx (Ventas)")
    print("   - test_suppliers.xlsx (Proveedores)")
    print("   - test_historico.xlsx (Histórico de Costos)")
    
    print("\n💡 Instrucciones:")
    print("   1. Ve a https://calculadora-fabricabilidad.onrender.com")
    print("   2. Inicia sesión con admin/admin123")
    print("   3. Sube estos archivos uno por uno")
    print("   4. Verifica que los badges cambien a 'Cargado'")
    
    return True

if __name__ == "__main__":
    create_test_files() 