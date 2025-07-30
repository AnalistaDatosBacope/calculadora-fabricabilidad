import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
# Importa las nuevas clases de data_models, incluyendo ModelFullCostResult
from data_models import BomItem, StockItem, LotItem, IndividualCalculationResult, PurchaseSuggestion, ComponentDetail, LotCalculationResult, DemandProjectionResult, ComponentDemandDetail, PurchaseSuggestionDemand, EqualizationComponentSummary, EqualizationResult, SupplierItem, ModelFullCostResult

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

class CalculadoraCore:
    def __init__(self, data_dict):
        # Inicialización de DataFrames y diccionarios con valores predeterminados vacíos
        # para evitar KeyError si un archivo no se carga.
        self.boms = data_dict.get('boms', {})
        self.stock = data_dict.get('stock', {})
        self.lots = data_dict.get('lots', [])
        self.costs = data_dict.get('costs', {})
        self.sales_df = data_dict.get('sales_df', pd.DataFrame())
        self.suppliers_df = data_dict.get('suppliers_df', pd.DataFrame()) # DataFrame de proveedores

        # Asegurarse de que sales_df tenga la columna 'FECHA' como datetime
        if not self.sales_df.empty and 'FECHA' in self.sales_df.columns:
            self.sales_df['FECHA'] = pd.to_datetime(self.sales_df['FECHA'], errors='coerce')
            self.sales_df.dropna(subset=['FECHA'], inplace=True) # Eliminar filas con fechas no válidas

    def calculate_individual_fabricability(self, model_name, desired_qty):
        if not self.boms:
            return IndividualCalculationResult(
                nombre_modelo=model_name,
                desired_qty=desired_qty,
                cantidad_fabricable=0,
                costo_total_modelo=0,
                costo_total_sugerencias=0,
                sugerencias_compra=[],
                detalle_componentes=[],
                mensaje="Error: BOM no cargado."
            )
        if not self.stock:
            return IndividualCalculationResult(
                nombre_modelo=model_name,
                desired_qty=desired_qty,
                cantidad_fabricable=0,
                costo_total_modelo=0,
                costo_total_sugerencias=0,
                sugerencias_compra=[],
                detalle_componentes=[],
                mensaje="Error: Stock no cargado."
            )
        if not self.costs:
            return IndividualCalculationResult(
                nombre_modelo=model_name,
                desired_qty=desired_qty,
                cantidad_fabricable=0,
                costo_total_modelo=0,
                costo_total_sugerencias=0,
                sugerencias_compra=[],
                detalle_componentes=[],
                mensaje="Error: Costos no cargados."
            )

        if model_name not in self.boms:
            return IndividualCalculationResult(
                nombre_modelo=model_name,
                desired_qty=desired_qty,
                cantidad_fabricable=0,
                costo_total_modelo=0,
                costo_total_sugerencias=0,
                sugerencias_compra=[],
                detalle_componentes=[],
                mensaje=f"Error: Modelo '{model_name}' no encontrado en el BOM."
            )

        bom_for_model = self.boms[model_name]
        
        # Calcular la cantidad fabricable del modelo
        max_fabricable = float('inf')
        component_details = []
        total_model_cost = 0.0

        for item in bom_for_model:
            required = item.cantidad_hijo * desired_qty
            available_stock = self.stock.get(item.cod_prod_hijo, 0)
            
            costo_unitario = self.costs.get(item.cod_prod_hijo, 0.0)
            
            # Calcular la cantidad fabricable basada en este componente
            if item.cantidad_hijo > 0: # Evitar división por cero
                fabricable_by_component = available_stock / item.cantidad_hijo
                max_fabricable = min(max_fabricable, fabricable_by_component)
            else:
                # Si la cantidad requerida es 0, no limita la producción
                pass

            # Detalle para el reporte
            component_details.append(ComponentDetail(
                articulo=item.cod_prod_hijo,
                articulo_descripcion=item.descripcion_articulo if hasattr(item, 'descripcion_articulo') and item.descripcion_articulo else "Descripción no disponible (desde BOM)",
                cantidad_requerida_total=required,
                cantidad_disponible_stock=available_stock,
                cantidad_faltante=max(0, required - available_stock),
                costo_unitario=costo_unitario,
                costo_total=required * costo_unitario # Costo total de este componente para la cantidad deseada
            ))
            total_model_cost += (required * costo_unitario) # Sumar al costo total del modelo

        cantidad_fabricable = int(max_fabricable) if max_fabricable != float('inf') else 0

        # Calcular sugerencias de compra y costo total de sugerencias
        purchase_suggestions = []
        total_suggestions_cost = 0.0

        for detail in component_details:
            if detail.cantidad_faltante > 0:
                purchase_suggestions.append(PurchaseSuggestion(
                    articulo=detail.articulo,
                    cantidad_necesaria=detail.cantidad_faltante,
                    costo_unitario=detail.costo_unitario, # Asumimos costo unitario consistente
                    costo_total=detail.cantidad_faltante * detail.costo_unitario
                ))
                total_suggestions_cost += (detail.cantidad_faltante * detail.costo_unitario)
            
        return IndividualCalculationResult(
            nombre_modelo=model_name,
            desired_qty=desired_qty,
            cantidad_fabricable=cantidad_fabricable,
            costo_total_modelo=total_model_cost,
            costo_total_sugerencias=total_suggestions_cost,
            sugerencias_compra=purchase_suggestions,
            detalle_componentes=component_details,
            mensaje="" # Mensaje vacío si no hay errores
        )

    def calculate_lot_fabricability(self):
        if not self.boms:
            return {"error": "BOM no cargado."}
        if not self.stock:
            return {"error": "Stock no cargado."}
        if not self.lots:
            return {"error": "Lote no cargado."}
        if not self.costs:
            return {"error": "Costos no cargados."}

        lot_results = {}
        all_purchase_suggestions = {} # Para consolidar sugerencias de todo el lote

        for lot_item in self.lots:
            model_name = lot_item.cod_prod
            desired_qty = lot_item.cantidad
            
            # Reutilizar la lógica de cálculo individual
            result = self.calculate_individual_fabricability(model_name, desired_qty)
            
            if result.mensaje and "error" in result.mensaje.lower(): # Si hay un error en el cálculo individual
                lot_results[model_name] = {"error": result.mensaje}
                continue

            lot_results[model_name] = result # Almacenar el objeto IndividualCalculationResult

            # Consolidar sugerencias de compra
            for suggestion in result.sugerencias_compra:
                if suggestion.articulo not in all_purchase_suggestions:
                    all_purchase_suggestions[suggestion.articulo] = {
                        "articulo": suggestion.articulo,
                        "cantidad_necesaria": 0.0,
                        "costo_unitario": suggestion.costo_unitario, # Asumimos costo unitario consistente
                        "costo_total": 0.0
                    }
                all_purchase_suggestions[suggestion.articulo]["cantidad_necesaria"] += suggestion.cantidad_necesaria
                all_purchase_suggestions[suggestion.articulo]["costo_total"] += suggestion.costo_total
        
        # Convertir sugerencias consolidadas a objetos PurchaseSuggestion
        consolidated_suggestions_objects = {
            k: PurchaseSuggestion(**v) for k, v in all_purchase_suggestions.items()
        }

        return {"results": lot_results, "suggestions": consolidated_suggestions_objects}

    def proyectar_demanda_futura(self, selected_models, start_date, end_date):
        logging.info(f"\n{'='*50}")
        logging.info(f"=== PROYECCIÓN DE DEMANDA ===")
        logging.info(f"Modelos seleccionados: {selected_models}")
        logging.info(f"Rango de proyección: {start_date} a {end_date}")
        logging.info(f"{'='*50}")
        logging.info("🚀 FUNCIÓN EJECUTÁNDOSE - DEBERÍAS VER ESTE MENSAJE EN EL TERMINAL")

        # Lista de feriados nacionales de Argentina (ejemplo 2024, puedes actualizarla cada año)
        feriados = [
            '2024-01-01', '2024-02-12', '2024-02-13', '2024-03-24', '2024-03-29', '2024-04-01',
            '2024-04-02', '2024-05-01', '2024-05-25', '2024-06-17', '2024-06-20', '2024-07-09',
            '2024-08-19', '2024-10-14', '2024-11-18', '2024-12-08', '2024-12-25',
            # Agrega más feriados si es necesario
        ]
        feriados = pd.to_datetime(feriados)

        if self.sales_df.empty:
            logging.error("DEBUG: Error - No hay historial de ventas cargado.")
            return DemandProjectionResult(mensaje="error: No hay historial de ventas cargado para proyectar la demanda.")
        if not self.boms:
            logging.error("DEBUG: Error - BOM no cargado.")
            return DemandProjectionResult(mensaje="error: BOM no cargado para proyectar la demanda.")
        if not self.stock:
            logging.error("DEBUG: Error - Stock no cargado.")
            return DemandProjectionResult(mensaje="error: Stock no cargado para proyectar la demanda.")
        if not self.costs:
            logging.error("DEBUG: Error - Costos no cargados.")
            return DemandProjectionResult(mensaje="error: Costos no cargados para proyectar la demanda.")

        # Asegurarse de que las fechas sean objetos datetime.date
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        logging.info(f"Fechas parseadas - Inicio: {start_date}, Fin: {end_date}")

        # Filtrar ventas por los modelos seleccionados del historial COMPLETO
        logging.info("Filtrando ventas por modelos seleccionados...")
        filtered_sales_for_models = self.sales_df[self.sales_df['COD_PROD'].isin(selected_models)].copy()
        logging.info(f"Ventas históricas totales para modelos seleccionados: {len(filtered_sales_for_models)} registros")

        if filtered_sales_for_models.empty:
            logging.warning("INFO: No hay datos de ventas para los modelos seleccionados en todo el historial.")
            return DemandProjectionResult(mensaje="info: No hay datos de ventas para los modelos seleccionados en el historial.")

        # Calcular el número de días hábiles en el período de proyección
        logging.info("Calculando días hábiles de proyección...")
        rango_proyeccion = pd.date_range(start=start_date, end=end_date, freq='B')
        rango_proyeccion = rango_proyeccion[~rango_proyeccion.isin(feriados)]
        dias_habiles_proyeccion = len(rango_proyeccion)
        logging.info(f"Días hábiles en el rango de proyección: {dias_habiles_proyeccion}")

        if dias_habiles_proyeccion <= 0:
            logging.error("ERROR: El rango de fechas de proyección no tiene días hábiles válidos.")
            return DemandProjectionResult(
                projection_period=0,
                sugerencias_agrupadas={},
                mensaje="Error: El rango de fechas de proyección no tiene días hábiles válidos."
            )

        # Determinar el rango de meses y días del período de proyección (fuera del bucle)
        start_month, start_day = start_date.month, start_date.day
        end_month, end_day = end_date.month, end_date.day
        logging.info(f"Rango de proyección: {start_month}/{start_day} a {end_month}/{end_day}")

        sugerencias_agrupadas = {}
        modelos_sin_ventas = []

        logging.info("Iniciando procesamiento de modelos...")
        for model_code in selected_models:
            logging.info(f"\n--- Modelo: {model_code} ---")
            componentes_necesarios_para_modelo = []
            logging.info(f"Filtrando ventas para modelo {model_code}...")
            ventas_historicas_modelo = filtered_sales_for_models[filtered_sales_for_models['COD_PROD'] == model_code]
            logging.info(f"Ventas encontradas para {model_code}: {len(ventas_historicas_modelo)} registros")

            if ventas_historicas_modelo.empty:
                logging.warning(f"Sin ventas históricas para el modelo '{model_code}' en el historial total.")
                sugerencias_agrupadas[model_code] = {
                    "demanda_proyectada_modelo": 0,
                    "componentes_necesarios": []
                }
                modelos_sin_ventas.append(model_code)
                continue

            # Filtrar ventas históricas SOLO para el mismo rango de fechas de cada año
            logging.info(f"Procesando fechas para {model_code}...")
            ventas_historicas_modelo['anio'] = ventas_historicas_modelo['FECHA'].dt.year
            ventas_historicas_modelo['mes'] = ventas_historicas_modelo['FECHA'].dt.month
            ventas_historicas_modelo['dia'] = ventas_historicas_modelo['FECHA'].dt.day
            logging.info(f"Años únicos en ventas de {model_code}: {ventas_historicas_modelo['anio'].unique()}")

            # NO filtrar por rango de fechas para el cálculo del promedio diario
            # Usar TODOS los datos históricos para calcular el promedio diario real
            logging.info(f"Usando TODOS los datos históricos para calcular promedio diario de {model_code}")
            logging.info(f"Total registros históricos para {model_code}: {len(ventas_historicas_modelo)}")

            # Solo considerar días hábiles históricos (lunes a viernes, excluyendo feriados)
            logging.info(f"Filtrando días hábiles para {model_code}...")
            ventas_historicas_modelo = ventas_historicas_modelo[ventas_historicas_modelo['FECHA'].dt.weekday < 5]
            logging.info(f"Ventas después de filtrar días hábiles: {len(ventas_historicas_modelo)} registros")
            ventas_historicas_modelo = ventas_historicas_modelo[~ventas_historicas_modelo['FECHA'].isin(feriados)]
            logging.info(f"Ventas después de excluir feriados: {len(ventas_historicas_modelo)} registros")

            # Calcular todos los días hábiles históricos para TODO el año de cada año
            logging.info(f"Calculando días hábiles históricos para {model_code}...")
            dias_habiles_historicos = 0
            for anio in ventas_historicas_modelo['anio'].unique():
                # Usar TODO el año para calcular días hábiles históricos
                fecha_ini = date(anio, 1, 1)
                fecha_fin = date(anio, 12, 31)
                logging.info(f"Calculando días hábiles para año {anio}: {fecha_ini} a {fecha_fin}")
                rango = pd.date_range(start=fecha_ini, end=fecha_fin, freq='B')
                # Excluir feriados
                rango = rango[~rango.isin(feriados)]
                dias_habiles_anio = len(rango)
                dias_habiles_historicos += dias_habiles_anio
                logging.info(f"Días hábiles para {anio}: {dias_habiles_anio}")
            logging.info(f"Total días hábiles históricos para {model_code}: {dias_habiles_historicos}")

            total_ventas_historicas = ventas_historicas_modelo['VENTA'].sum()
            logging.info(f"Total ventas históricas hábiles para '{model_code}': {total_ventas_historicas}")
            logging.info(f"Total días hábiles históricos para '{model_code}': {dias_habiles_historicos}")

            promedio_venta_diaria_historica = 0
            if dias_habiles_historicos > 0:
                promedio_venta_diaria_historica = total_ventas_historicas / dias_habiles_historicos
            logging.info(f"Promedio venta diaria hábil histórica para '{model_code}': {promedio_venta_diaria_historica}")

            # Proyección: promedio diario hábil histórico × días hábiles en el rango futuro
            demanda_proyectada_modelo = promedio_venta_diaria_historica * dias_habiles_proyeccion
            logging.info(f"Demanda proyectada total para '{model_code}': {demanda_proyectada_modelo}")
            logging.info(f"DEBUG: {promedio_venta_diaria_historica} × {dias_habiles_proyeccion} = {demanda_proyectada_modelo}")
            
            # Mostrar algunos datos de ventas históricas para verificar
            if not ventas_historicas_modelo.empty:
                logging.info(f"DEBUG: Ventas históricas por año para '{model_code}':")
                for anio in ventas_historicas_modelo['anio'].unique():
                    ventas_anio = ventas_historicas_modelo[ventas_historicas_modelo['anio'] == anio]['VENTA'].sum()
                    logging.info(f"  {anio}: {ventas_anio} unidades")

            if demanda_proyectada_modelo == 0:
                sugerencias_agrupadas[model_code] = {
                    "demanda_proyectada_modelo": 0,
                    "componentes_necesarios": []
                }
                continue

            bom_modelo = self.boms.get(model_code)
            if not bom_modelo:
                print(f"ERROR: Modelo '{model_code}' no encontrado en el BOM para proyección de componentes.")
                sugerencias_agrupadas[model_code] = {
                    "demanda_proyectada_modelo": demanda_proyectada_modelo,
                    "componentes_necesarios": [],
                    "mensaje": f"Modelo '{model_code}' no encontrado en el BOM. No se pueden proyectar componentes."
                }
                continue

            for item in bom_modelo:
                componente_articulo = item.cod_prod_hijo
                cantidad_requerida_por_modelo = item.cantidad_hijo
                # (Eliminado print de cada componente para no llenar el log)
                demanda_proyectada_componente = demanda_proyectada_modelo * cantidad_requerida_por_modelo
                stock_actual = self.stock.get(componente_articulo, 0)
                costo_unitario = self.costs.get(componente_articulo, 0)
                cantidad_a_comprar = max(0, demanda_proyectada_componente - stock_actual)
                costo_total_compra = cantidad_a_comprar * costo_unitario
                descripcion_articulo = item.descripcion_articulo if hasattr(item, 'descripcion_articulo') and item.descripcion_articulo else "Descripción no disponible (desde BOM)"
                componentes_necesarios_para_modelo.append(ComponentDemandDetail(
                    articulo=componente_articulo,
                    articulo_descripcion=descripcion_articulo,
                    stock_actual=stock_actual,
                    demanda_proyectada_componente=demanda_proyectada_componente,
                    cantidad_a_comprar=cantidad_a_comprar,
                    costo_total_compra=costo_total_compra
                ))
            sugerencias_agrupadas[model_code] = {
                "demanda_proyectada_modelo": int(round(demanda_proyectada_modelo)),
                "componentes_necesarios": componentes_necesarios_para_modelo
            }
        print(f"{'='*50}")
        print("=== FIN PROYECCIÓN DE DEMANDA ===")
        print(f"{'='*50}\n")
        mensaje = None
        if modelos_sin_ventas:
            mensaje = f"info: Los siguientes modelos no tienen datos históricos de ventas en el rango seleccionado: {', '.join(modelos_sin_ventas)}."
        return DemandProjectionResult(
            projection_period=dias_habiles_proyeccion, # Ahora es la cantidad de días hábiles del rango
            sugerencias_agrupadas=sugerencias_agrupadas,
            mensaje=mensaje # Mensaje vacío si hay resultados
        )

    def calculate_stock_equalization(self, selected_models, start_date, end_date):
        print(f"DEBUG: Iniciando calculate_stock_equalization para modelos: {selected_models}")
        print(f"DEBUG: Rango de fechas de equilibrado: {start_date} a {end_date}")

        if self.sales_df.empty:
            print("DEBUG: Error - No hay historial de ventas cargado para equilibrado.")
            return EqualizationResult(message="error: No hay historial de ventas cargado para proyectar la demanda.")
        if not self.boms:
            print("DEBUG: Error - BOM no cargado para equilibrado.")
            return EqualizationResult(message="error: BOM no cargado para proyectar la demanda.")
        if not self.stock:
            print("DEBUG: Error - Stock no cargado para equilibrado.")
            return EqualizationResult(message="error: Stock no cargado para proyectar la demanda.")
        if not self.costs:
            print("DEBUG: Error - Costos no cargados para equilibrado.")
            return EqualizationResult(message="error: Costos no cargados para proyectar la demanda.")
        if self.suppliers_df.empty:
            print("DEBUG: Error - DataFrame de proveedores vacío para equilibrado.")
            return EqualizationResult(message="error: No hay datos de proveedores cargados para el equilibrado.")

        # Calcular el período de proyección en meses
        delta = relativedelta(end_date, start_date)
        num_months_projection = delta.years * 12 + delta.months + 1
        print(f"DEBUG: Período de proyección para equilibrado (meses): {num_months_projection}")
        
        # Primero, calculamos la demanda proyectada para todos los modelos seleccionados
        print("DEBUG: Llamando a proyectar_demanda_futura desde calculate_stock_equalization...")
        demand_projection_result = self.proyectar_demanda_futura(selected_models, start_date, end_date)
        print(f"DEBUG: Resultado de proyectar_demanda_futura: {demand_projection_result.to_dict()}")
        
        if demand_projection_result.mensaje and "error" in demand_projection_result.mensaje.lower():
            print(f"DEBUG: Error en la proyección de demanda: {demand_projection_result.mensaje}")
            return EqualizationResult(message=demand_projection_result.mensaje)
        
        # Consolidar la demanda total de componentes de todos los modelos seleccionados
        global_component_demand = {} # {articulo: demanda_total_proyectada}
        print("DEBUG: Consolidando demanda global de componentes...")

        if not demand_projection_result.sugerencias_agrupadas:
            print("DEBUG: No hay sugerencias agrupadas en el resultado de la proyección de demanda.")
            return EqualizationResult(
                component_summaries=[],
                total_cost_after_equalization=0.0,
                message="No se generaron sugerencias de demanda para los modelos seleccionados. Verifique los datos de ventas y BOMs.",
                projection_period_months=num_months_projection
            )

        for model_data in demand_projection_result.sugerencias_agrupadas.values():
            for comp_detail in model_data.get('componentes_necesarios', []):
                articulo = comp_detail.articulo
                demanda_proyectada = comp_detail.demanda_proyectada_componente
                if articulo not in global_component_demand:
                    global_component_demand[articulo] = 0.0
                global_component_demand[articulo] += demanda_proyectada
        print(f"DEBUG: Demanda global de componentes consolidada: {global_component_demand}")

        component_summaries = []
        total_cost_after_equalization = 0.0

        print("DEBUG: Calculando stock ideal y compras necesarias por componente...")
        for articulo, demanda_proyectada_global in global_component_demand.items():
            stock_actual_global = self.stock.get(articulo, 0.0)

            # Obtener el costo desde la lista de costos
            costo_unitario_lista_costos = self.costs.get(articulo, float('inf'))
            proveedor_lista_costos = "N/A"
            codigo_proveedor_lista_costos = "N/A"

            # Buscar en la lista de proveedores el proveedor cuyo precio coincida con el costo de la lista de costos
            suppliers_for_article = self.suppliers_df[self.suppliers_df['articulo'] == articulo]
            if not suppliers_for_article.empty:
                # Buscar coincidencia exacta o muy cercana (por decimales)
                match = suppliers_for_article[abs(suppliers_for_article['precio'] - costo_unitario_lista_costos) < 1e-4]
                if not match.empty:
                    # Tomar el primer proveedor que coincida
                    row = match.iloc[0]
                    proveedor_lista_costos = row['razon_social']
                    codigo_proveedor_lista_costos = str(row['codigo'])
                else:
                    print(f"DEBUG: No se encontró proveedor con precio igual al de la lista de costos para '{articulo}'. Se usará 'N/A'.")
            else:
                print(f"DEBUG: No se encontró proveedor para el artículo '{articulo}'.")

            excedente_global = max(0, stock_actual_global - demanda_proyectada_global)
            deficit_global = max(0, demanda_proyectada_global - stock_actual_global)
            cantidad_a_comprar_final = deficit_global
            costo_total_compra_final = cantidad_a_comprar_final * costo_unitario_lista_costos
            total_cost_after_equalization += costo_total_compra_final

            component_summaries.append(EqualizationComponentSummary(
                articulo=articulo,
                articulo_descripcion=suppliers_for_article.iloc[0]['descripcion'] if not suppliers_for_article.empty else "Descripción no disponible",
                demanda_total=demanda_proyectada_global,
                stock_disponible=stock_actual_global,
                cantidad_faltante_original=deficit_global,
                razon_social_proveedor_final=proveedor_lista_costos,
                codigo_proveedor_final=codigo_proveedor_lista_costos,
                costo_unitario_proveedor_final=costo_unitario_lista_costos,
                cantidad_a_comprar_final=cantidad_a_comprar_final,
                costo_total_compra_final=costo_total_compra_final
            ))
        component_summaries.sort(key=lambda x: x.cantidad_a_comprar_final, reverse=True)
        print(f"DEBUG: Resumen de componentes para equilibrado finalizado: {component_summaries}")

        final_message = "Cálculo de equilibrado de stock completado."
        if not component_summaries:
            final_message = "No se encontraron componentes faltantes después de la proyección de demanda para la igualación, o el stock actual cubre todas las necesidades."
        print(f"DEBUG: Mensaje final de EqualizationResult: {final_message}")
        return EqualizationResult(
            component_summaries=component_summaries,
            total_cost_after_equalization=total_cost_after_equalization,
            message=final_message,
            projection_period_months=num_months_projection
        )

    def calculate_model_full_cost(self, model_name: str, quantity: int):
        """
        Calcula el costo total de fabricar una cantidad específica de un modelo,
        basándose únicamente en el BOM y los costos de los componentes, sin considerar el stock.
        """
        print(f"DEBUG: Iniciando calculate_model_full_cost para modelo='{model_name}', cantidad={quantity}")

        if not self.boms:
            print("DEBUG: Error - BOM no cargado.")
            return ModelFullCostResult(
                nombre_modelo=model_name,
                cantidad_modelo=quantity,
                costo_total_fabricacion=0.0,
                detalle_componentes=[],
                mensaje="Error: BOM no cargado."
            )
        if not self.costs:
            print("DEBUG: Error - Costos no cargados.")
            return ModelFullCostResult(
                nombre_modelo=model_name,
                cantidad_modelo=quantity,
                costo_total_fabricacion=0.0,
                detalle_componentes=[],
                mensaje="Error: Costos no cargados."
            )

        if model_name not in self.boms:
            print(f"DEBUG: Error - Modelo '{model_name}' no encontrado en el BOM.")
            return ModelFullCostResult(
                nombre_modelo=model_name,
                cantidad_modelo=quantity,
                costo_total_fabricacion=0.0,
                detalle_componentes=[],
                mensaje=f"Error: Modelo '{model_name}' no encontrado en el BOM."
            )

        bom_for_model = self.boms[model_name]
        print(f"DEBUG: BOM para '{model_name}': {bom_for_model}")
        
        total_fabrication_cost = 0.0
        component_details = []

        for item in bom_for_model:
            articulo = item.cod_prod_hijo
            cantidad_requerida_por_modelo = item.cantidad_hijo
            
            print(f"DEBUG: Procesando componente '{articulo}' (cantidad por modelo: {cantidad_requerida_por_modelo})")
            
            # Cantidad total de este componente necesaria para la cantidad deseada del modelo
            total_required_component_qty = cantidad_requerida_por_modelo * quantity
            print(f"DEBUG: Cantidad total requerida de '{articulo}': {total_required_component_qty}")
            
            costo_unitario = self.costs.get(articulo, 0.0)
            print(f"DEBUG: Costo unitario de '{articulo}': {costo_unitario}")
            
            # Costo total de este componente para la cantidad deseada del modelo
            costo_total_componente = total_required_component_qty * costo_unitario
            print(f"DEBUG: Costo total de componente '{articulo}': {costo_total_componente}")
            
            total_fabrication_cost += costo_total_componente

            component_details.append(ComponentDetail(
                articulo=articulo,
                articulo_descripcion=item.descripcion_articulo if hasattr(item, 'descripcion_articulo') and item.descripcion_articulo else "Descripción no disponible (desde BOM)",
                cantidad_requerida_total=total_required_component_qty,
                cantidad_disponible_stock=0, # No relevante para este cálculo de costo total de fabricación
                cantidad_faltante=total_required_component_qty, # Se considera todo faltante para el costo de fabricación
                costo_unitario=costo_unitario,
                costo_total=costo_total_componente
            ))
        
        print(f"DEBUG: Costo total de fabricación final para '{model_name}': {total_fabrication_cost}")
        return ModelFullCostResult(
            nombre_modelo=model_name,
            cantidad_modelo=quantity,
            costo_total_fabricacion=total_fabrication_cost,
            detalle_componentes=component_details,
            mensaje="" # Mensaje vacío si no hay errores
        )
