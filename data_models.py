from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

@dataclass
class BomItem:
    cod_prod_padre: str
    cod_prod_hijo: str
    cantidad_hijo: float
    descripcion_modelo: str = ""
    descripcion_articulo: str = ""
    unidad: str = ""

    def to_dict(self):
        return {
            "cod_prod_padre": self.cod_prod_padre,
            "cod_prod_hijo": self.cod_prod_hijo,
            "cantidad_hijo": self.cantidad_hijo,
            "descripcion_modelo": self.descripcion_modelo,
            "descripcion_articulo": self.descripcion_articulo,
            "unidad": self.unidad
        }

@dataclass
class StockItem:
    cod_producto: str
    stock: float

@dataclass
class LotItem:
    lote: str
    cod_prod: str
    cantidad: int

# --- CLASES PARA ESTRUCTURAR RESULTADOS ---

@dataclass
class PurchaseSuggestion:
    articulo: str
    cantidad_necesaria: float
    costo_unitario: float
    costo_total: float

    def to_dict(self):
        return asdict(self)

@dataclass
class ComponentDetail:
    articulo: str
    articulo_descripcion: str
    cantidad_requerida_total: float
    cantidad_disponible_stock: float
    cantidad_faltante: float
    costo_unitario: float
    costo_total: float

    def to_dict(self):
        return asdict(self)

@dataclass
class IndividualCalculationResult:
    nombre_modelo: str
    desired_qty: int
    cantidad_fabricable: int
    costo_total_modelo: float
    costo_total_sugerencias: float
    sugerencias_compra: List[PurchaseSuggestion] = field(default_factory=list)
    detalle_componentes: List[ComponentDetail] = field(default_factory=list)
    mensaje: str = ""

    def to_dict(self):
        return {
            "nombre_modelo": self.nombre_modelo,
            "desired_qty": self.desired_qty,
            "cantidad_fabricable": self.cantidad_fabricable,
            "costo_total_modelo": self.costo_total_modelo,
            "costo_total_sugerencias": self.costo_total_sugerencias,
            "sugerencias_compra": [s.to_dict() for s in self.sugerencias_compra],
            "detalle_componentes": [d.to_dict() for d in self.detalle_componentes],
            "mensaje": self.mensaje
        }

@dataclass
class LotCalculationResult:
    results: Dict[str, IndividualCalculationResult] = field(default_factory=dict)
    suggestions: Dict[str, PurchaseSuggestion] = field(default_factory=dict)
    mensaje: str = ""

    def to_dict(self):
        return {
            "results": {k: v.to_dict() for k, v in self.results.items()},
            "suggestions": {k: v.to_dict() for k, v in self.suggestions.items()},
            "mensaje": self.mensaje
        }

@dataclass
class ComponentDemandDetail:
    articulo: str
    stock_actual: float
    demanda_proyectada_componente: float
    cantidad_a_comprar: float
    costo_total_compra: float
    articulo_descripcion: str = ""

    def to_dict(self):
        return asdict(self)

@dataclass
class PurchaseSuggestionDemand:
    articulo: str
    articulo_descripcion: str
    cantidad_requerida_total: float
    cantidad_disponible_stock: float
    cantidad_faltante: float
    costo_unitario: float
    costo_total: float

    def to_dict(self):
        return asdict(self)

@dataclass
class DemandProjectionResult:
    model_name: str = ""
    start_date: Any = None
    end_date: Any = None
    projection_period: int = 0
    sugerencias_agrupadas: Dict[str, Any] = field(default_factory=dict)
    total_sales: float = 0.0
    mensaje: str = ""

    def to_dict(self):
        sugerencias_agrupadas_dict = {}
        for model, data in self.sugerencias_agrupadas.items():
            comp_list = []
            for comp in data.get("componentes_necesarios", []):
                if isinstance(comp, ComponentDemandDetail):
                    comp_list.append(comp.to_dict())
                else:
                    comp_list.append(comp)
            sugerencias_agrupadas_dict[model] = {
                "demanda_proyectada_modelo": data.get("demanda_proyectada_modelo", 0),
                "componentes_necesarios": comp_list,
                "mensaje": data.get("mensaje", "")
            }

        return {
            "model_name": self.model_name,
            "start_date": str(self.start_date) if self.start_date else None,
            "end_date": str(self.end_date) if self.end_date else None,
            "projection_period": self.projection_period,
            "sugerencias_agrupadas": sugerencias_agrupadas_dict,
            "total_sales": self.total_sales,
            "mensaje": self.mensaje
        }

@dataclass
class EqualizationComponentSummary:
    articulo: str
    articulo_descripcion: str = ""
    demanda_total: float = 0.0  # Added default value
    stock_disponible: float = 0.0  # Added default value
    cantidad_faltante_original: float = 0.0  # Added default value
    razon_social_proveedor_final: str = "N/A"  # Added default value
    codigo_proveedor_final: str = "N/A"  # Added default value
    costo_unitario_proveedor_final: float = 0.0  # Added default value
    cantidad_a_comprar_final: float = 0.0  # Added default value
    costo_total_compra_final: float = 0.0  # Added default value

    def to_dict(self):
        return {
            "articulo": self.articulo,
            "articulo_descripcion": self.articulo_descripcion,
            "demanda_total": f"{self.demanda_total:.2f}",
            "stock_disponible": f"{self.stock_disponible:.2f}",
            "cantidad_faltante_original": f"{self.cantidad_faltante_original:.2f}",
            "razon_social_proveedor_final": self.razon_social_proveedor_final,
            "codigo_proveedor_final": self.codigo_proveedor_final,
            "costo_unitario_proveedor_final": f"{self.costo_unitario_proveedor_final:.2f}",
            "cantidad_a_comprar_final": f"{self.cantidad_a_comprar_final:.2f}",
            "costo_total_compra_final": f"{self.costo_total_compra_final:.2f}"
        }

@dataclass
class EqualizationResult:
    component_summaries: List[EqualizationComponentSummary] = field(default_factory=list)
    total_cost_after_equalization: float = 0.0
    message: str = ""
    projection_period_months: int = 0

    def to_dict(self):
        return {
            "component_summaries": [c.to_dict() for c in self.component_summaries],
            "total_cost_after_equalization": f"{self.total_cost_after_equalization:.2f}",
            "message": self.message,
            "projection_period_months": self.projection_period_months
        }

@dataclass
class SupplierItem:
    articulo: str
    descripcion: str
    codigo: str
    razon_social: str
    precio: float

    def to_dict(self):
        return asdict(self)

# --- NUEVA CLASE PARA EL COSTO TOTAL DE FABRICACIÓN DE UN MODELO ---
@dataclass
class ModelFullCostResult:
    nombre_modelo: str
    cantidad_modelo: int
    costo_total_fabricacion: float
    detalle_componentes: List[ComponentDetail] = field(default_factory=list)
    mensaje: str = ""

    def to_dict(self):
        return {
            "nombre_modelo": self.nombre_modelo,
            "cantidad_modelo": self.cantidad_modelo,
            "costo_total_fabricacion": self.costo_total_fabricacion,
            "detalle_componentes": [d.to_dict() for d in self.detalle_componentes],
            "mensaje": self.mensaje
        }
