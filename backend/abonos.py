"""
Módulo para manejo de abonos extraordinarios (programados y ad-hoc).
Incluye lógica de recálculo con opciones de reducir cuota o reducir plazo.
"""

from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from backend.calculos import calcular_cuota_frances, redondear_decimal, FRECUENCIAS


def validar_abonos(abonos: List[Dict], n_periodos: int) -> bool:
    """
    Valida que los abonos sean correctos.
    
    Args:
        abonos: Lista de abonos con {"periodo": int, "monto": float}
        n_periodos: Número total de periodos
    
    Returns:
        True si son válidos, False en caso contrario
    """
    for abono in abonos:
        if abono["periodo"] < 1 or abono["periodo"] > n_periodos:
            return False
        if abono["monto"] <= 0:
            return False
    return True


def generar_abonos_programados(
    frecuencia_abono: str,
    frecuencia_pago: str,
    monto_abono: float,
    n_periodos: int
) -> List[Dict]:
    """
    Genera una lista de abonos programados según la frecuencia especificada.
    
    Args:
        frecuencia_abono: Frecuencia del abono (ej: "trimestral")
        frecuencia_pago: Frecuencia de pago del crédito
        monto_abono: Monto del abono extraordinario
        n_periodos: Número total de periodos
    
    Returns:
        Lista de abonos programados
    """
    meses_abono = FRECUENCIAS[frecuencia_abono]
    meses_pago = FRECUENCIAS[frecuencia_pago]
    
    # Calcular cada cuántos periodos hay un abono
    periodos_entre_abonos = int(meses_abono / meses_pago)
    
    abonos = []
    periodo = periodos_entre_abonos
    
    while periodo <= n_periodos:
        abonos.append({
            "periodo": periodo,
            "monto": monto_abono,
            "tipo": "programado"
        })
        periodo += periodos_entre_abonos
    
    return abonos


def aplicar_abonos_reducir_cuota(
    saldo_inicial: float,
    tasa_periodo: float,
    n_periodos_inicial: int,
    abonos: List[Dict],
    fecha_inicio: str,
    frecuencia_pago: str
) -> pd.DataFrame:
    """
    Genera tabla de amortización con abonos que reducen la cuota.
    
    Args:
        saldo_inicial: Saldo inicial del préstamo
        tasa_periodo: Tasa de interés por periodo (decimal)
        n_periodos_inicial: Número de periodos inicial
        abonos: Lista de abonos ordenados por periodo
        fecha_inicio: Fecha de inicio
        frecuencia_pago: Frecuencia de pago
    
    Returns:
        DataFrame con tabla de amortización
    """
    from datetime import datetime, timedelta
    
    # Ordenar abonos por periodo
    abonos_dict = {a["periodo"]: a["monto"] for a in abonos}
    
    saldo = saldo_inicial
    cuota = calcular_cuota_frances(saldo, tasa_periodo, n_periodos_inicial)
    fecha_actual = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    meses_por_periodo = FRECUENCIAS[frecuencia_pago]
    
    filas = []
    periodo = 1
    
    while saldo > 0.01 and periodo <= n_periodos_inicial * 2:  # Límite de seguridad
        # Calcular interés
        interes = saldo * tasa_periodo
        
        # Calcular abono a capital
        abono_capital = cuota - interes
        
        # Verificar si hay abono extraordinario en este periodo
        abono_extra = abonos_dict.get(periodo, 0.0)
        
        # Actualizar saldo
        saldo = saldo - abono_capital - abono_extra
        
        if saldo < 0:
            # Ajustar última cuota
            abono_capital += saldo
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
            "Abono_Extra": redondear_decimal(abono_extra),
            "Saldo": redondear_decimal(max(0, saldo))
        })
        
        # Si hubo abono extra, recalcular cuota para periodos restantes
        if abono_extra > 0 and saldo > 0.01:
            periodos_restantes = n_periodos_inicial - periodo
            if periodos_restantes > 0:
                cuota = calcular_cuota_frances(saldo, tasa_periodo, periodos_restantes)
        
        fecha_actual = fecha_pago
        periodo += 1
        
        if saldo <= 0.01:
            break
    
    return pd.DataFrame(filas)


