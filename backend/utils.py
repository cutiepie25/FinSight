"""
Módulo de utilidades: validaciones y exportación de datos.
"""

from typing import Dict, Any, Tuple
import pandas as pd
from io import BytesIO
import re
from datetime import datetime


def validar_parametros_credito(params: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Valida los parámetros de entrada para el cálculo de amortización.
    
    Args:
        params: Diccionario con parámetros del crédito
    
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    # Validar monto
    if "monto" not in params or params["monto"] <= 0:
        return False, "El monto debe ser mayor a 0"
    
    # Validar tasa
    if "tasa" not in params:
        return False, "Debe especificar una tasa de interés"
    
    if params["tasa"] < 0 or params["tasa"] > 100:
        return False, "La tasa debe estar entre 0 y 100%"
    
    # Validar tipo de tasa
    if "tipo_tasa" not in params or params["tipo_tasa"] not in ["nominal", "efectiva"]:
        return False, "El tipo de tasa debe ser 'nominal' o 'efectiva'"
    
    # Validar tipo de pago
    if "tipo_pago" not in params or params["tipo_pago"] not in ["anticipada", "vencida"]:
        return False, "El tipo de pago debe ser 'anticipada' o 'vencida'"
    
    # Validar plazo
    if "plazo_meses" not in params or params["plazo_meses"] <= 0:
        return False, "El plazo debe ser mayor a 0 meses"
    
    # Validar frecuencia
    frecuencias_validas = ["diaria", "quincenal", "mensual", "bimestral", 
                          "trimestral", "cuatrimestral", "semestral", "anual"]
    
    if "frecuencia_pago" not in params or params["frecuencia_pago"] not in frecuencias_validas:
        return False, f"La frecuencia de pago debe ser una de: {', '.join(frecuencias_validas)}"
    
    # Validar fecha
    if "fecha_inicio" not in params:
        return False, "Debe especificar una fecha de inicio"
    
    try:
        datetime.strptime(params["fecha_inicio"], "%Y-%m-%d")
    except ValueError:
        return False, "La fecha debe estar en formato YYYY-MM-DD"
    
    # Validar coherencia entre plazo y frecuencia
    from backend.calculos import FRECUENCIAS
    meses_por_periodo = FRECUENCIAS[params["frecuencia_pago"]]
    
    if params["plazo_meses"] < meses_por_periodo:
        return False, f"El plazo debe ser al menos {meses_por_periodo} meses para la frecuencia seleccionada"
    
    return True, "Parámetros válidos"


def validar_abono(periodo: int, monto: float, n_periodos_total: int) -> Tuple[bool, str]:
    """
    Valida un abono extraordinario.
    
    Args:
        periodo: Periodo en el que se hace el abono
        monto: Monto del abono
        n_periodos_total: Número total de periodos
    
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if periodo < 1 or periodo > n_periodos_total:
        return False, f"El periodo debe estar entre 1 y {n_periodos_total}"
    
    if monto <= 0:
        return False, "El monto del abono debe ser mayor a 0"
    
    return True, "Abono válido"


def exportar_a_csv(df: pd.DataFrame) -> bytes:
    """
    Exporta un DataFrame a CSV en bytes.
    
    Args:
        df: DataFrame a exportar
    
    Returns:
        Bytes del archivo CSV
    """
    return df.to_csv(index=False).encode('utf-8')


def exportar_a_excel(df: pd.DataFrame, nombre_hoja: str = "Amortización") -> bytes:
    """
    Exporta un DataFrame a Excel con formato.
    
    Args:
        df: DataFrame a exportar
        nombre_hoja: Nombre de la hoja de Excel
    
    Returns:
        Bytes del archivo Excel
    """
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre_hoja, index=False)
        
        # Obtener la hoja y aplicar formato
        workbook = writer.book
        worksheet = writer.sheets[nombre_hoja]
        
        # Ajustar ancho de columnas
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Aplicar formato a números (columnas numéricas)
        from openpyxl.styles import numbers
        
        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
            for cell in row:
                if isinstance(cell.value, (int, float)):
                    cell.number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
    
    output.seek(0)
    return output.getvalue()


def formatear_moneda(valor: float) -> str:
    """
    Formatea un valor como moneda.
    
    Args:
        valor: Valor numérico
    
    Returns:
        String formateado como moneda
    """
    return f"${valor:,.2f}"


def formatear_porcentaje(valor: float) -> str:
    """
    Formatea un valor como porcentaje.
    
    Args:
        valor: Valor decimal (ej: 0.12 para 12%)
    
    Returns:
        String formateado como porcentaje
    """
    return f"{valor * 100:.4f}%"


def calcular_resumen_credito(df: pd.DataFrame, monto_inicial: float) -> Dict[str, Any]:
    """
    Calcula un resumen del crédito a partir de la tabla de amortización.
    
    Args:
        df: DataFrame con tabla de amortización
        monto_inicial: Monto inicial del crédito
    
    Returns:
        Diccionario con resumen del crédito
    """
    total_intereses = df["Interes"].sum()
    total_abonos_extra = df["Abono_Extra"].sum()
    total_pagado = df["Cuota"].sum() + total_abonos_extra
    numero_cuotas = len(df)
    
    return {
        "monto_inicial": round(monto_inicial, 2),
        "total_intereses": round(total_intereses, 2),
        "total_abonos_extra": round(total_abonos_extra, 2),
        "total_pagado": round(total_pagado, 2),
        "numero_cuotas": numero_cuotas,
        "cuota_promedio": round(df["Cuota"].mean(), 2),
        "saldo_final": round(df.iloc[-1]["Saldo"], 2)
    }


def validar_frecuencia_abono(frecuencia_abono: str, frecuencia_pago: str) -> Tuple[bool, str]:
    """
    Valida que la frecuencia de abono sea compatible con la frecuencia de pago.
    
    Args:
        frecuencia_abono: Frecuencia del abono extraordinario
        frecuencia_pago: Frecuencia de pago del crédito
    
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    from backend.calculos import FRECUENCIAS
    
    if frecuencia_abono not in FRECUENCIAS:
        return False, f"Frecuencia de abono inválida: {frecuencia_abono}"
    
    if frecuencia_pago not in FRECUENCIAS:
        return False, f"Frecuencia de pago inválida: {frecuencia_pago}"
    
    meses_abono = FRECUENCIAS[frecuencia_abono]
    meses_pago = FRECUENCIAS[frecuencia_pago]
    
    # La frecuencia de abono debe ser múltiplo de la frecuencia de pago
    if meses_abono < meses_pago:
        return False, "La frecuencia de abono debe ser igual o mayor a la frecuencia de pago"
    
    # Verificar que sea múltiplo exacto
    if meses_abono % meses_pago != 0:
        return False, "La frecuencia de abono debe ser múltiplo exacto de la frecuencia de pago"
    
    return True, "Frecuencias compatibles"


def generar_reporte_comparativo(
    tabla_sin_abonos: pd.DataFrame,
    tabla_con_abonos: pd.DataFrame,
    monto_inicial: float
) -> Dict[str, Any]:
    """
    Genera un reporte comparativo entre escenarios con y sin abonos.
    
    Args:
        tabla_sin_abonos: Tabla sin abonos extraordinarios
        tabla_con_abonos: Tabla con abonos extraordinarios
        monto_inicial: Monto inicial del crédito
    
    Returns:
        Diccionario con comparación detallada
    """
    resumen_sin = calcular_resumen_credito(tabla_sin_abonos, monto_inicial)
    resumen_con = calcular_resumen_credito(tabla_con_abonos, monto_inicial)
    
    ahorro_intereses = resumen_sin["total_intereses"] - resumen_con["total_intereses"]
    reduccion_plazo = resumen_sin["numero_cuotas"] - resumen_con["numero_cuotas"]
    
    return {
        "sin_abonos": resumen_sin,
        "con_abonos": resumen_con,
        "ahorro_intereses": round(ahorro_intereses, 2),
        "ahorro_porcentual": round((ahorro_intereses / resumen_sin["total_intereses"]) * 100, 2),
        "reduccion_plazo_periodos": reduccion_plazo,
        "reduccion_plazo_porcentual": round((reduccion_plazo / resumen_sin["numero_cuotas"]) * 100, 2)
    }
