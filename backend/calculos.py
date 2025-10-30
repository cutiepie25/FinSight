"""
Módulo de cálculos financieros para tabla de amortización.
Incluye método Francés y conversión de tasas (nominal→efectiva, anticipada→vencida, equivalente).
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import pandas as pd

# -----------------------------
# MAPEO DE FRECUENCIAS A MESES
# -----------------------------
FRECUENCIAS = {
    "diaria": 1/30,
    "quincenal": 0.5,
    "mensual": 1,
    "bimestral": 2,
    "trimestral": 3,
    "cuatrimestral": 4,
    "semestral": 6,
    "anual": 12
}

# Mapeo de frecuencias a días (para conversión base 365)
FRECUENCIAS_DIAS = {
    "diaria": 1,
    "quincenal": 15,
    "mensual": 30,
    "bimestral": 60,
    "trimestral": 90,
    "cuatrimestral": 120,
    "semestral": 180,
    "anual": 365
}


def convertir_nominal_a_efectiva(tasa_nominal: float, m: int) -> float:
    """
    Convierte tasa nominal a efectiva.
    Fórmula: ie = (1 + in/m)^m - 1
    
    Args:
        tasa_nominal: Tasa nominal (decimal, ej: 0.12 para 12%)
        m: Número de capitalizaciones por año
    
    Returns:
        Tasa efectiva anual (decimal)
    """
    return (1 + tasa_nominal / m) ** m - 1


def convertir_anticipada_a_vencida(tasa_anticipada: float) -> float:
    """
    Convierte tasa anticipada a vencida.
    Fórmula: iv = ia / (1 + ia)
    
    Args:
        tasa_anticipada: Tasa anticipada (decimal)
    
    Returns:
        Tasa vencida (decimal)
    """
    return tasa_anticipada / (1 + tasa_anticipada)


def convertir_tasa_a_frecuencia_pago(tasa: float, frecuencia_origen: str, frecuencia_destino: str) -> float:
    """
    Convierte una tasa efectiva de una frecuencia a otra usando base diaria (365 días).
    Fórmula: ieq = (1 + i)^(frec_pago/365) - 1
    
    Args:
        tasa: Tasa efectiva en frecuencia origen (decimal)
        frecuencia_origen: Frecuencia de la tasa origen
        frecuencia_destino: Frecuencia de pago deseada
    
    Returns:
        Tasa equivalente en frecuencia destino (decimal)
    """
    dias_origen = FRECUENCIAS_DIAS[frecuencia_origen]
    dias_destino = FRECUENCIAS_DIAS[frecuencia_destino]
    
    # Convertir a tasa diaria primero
    tasa_diaria = (1 + tasa) ** (1 / dias_origen) - 1
    
    # Convertir a frecuencia destino
    tasa_destino = (1 + tasa_diaria) ** dias_destino - 1
    
    return tasa_destino


def convertir_tasa_efectiva(tasa: float, frecuencia_origen: str, frecuencia_destino: str) -> float:
    """
    Convierte una tasa efectiva de una frecuencia a otra usando meses.
    Ejemplo: de anual a mensual, o de trimestral a quincenal, etc.
    
    Args:
        tasa: Tasa efectiva en frecuencia origen (decimal)
        frecuencia_origen: Frecuencia de la tasa origen
        frecuencia_destino: Frecuencia de pago deseada
    
    Returns:
        Tasa equivalente en frecuencia destino (decimal)
    """
    meses_origen = FRECUENCIAS[frecuencia_origen]
    meses_destino = FRECUENCIAS[frecuencia_destino]
    tasa_destino = (1 + tasa) ** (meses_destino / meses_origen) - 1
    return tasa_destino


def calcular_cuota_frances(principal: float, tasa_periodo: float, n_periodos: int) -> float:
    """
    Calcula la cuota fija del método francés (cuota constante).
    Fórmula: C = P * [r * (1 + r)^n] / [(1 + r)^n - 1]
    
    Args:
        principal: Monto del préstamo
        tasa_periodo: Tasa de interés por periodo (decimal)
        n_periodos: Número de periodos
    
    Returns:
        Cuota fija por periodo
    """
    if tasa_periodo == 0:
        return principal / n_periodos
    
    cuota = principal * (tasa_periodo * (1 + tasa_periodo) ** n_periodos) / \
            ((1 + tasa_periodo) ** n_periodos - 1)
    return cuota


def redondear_decimal(valor: float, decimales: int = 2) -> float:
    """
    Redondea un valor usando Decimal para mayor precisión.
    
    Args:
        valor: Valor a redondear
        decimales: Número de decimales
    
    Returns:
        Valor redondeado
    """
    d = Decimal(str(valor))
    factor = Decimal(10) ** decimales
    return float(d.quantize(Decimal('1') / factor, rounding=ROUND_HALF_UP))


def generar_tabla_amortizacion(
    monto: float,
    tasa: float,
    tipo_tasa: str,
    tipo_pago: str,
    plazo_meses: int,
    frecuencia_pago: str,
    fecha_inicio: str,
    frecuencia_tasa: str = "anual"
) -> pd.DataFrame:
    """
    Genera la tabla de amortización completa usando método francés.
    
    Args:
        monto: Monto del préstamo
        tasa: Tasa de interés (en porcentaje, ej: 12 para 12%)
        tipo_tasa: "nominal" o "efectiva"
        tipo_pago: "anticipada" o "vencida"
        plazo_meses: Plazo total en meses
        frecuencia_pago: Frecuencia de los pagos
        fecha_inicio: Fecha de inicio del préstamo (YYYY-MM-DD)
        frecuencia_tasa: Frecuencia de la tasa dada (default: "anual")
    
    Returns:
        DataFrame con la tabla de amortización
    """
    # Convertir tasa de porcentaje a decimal
    tasa_decimal = tasa / 100
    
    # Paso 1: Convertir a tasa efectiva si es nominal
    if tipo_tasa == "nominal":
        # Determinar m según frecuencia de capitalización
        m_map = {"mensual": 12, "trimestral": 4, "semestral": 2, "anual": 1}
        m = m_map.get(frecuencia_tasa, 12)
        tasa_efectiva_anual = convertir_nominal_a_efectiva(tasa_decimal, m)
    else:
        tasa_efectiva_anual = tasa_decimal
    
    # Paso 2: Convertir de anticipada a vencida si es necesario
    if tipo_pago == "anticipada":
        tasa_efectiva_anual = convertir_anticipada_a_vencida(tasa_efectiva_anual)
    
    # Paso 3: Convertir a la frecuencia de pago
    if frecuencia_tasa == "anual":
        tasa_periodo = convertir_tasa_efectiva(tasa_efectiva_anual, "anual", frecuencia_pago)
    else:
        tasa_periodo = convertir_tasa_efectiva(tasa_efectiva_anual, frecuencia_tasa, frecuencia_pago)
    
    # Calcular número de periodos según frecuencia
    meses_por_periodo = FRECUENCIAS[frecuencia_pago]
    n_periodos = int(plazo_meses / meses_por_periodo)
    
    # Calcular cuota fija
    cuota = calcular_cuota_frances(monto, tasa_periodo, n_periodos)
    
    # Generar tabla periodo por periodo
    saldo = monto
    fecha_actual = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    filas = []
    
    for periodo in range(1, n_periodos + 1):
        # Calcular interés del periodo
        interes = saldo * tasa_periodo
        
        # Calcular abono a capital
        abono_capital = cuota - interes
        
        # Actualizar saldo
        saldo = saldo - abono_capital
        
        # Ajustar último periodo para cerrar en 0
        if periodo == n_periodos and abs(saldo) < 0.01:
            saldo = 0
        
        # Calcular fecha de pago
        dias_a_sumar = int(meses_por_periodo * 30)
        fecha_pago = fecha_actual + timedelta(days=dias_a_sumar)
        
        filas.append({
            "Periodo": periodo,
            "Fecha": fecha_pago.strftime("%Y-%m-%d"),
            "Cuota": redondear_decimal(cuota),
            "Interes": redondear_decimal(interes),
            "Abono_Capital": redondear_decimal(abono_capital),
            "Abono_Extra": 0.0,
            "Saldo": redondear_decimal(max(0, saldo))
        })
        
        fecha_actual = fecha_pago
        
        if saldo <= 0:
            break
    
    return pd.DataFrame(filas)


def recalcular_tabla_con_abonos(
    tabla_original: pd.DataFrame,
    abonos: List[Dict],
    tasa_periodo: float,
    opcion_recalculo: str = "reducir_cuota"
) -> pd.DataFrame:
    """
    Recalcula la tabla de amortización incorporando abonos extraordinarios.
    
    Args:
        tabla_original: DataFrame con tabla original
        abonos: Lista de diccionarios con {"periodo": int, "monto": float}
        tasa_periodo: Tasa de interés por periodo (decimal)
        opcion_recalculo: "reducir_cuota" o "reducir_plazo"
    
    Returns:
        DataFrame con tabla recalculada
    """
    # Convertir abonos a diccionario para búsqueda rápida
    abonos_dict = {a["periodo"]: a["monto"] for a in abonos}
    
    filas = []
    saldo = tabla_original.iloc[0]["Saldo"] + tabla_original.iloc[0]["Abono_Capital"]
    cuota_actual = tabla_original.iloc[0]["Cuota"]
    n_periodos_restantes = len(tabla_original)
    
    for idx, row in tabla_original.iterrows():
        periodo = row["Periodo"]
        
        # Calcular interés sobre saldo actual
        interes = saldo * tasa_periodo
        abono_capital = cuota_actual - interes
        abono_extra = abonos_dict.get(periodo, 0.0)
        
        # Actualizar saldo
        saldo = saldo - abono_capital - abono_extra
        
        if saldo < 0:
            saldo = 0
        
        filas.append({
            "Periodo": periodo,
            "Fecha": row["Fecha"],
            "Cuota": redondear_decimal(cuota_actual),
            "Interes": redondear_decimal(interes),
            "Abono_Capital": redondear_decimal(abono_capital),
            "Abono_Extra": redondear_decimal(abono_extra),
            "Saldo": redondear_decimal(max(0, saldo))
        })
        
        # Recalcular cuota si hay abono y se elige reducir cuota
        if abono_extra > 0 and saldo > 0:
            n_periodos_restantes = len(tabla_original) - periodo
            
            if opcion_recalculo == "reducir_cuota" and n_periodos_restantes > 0:
                cuota_actual = calcular_cuota_frances(saldo, tasa_periodo, n_periodos_restantes)
            # Si es reducir_plazo, la cuota se mantiene igual
        
        if saldo <= 0:
            break
    
    return pd.DataFrame(filas)
