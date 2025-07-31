import pandas as pd
import openpyxl
import os
import unicodedata # Importar para la normalización de cadenas
from data_models import BomItem, StockItem, LotItem, SupplierItem # Asegúrate de que estas clases estén definidas en data_models.py

def normalize_string(s):
    """
    Normaliza una cadena: convierte a minúsculas, elimina acentos y reemplaza espacios por guiones bajos.
    """
    if isinstance(s, str):
        s = s.lower().strip()
        # Eliminar acentos
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        # Reemplazar espacios por guiones bajos
        s = s.replace(' ', '_')
    return s

class FileParser:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def parse_file(self, file, file_key):
        file_path = os.path.join(self.upload_folder, file.filename)
        file.save(file_path)

        try:
            if file_key == 'bom_file':
                return self._parse_bom(file_path)
            elif file_key == 'stock_file':
                return self._parse_stock(file_path)
            elif file_key == 'lot_file':
                return self._parse_lot(file_path)
            elif file_key == 'cost_file':
                return self._parse_costs(file_path)
            elif file_key == 'sales_file':
                return self._parse_sales_history(file_path)
            elif file_key == 'suppliers_file': # Nuevo caso para el archivo de proveedores
                return self._parse_suppliers(file_path)
            elif file_key == 'historico_costos_file':
                return self._parse_historico_costos(file_path)
            else:
                raise ValueError(f"Tipo de archivo desconocido: {file_key}")
        finally:
            # Asegurarse de que el archivo temporal se elimine siempre
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return None

    def _parse_historico_costos(self, file_path):
        """
        Lee el archivo Historico Costos.xlsx, convierte '-' a NaN, valores a float, y devuelve un DataFrame limpio.
        """
        df = pd.read_excel(file_path, sheet_name=0)
        # Reemplazar '-' por NaN
        df = df.replace('-', pd.NA)
        # Convertir columnas de años a float (excepto la primera columna, que es el artículo)
        for col in df.columns[1:]:
            # Extraer solo el valor numérico si hay 'USD' en la celda
            df[col] = df[col].astype(str).str.replace('USD', '').str.replace(',', '.').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df

    def _parse_bom(self, file_path):
        """
        Lee el BOM sin encabezados y filtra por la letra 'A'.
        Asigna nombres de columna explícitos y elimina las columnas vacías.
        Columnas esperadas (índices base 0):
        0: Modelo (cod_prod_padre)
        1: Descripción Modelo
        2: Vacia (eliminar)
        3: Vacia (eliminar)
        4: Letra (para filtrar por 'A')
        5: Artículo (cod_prod_hijo)
        6: Descripción Artículo
        7: Vacia (eliminar)
        8: Vacia (eliminar)
        9: Unidad
        10: Cantidad (cantidad_hijo)
        """
        try:
            column_names = [
                "modelo",
                "descripcion_modelo",
                "col2",
                "col3",
                "ok",
                "articulo",
                "descripcion_articulo",
                "col7",
                "col8",
                "unidad",
                "cantidad"
            ]
            df = pd.read_excel(file_path, header=None, names=column_names)
            # Eliminar columnas vacías
            df = df.drop(columns=["col2", "col3", "col7", "col8"])

            # Validar que el DataFrame tenga suficientes columnas
            if df.shape[1] < 7:
                raise ValueError("El archivo BOM debe tener al menos 7 columnas útiles después de limpiar. Columnas encontradas: " + str(df.shape[1]))

            boms = {}
            for index, row in df.iterrows():
                try:
                    letra = str(row["ok"]).strip().upper()
                    if letra == 'A':
                        padre = str(row["modelo"]).strip()
                        hijo = str(row["articulo"]).strip()
                        cantidad = float(row["cantidad"])
                        descripcion_modelo = str(row["descripcion_modelo"]).strip() if not pd.isna(row["descripcion_modelo"]) else ""
                        descripcion_articulo = str(row["descripcion_articulo"]).strip() if not pd.isna(row["descripcion_articulo"]) else ""
                        unidad = str(row["unidad"]).strip() if not pd.isna(row["unidad"]) else ""

                        if not padre or not hijo or pd.isna(cantidad):
                            continue

                        if padre not in boms:
                            boms[padre] = []
                        boms[padre].append(BomItem(
                            cod_prod_padre=padre,
                            cod_prod_hijo=hijo,
                            cantidad_hijo=cantidad,
                            descripcion_modelo=descripcion_modelo,
                            descripcion_articulo=descripcion_articulo,
                            unidad=unidad
                        ))
                except ValueError as ve:
                    raise ValueError(f"Error de formato en la fila {index+1} del archivo BOM: {ve}. Asegúrate de que las columnas de cantidad sean numéricas.")
                except Exception as e:
                    raise Exception(f"Error inesperado al procesar la fila {index+1} del archivo BOM: {e}")

            if not boms:
                raise ValueError("El archivo BOM no contiene datos válidos o ninguna fila con la letra 'A' en la columna 5.")
            return boms
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo BOM está vacío.")
        except Exception as e:
            raise Exception(f"Error al procesar el archivo BOM: {e}")

    def _parse_stock(self, file_path):
        """
        Lee el archivo de Stock con los encabezados 'Artículo' y 'Existencia'.
        """
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip() # Limpiar espacios en los nombres de columna

            # --- Nombres de columna esperados ---
            col_articulo = 'Artículo'
            col_existencia = 'Existencia'

            # Validar que las columnas necesarias existan
            if col_articulo not in df.columns:
                raise ValueError(f"Columna '{col_articulo}' no encontrada en el archivo de Stock. Columnas disponibles: {list(df.columns)}")
            if col_existencia not in df.columns:
                raise ValueError(f"Columna '{col_existencia}' no encontrada en el archivo de Stock. Columnas disponibles: {list(df.columns)}")

            stock_dict = {}
            for index, row in df.iterrows():
                try:
                    codigo = str(row[col_articulo]).strip()
                    stock = float(row[col_existencia])

                    if not codigo or pd.isna(stock):
                        # print(f"Advertencia: Fila {index+1} del Stock contiene datos faltantes o inválidos y será omitida.")
                        continue

                    stock_dict[codigo] = stock
                except ValueError as ve:
                    raise ValueError(f"Error de formato en la fila {index+1} del archivo de Stock: {ve}. Asegúrate de que la columna 'Existencia' sea numérica.")
                except Exception as e:
                    raise Exception(f"Error inesperado al procesar la fila {index+1} del archivo de Stock: {e}")
            
            if not stock_dict:
                raise ValueError("El archivo de Stock no contiene datos válidos.")
            return stock_dict
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo de Stock está vacío.")
        except Exception as e:
            raise Exception(f"Error al procesar el archivo de Stock: {e}")

    def _parse_lot(self, file_path):
        """
        Lee el archivo de Lote (con encabezados).
        Columnas esperadas: 'LOTE', 'COD_PROD', 'CANTIDAD'.
        """
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()

            # --- Nombres de columna esperados ---
            col_lote = 'LOTE'
            col_cod_prod = 'COD_PROD'
            col_cantidad = 'CANTIDAD'

            # Validar que las columnas necesarias existan
            if col_lote not in df.columns:
                raise ValueError(f"Columna '{col_lote}' no encontrada en el archivo de Lote. Columnas disponibles: {list(df.columns)}")
            if col_cod_prod not in df.columns:
                raise ValueError(f"Columna '{col_cod_prod}' no encontrada en el archivo de Lote. Columnas disponibles: {list(df.columns)}")
            if col_cantidad not in df.columns:
                raise ValueError(f"Columna '{col_cantidad}' no encontrada en el archivo de Lote. Columnas disponibles: {list(df.columns)}")

            lots = []
            for index, row in df.iterrows():
                try:
                    lote = str(row[col_lote]).strip()
                    cod_prod = str(row[col_cod_prod]).strip()
                    cantidad = int(row[col_cantidad])

                    if not lote or not cod_prod or pd.isna(cantidad):
                        # print(f"Advertencia: Fila {index+1} del Lote contiene datos faltantes o inválidos y será omitida.")
                        continue
                    
                    lots.append(LotItem(
                        lote=lote,
                        cod_prod=cod_prod,
                        cantidad=cantidad
                    ))
                except ValueError as ve:
                    raise ValueError(f"Error de formato en la fila {index+1} del archivo de Lote: {ve}. Asegúrate de que la columna 'CANTIDAD' sea numérica entera.")
                except Exception as e:
                    raise Exception(f"Error inesperado al procesar la fila {index+1} del archivo de Lote: {e}")
            
            if not lots:
                raise ValueError("El archivo de Lote no contiene datos válidos.")
            return lots
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo de Lote está vacío.")
        except Exception as e:
            raise Exception(f"Error al procesar el archivo de Lote: {e}")

    def _parse_costs(self, file_path):
        """
        Lee el archivo de Costos con los encabezados 'Código' e 'Importe'.
        """
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()

            # --- Nombres de columna esperados ---
            columna_codigo = 'Código'
            columna_costo = 'Importe'

            if columna_codigo not in df.columns:
                raise ValueError(f"Columna '{columna_codigo}' no encontrada en el archivo de Costos. Columnas disponibles: {list(df.columns)}")
            if columna_costo not in df.columns:
                raise ValueError(f"Columna '{columna_costo}' no encontrada en el archivo de Costos. Columnas disponibles: {list(df.columns)}")

            costs_dict = {}
            for index, row in df.iterrows():
                try:
                    codigo = str(row[columna_codigo]).strip()
                    costo = float(row[columna_costo])

                    if not codigo or pd.isna(costo):
                        # print(f"Advertencia: Fila {index+1} de Costos contiene datos faltantes o inválidos y será omitida.")
                        continue
                    
                    costs_dict[codigo] = costo
                except ValueError as ve:
                    raise ValueError(f"Error de formato en la fila {index+1} del archivo de Costos: {ve}. Asegúrate de que la columna 'Importe' sea numérica.")
                except Exception as e:
                    raise Exception(f"Error inesperado al procesar la fila {index+1} del archivo de Costos: {e}")
            
            if not costs_dict:
                raise ValueError("El archivo de Costos no contiene datos válidos.")
            return costs_dict
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo de Costos está vacío.")
        except Exception as e:
            raise Exception(f"Error al procesar el archivo de Costos: {e}")

    def _parse_sales_history(self, file_path):
        """
        Lee el archivo de Ventas (con encabezados).
        Permite configurar los nombres de las columnas desde aquí.
        Columnas esperadas: 'Fecha', 'MODELO', 'CANTIDAD'.
        """
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()

            # --- AJUSTA ESTOS TRES NOMBRES SEGÚN TU ARCHIVO EXCEL DE VENTAS ---
            nombre_columna_fecha = 'Fecha'
            nombre_columna_codigo = 'MODELO'
            nombre_columna_venta = 'CANTIDAD'

            # Verificamos que las columnas necesarias existan
            columnas_requeridas = [nombre_columna_fecha, nombre_columna_codigo, nombre_columna_venta]
            for col in columnas_requeridas:
                if col not in df.columns:
                    raise ValueError(f"La columna requerida '{col}' no se encontró en el archivo de Ventas. Columnas encontradas: {list(df.columns)}")

            # Renombramos las columnas a los nombres estándar que usa la aplicación internamente
            df.rename(columns={
                nombre_columna_fecha: 'FECHA',
                nombre_columna_codigo: 'COD_PROD',
                nombre_columna_venta: 'VENTA'
            }, inplace=True)

            # Convertimos la columna de fecha ya con su nombre estándar
            # errors='coerce' convertirá los valores no válidos a NaT (Not a Time)
            df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

            # Eliminar filas donde la fecha es NaT (no se pudo parsear)
            df.dropna(subset=['FECHA'], inplace=True)

            # Validar que la columna 'VENTA' sea numérica
            if not pd.api.types.is_numeric_dtype(df['VENTA']):
                # Intentar convertir a numérico, forzando errores a NaN
                df['VENTA'] = pd.to_numeric(df['VENTA'], errors='coerce')
                df.dropna(subset=['VENTA'], inplace=True) # Eliminar filas con ventas no numéricas
                if df['VENTA'].empty:
                    raise ValueError("La columna 'CANTIDAD' en el archivo de Ventas no contiene valores numéricos válidos.")

            if df.empty:
                raise ValueError("El archivo de Ventas no contiene datos válidos después de la limpieza.")

            return df
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo de Ventas está vacío.")
        except Exception as e:
            raise Exception(f"Error al procesar el archivo de Ventas: {e}")

    def _parse_suppliers(self, file_path):
        """
        Lee el archivo de Proveedores.
        Columnas esperadas: 'Artículo', 'Descripción', 'Código', 'Razón Social', 'Precio'.
        """
        try:
            df = pd.read_excel(file_path)
            df.columns = [normalize_string(col) for col in df.columns] # Normalizar todos los nombres de columna

            # --- Nombres de columna esperados (ahora normalizados) ---
            expected_columns = ['articulo', 'descripcion', 'codigo', 'razon_social', 'precio']

            # Validar que todas las columnas necesarias existan
            for col in expected_columns:
                if col not in df.columns:
                    # Si la columna 'razon_social' no se encuentra, intentar con 'razon_social' (sin normalizar)
                    # Esto es un fallback si el normalize_string no funciona como se espera para ese caso específico
                    if col == 'razon_social' and 'razon social' in df.columns:
                        df.rename(columns={'razon social': 'razon_social'}, inplace=True)
                    else:
                        raise ValueError(f"La columna requerida '{col}' no se encontró en el archivo de Proveedores. Columnas disponibles: {list(df.columns)}")

            # Convertir la columna 'precio' a numérica, forzando errores a NaN
            df['precio'] = pd.to_numeric(df['precio'], errors='coerce')
            # Eliminar filas donde 'precio' no es un número válido
            df.dropna(subset=['precio'], inplace=True)

            # Validar que las columnas de texto no estén vacías
            for col in ['articulo', 'descripcion', 'codigo', 'razon_social']:
                df[col] = df[col].astype(str).str.strip()
                df = df[df[col] != ''] # Eliminar filas con valores vacíos en estas columnas

            if df.empty:
                raise ValueError("El archivo de Proveedores no contiene datos válidos después de la limpieza.")
            
            return df
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo de Proveedores está vacío.")
        except Exception as e:
            raise Exception(f"Error al procesar el archivo de Proveedores: {e}")
            # Eliminar columnas vacías
            df = df.drop(columns=["col2", "col3", "col7", "col8"])

            # Validar que el DataFrame tenga suficientes columnas
            if df.shape[1] < 7:
                raise ValueError("El archivo BOM debe tener al menos 7 columnas útiles después de limpiar. Columnas encontradas: " + str(df.shape[1]))

            boms = {}
            for index, row in df.iterrows():
                try:
                    letra = str(row["ok"]).strip().upper()
                    if letra == 'A':
                        padre = str(row["modelo"]).strip()
                        hijo = str(row["articulo"]).strip()
                        cantidad = float(row["cantidad"])
                        descripcion_modelo = str(row["descripcion_modelo"]).strip() if not pd.isna(row["descripcion_modelo"]) else ""
                        descripcion_articulo = str(row["descripcion_articulo"]).strip() if not pd.isna(row["descripcion_articulo"]) else ""
                        unidad = str(row["unidad"]).strip() if not pd.isna(row["unidad"]) else ""

                        if not padre or not hijo or pd.isna(cantidad):
                            continue

                        if padre not in boms:
                            boms[padre] = []
                        boms[padre].append(BomItem(
                            cod_prod_padre=padre,
                            cod_prod_hijo=hijo,
                            cantidad_hijo=cantidad,
                            descripcion_modelo=descripcion_modelo,
                            descripcion_articulo=descripcion_articulo,
                            unidad=unidad
                        ))
                except ValueError as ve:
                    raise ValueError(f"Error de formato en la fila {index+1} del archivo BOM: {ve}. Asegúrate de que las columnas de cantidad sean numéricas.")
                except Exception as e:
                    raise Exception(f"Error inesperado al procesar la fila {index+1} del archivo BOM: {e}")

            if not boms:
                raise ValueError("El archivo BOM no contiene datos válidos o ninguna fila con la letra 'A' en la columna 5.")
            return boms
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo BOM está vacío.")
        except Exception as e:
            raise Exception(f"Error al procesar el archivo BOM: {e}")

    def _parse_stock(self, file_path):
        """
        Lee el archivo de Stock con los encabezados 'Artículo' y 'Existencia'.
        """
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip() # Limpiar espacios en los nombres de columna

            # --- Nombres de columna esperados ---
            col_articulo = 'Artículo'
            col_existencia = 'Existencia'

            # Validar que las columnas necesarias existan
            if col_articulo not in df.columns:
                raise ValueError(f"Columna '{col_articulo}' no encontrada en el archivo de Stock. Columnas disponibles: {list(df.columns)}")
            if col_existencia not in df.columns:
                raise ValueError(f"Columna '{col_existencia}' no encontrada en el archivo de Stock. Columnas disponibles: {list(df.columns)}")

            stock_dict = {}
            for index, row in df.iterrows():
                try:
                    codigo = str(row[col_articulo]).strip()
                    stock = float(row[col_existencia])

                    if not codigo or pd.isna(stock):
                        # print(f"Advertencia: Fila {index+1} del Stock contiene datos faltantes o inválidos y será omitida.")
                        continue

                    stock_dict[codigo] = stock
                except ValueError as ve:
                    raise ValueError(f"Error de formato en la fila {index+1} del archivo de Stock: {ve}. Asegúrate de que la columna 'Existencia' sea numérica.")
                except Exception as e:
                    raise Exception(f"Error inesperado al procesar la fila {index+1} del archivo de Stock: {e}")
            
            if not stock_dict:
                raise ValueError("El archivo de Stock no contiene datos válidos.")
            return stock_dict
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo de Stock está vacío.")
        except Exception as e:
            raise Exception(f"Error al procesar el archivo de Stock: {e}")

    def _parse_lot(self, file_path):
        """
        Lee el archivo de Lote (con encabezados).
        Columnas esperadas: 'LOTE', 'COD_PROD', 'CANTIDAD'.
        """
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()

            # --- Nombres de columna esperados ---
            col_lote = 'LOTE'
            col_cod_prod = 'COD_PROD'
            col_cantidad = 'CANTIDAD'

            # Validar que las columnas necesarias existan
            if col_lote not in df.columns:
                raise ValueError(f"Columna '{col_lote}' no encontrada en el archivo de Lote. Columnas disponibles: {list(df.columns)}")
            if col_cod_prod not in df.columns:
                raise ValueError(f"Columna '{col_cod_prod}' no encontrada en el archivo de Lote. Columnas disponibles: {list(df.columns)}")
            if col_cantidad not in df.columns:
                raise ValueError(f"Columna '{col_cantidad}' no encontrada en el archivo de Lote. Columnas disponibles: {list(df.columns)}")

            lots = []
            for index, row in df.iterrows():
                try:
                    lote = str(row[col_lote]).strip()
                    cod_prod = str(row[col_cod_prod]).strip()
                    cantidad = int(row[col_cantidad])

                    if not lote or not cod_prod or pd.isna(cantidad):
                        # print(f"Advertencia: Fila {index+1} del Lote contiene datos faltantes o inválidos y será omitida.")
                        continue
                    
                    lots.append(LotItem(
                        lote=lote,
                        cod_prod=cod_prod,
                        cantidad=cantidad
                    ))
                except ValueError as ve:
                    raise ValueError(f"Error de formato en la fila {index+1} del archivo de Lote: {ve}. Asegúrate de que la columna 'CANTIDAD' sea numérica entera.")
                except Exception as e:
                    raise Exception(f"Error inesperado al procesar la fila {index+1} del archivo de Lote: {e}")
            
            if not lots:
                raise ValueError("El archivo de Lote no contiene datos válidos.")
            return lots
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo de Lote está vacío.")
        except Exception as e:
            raise Exception(f"Error al procesar el archivo de Lote: {e}")

    def _parse_costs(self, file_path):
        """
        Lee el archivo de Costos con los encabezados 'Código' e 'Importe'.
        """
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()

            # --- Nombres de columna esperados ---
            columna_codigo = 'Código'
            columna_costo = 'Importe'

            if columna_codigo not in df.columns:
                raise ValueError(f"Columna '{columna_codigo}' no encontrada en el archivo de Costos. Columnas disponibles: {list(df.columns)}")
            if columna_costo not in df.columns:
                raise ValueError(f"Columna '{columna_costo}' no encontrada en el archivo de Costos. Columnas disponibles: {list(df.columns)}")

            costs_dict = {}
            for index, row in df.iterrows():
                try:
                    codigo = str(row[columna_codigo]).strip()
                    costo = float(row[columna_costo])

                    if not codigo or pd.isna(costo):
                        # print(f"Advertencia: Fila {index+1} de Costos contiene datos faltantes o inválidos y será omitida.")
                        continue
                    
                    costs_dict[codigo] = costo
                except ValueError as ve:
                    raise ValueError(f"Error de formato en la fila {index+1} del archivo de Costos: {ve}. Asegúrate de que la columna 'Importe' sea numérica.")
                except Exception as e:
                    raise Exception(f"Error inesperado al procesar la fila {index+1} del archivo de Costos: {e}")
            
            if not costs_dict:
                raise ValueError("El archivo de Costos no contiene datos válidos.")
            return costs_dict
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo de Costos está vacío.")
        except Exception as e:
            raise Exception(f"Error al procesar el archivo de Costos: {e}")

    def _parse_sales_history(self, file_path):
        """
        Lee el archivo de Ventas (con encabezados).
        Permite configurar los nombres de las columnas desde aquí.
        Columnas esperadas: 'Fecha', 'MODELO', 'CANTIDAD'.
        """
        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()

            # --- AJUSTA ESTOS TRES NOMBRES SEGÚN TU ARCHIVO EXCEL DE VENTAS ---
            nombre_columna_fecha = 'Fecha'
            nombre_columna_codigo = 'MODELO'
            nombre_columna_venta = 'CANTIDAD'

            # Verificamos que las columnas necesarias existan
            columnas_requeridas = [nombre_columna_fecha, nombre_columna_codigo, nombre_columna_venta]
            for col in columnas_requeridas:
                if col not in df.columns:
                    raise ValueError(f"La columna requerida '{col}' no se encontró en el archivo de Ventas. Columnas encontradas: {list(df.columns)}")

            # Renombramos las columnas a los nombres estándar que usa la aplicación internamente
            df.rename(columns={
                nombre_columna_fecha: 'FECHA',
                nombre_columna_codigo: 'COD_PROD',
                nombre_columna_venta: 'VENTA'
            }, inplace=True)

            # Convertimos la columna de fecha ya con su nombre estándar
            # errors='coerce' convertirá los valores no válidos a NaT (Not a Time)
            df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

            # Eliminar filas donde la fecha es NaT (no se pudo parsear)
            df.dropna(subset=['FECHA'], inplace=True)

            # Validar que la columna 'VENTA' sea numérica
            if not pd.api.types.is_numeric_dtype(df['VENTA']):
                # Intentar convertir a numérico, forzando errores a NaN
                df['VENTA'] = pd.to_numeric(df['VENTA'], errors='coerce')
                df.dropna(subset=['VENTA'], inplace=True) # Eliminar filas con ventas no numéricas
                if df['VENTA'].empty:
                    raise ValueError("La columna 'CANTIDAD' en el archivo de Ventas no contiene valores numéricos válidos.")

            if df.empty:
                raise ValueError("El archivo de Ventas no contiene datos válidos después de la limpieza.")

            return df
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo de Ventas está vacío.")
        except Exception as e:
            raise Exception(f"Error al procesar el archivo de Ventas: {e}")

    def _parse_suppliers(self, file_path):
        """
        Lee el archivo de Proveedores.
        Columnas esperadas: 'Artículo', 'Descripción', 'Código', 'Razón Social', 'Precio'.
        """
        try:
            df = pd.read_excel(file_path)
            df.columns = [normalize_string(col) for col in df.columns] # Normalizar todos los nombres de columna

            # --- Nombres de columna esperados (ahora normalizados) ---
            expected_columns = ['articulo', 'descripcion', 'codigo', 'razon_social', 'precio']

            # Validar que todas las columnas necesarias existan
            for col in expected_columns:
                if col not in df.columns:
                    # Si la columna 'razon_social' no se encuentra, intentar con 'razon_social' (sin normalizar)
                    # Esto es un fallback si el normalize_string no funciona como se espera para ese caso específico
                    if col == 'razon_social' and 'razon social' in df.columns:
                        df.rename(columns={'razon social': 'razon_social'}, inplace=True)
                    else:
                        raise ValueError(f"La columna requerida '{col}' no se encontró en el archivo de Proveedores. Columnas disponibles: {list(df.columns)}")

            # Convertir la columna 'precio' a numérica, forzando errores a NaN
            df['precio'] = pd.to_numeric(df['precio'], errors='coerce')
            # Eliminar filas donde 'precio' no es un número válido
            df.dropna(subset=['precio'], inplace=True)

            # Validar que las columnas de texto no estén vacías
            for col in ['articulo', 'descripcion', 'codigo', 'razon_social']:
                df[col] = df[col].astype(str).str.strip()
                df = df[df[col] != ''] # Eliminar filas con valores vacíos en estas columnas

            if df.empty:
                raise ValueError("El archivo de Proveedores no contiene datos válidos después de la limpieza.")
            
            return df
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo de Proveedores está vacío.")
        except Exception as e:
            raise Exception(f"Error al procesar el archivo de Proveedores: {e}")