def aplicar_abonos_reducir_plazo(
    saldo_inicial: float,
    tasa_periodo: float,
    n_periodos_inicial: int,
    abonos: List[Dict],
    fecha_inicio: str,
    frecuencia_pago: str
) -> pd.DataFrame:
    """
    Genera tabla de amortización con abonos que reducen el plazo (cuota constante).
    
    Args:
        saldo_inicial: Saldo inicial del préstamo
        tasa_periodo: Tasa de interés por periodo (decimal)
        n_periodos_inicial: Número de periodos inicial
        abonos: Lista de abonos ordenados por periodo
        fecha_inicio: Fecha de inicio
        frecuencia_pago: Frecuencia de pago
    
    Returns:
        DataFrame con tabla de amortización
    """
    from datetime import datetime, timedelta
    
    # Ordenar abonos por periodo
    abonos_dict = {a["periodo"]: a["monto"] for a in abonos}
    
    saldo = saldo_inicial
    cuota = calcular_cuota_frances(saldo, tasa_periodo, n_periodos_inicial)
    fecha_actual = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    meses_por_periodo = FRECUENCIAS[frecuencia_pago]
    
    filas = []
    periodo = 1
    
    while saldo > 0.01 and periodo <= n_periodos_inicial * 2:  # Límite de seguridad
        # Calcular interés
        interes = saldo * tasa_periodo
        
        # Calcular abono a capital
        abono_capital = cuota - interes
        
        # Verificar si hay abono extraordinario en este periodo
        abono_extra = abonos_dict.get(periodo, 0.0)
        
        # Actualizar saldo
        saldo = saldo - abono_capital - abono_extra
        
        if saldo < 0:
            # Ajustar última cuota
            abono_capital += saldo
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
            "Abono_Extra": redondear_decimal(abono_extra),
            "Saldo": redondear_decimal(max(0, saldo))
        })
        
        # En modo reducir plazo, la cuota NO cambia, solo se reduce el número de periodos
        
        fecha_actual = fecha_pago
        periodo += 1
        
        if saldo <= 0.01:
            break
    
    return pd.DataFrame(filas)


def agregar_abono_adhoc(
    tabla_actual: pd.DataFrame,
    periodo_abono: int,
    monto_abono: float,
    tasa_periodo: float,
    opcion_recalculo: str,
    fecha_inicio: str,
    frecuencia_pago: str
) -> pd.DataFrame:
    """
    Agrega un abono ad-hoc a la tabla existente y recalcula.
    
    Args:
        tabla_actual: DataFrame con tabla actual
        periodo_abono: Periodo en el que se hace el abono
        monto_abono: Monto del abono
        tasa_periodo: Tasa de interés por periodo
        opcion_recalculo: "reducir_cuota" o "reducir_plazo"
        fecha_inicio: Fecha de inicio del crédito
        frecuencia_pago: Frecuencia de pago
    
    Returns:
        DataFrame con tabla recalculada
    """
    # Obtener saldo inicial (reconstruir desde la tabla)
    if len(tabla_actual) == 0:
        return tabla_actual
    
    # Reconstruir saldo inicial
    primera_fila = tabla_actual.iloc[0]
    saldo_inicial = primera_fila["Saldo"] + primera_fila["Abono_Capital"] + primera_fila["Abono_Extra"]
    
    # Recopilar abonos existentes
    abonos = []
    for _, row in tabla_actual.iterrows():
        if row["Abono_Extra"] > 0:
            abonos.append({
                "periodo": row["Periodo"],
                "monto": row["Abono_Extra"]
            })
    
    # Agregar nuevo abono
    abonos.append({
        "periodo": periodo_abono,
        "monto": monto_abono
    })
    
    # Ordenar abonos por periodo
    abonos = sorted(abonos, key=lambda x: x["periodo"])
    
    # Recalcular tabla completa
    n_periodos_inicial = len(tabla_actual)
    
    if opcion_recalculo == "reducir_cuota":
        return aplicar_abonos_reducir_cuota(
            saldo_inicial, tasa_periodo, n_periodos_inicial,
            abonos, fecha_inicio, frecuencia_pago
        )
    else:
        return aplicar_abonos_reducir_plazo(
            saldo_inicial, tasa_periodo, n_periodos_inicial,
            abonos, fecha_inicio, frecuencia_pago
        )


def calcular_ahorro_por_abonos(tabla_sin_abonos: pd.DataFrame, tabla_con_abonos: pd.DataFrame) -> Dict:
    """
    Calcula el ahorro generado por los abonos extraordinarios.
    
    Args:
        tabla_sin_abonos: Tabla sin abonos
        tabla_con_abonos: Tabla con abonos
    
    Returns:
        Diccionario con métricas de ahorro
    """
    # Calcular totales
    total_pagado_sin_abonos = tabla_sin_abonos["Cuota"].sum()
    total_intereses_sin_abonos = tabla_sin_abonos["Interes"].sum()
    
    total_pagado_con_abonos = tabla_con_abonos["Cuota"].sum() + tabla_con_abonos["Abono_Extra"].sum()
    total_intereses_con_abonos = tabla_con_abonos["Interes"].sum()
    
    ahorro_intereses = total_intereses_sin_abonos - total_intereses_con_abonos
    reduccion_plazo = len(tabla_sin_abonos) - len(tabla_con_abonos)
    
    return {
        "ahorro_intereses": redondear_decimal(ahorro_intereses),
        "reduccion_plazo_periodos": reduccion_plazo,
        "total_intereses_sin_abonos": redondear_decimal(total_intereses_sin_abonos),
        "total_intereses_con_abonos": redondear_decimal(total_intereses_con_abonos),
        "total_pagado_sin_abonos": redondear_decimal(total_pagado_sin_abonos),
        "total_pagado_con_abonos": redondear_decimal(total_pagado_con_abonos)
    }
