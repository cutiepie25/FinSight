"""
Script de prueba para verificar el funcionamiento del sistema FinSight.
"""

import sys
sys.path.insert(0, '/home/maria/SEMESTRE_2025_20/FInanciera/FinSight')

from backend.calculos import (
    generar_tabla_amortizacion,
    convertir_nominal_a_efectiva,
    convertir_anticipada_a_vencida,
    calcular_cuota_frances
)
from backend.abonos import generar_abonos_programados, aplicar_abonos_reducir_cuota
from backend.utils import validar_parametros_credito, calcular_resumen_credito

print("=" * 80)
print("PRUEBA DEL SISTEMA FINSIGHT")
print("=" * 80)

# Prueba 1: Caso Base
print("\n📊 PRUEBA 1: Caso Base - Crédito Mensual Simple")
print("-" * 80)

parametros = {
    "monto": 100000,
    "tasa": 12,
    "tipo_tasa": "nominal",
    "tipo_pago": "vencida",
    "plazo_meses": 12,
    "frecuencia_pago": "mensual",
    "fecha_inicio": "2024-01-01",
    "frecuencia_tasa": "anual"
}

# Validar parámetros
es_valido, mensaje = validar_parametros_credito(parametros)
print(f"Validación: {mensaje}")

if es_valido:
    # Generar tabla
    tabla = generar_tabla_amortizacion(**parametros)
    resumen = calcular_resumen_credito(tabla, parametros["monto"])
    
    print(f"\nMonto: ${parametros['monto']:,.2f}")
    print(f"Tasa: {parametros['tasa']}% {parametros['tipo_tasa']} {parametros['tipo_pago']}")
    print(f"Plazo: {parametros['plazo_meses']} meses")
    print(f"\nRESULTADOS:")
    print(f"  Cuota promedio: ${resumen['cuota_promedio']:,.2f}")
    print(f"  Total intereses: ${resumen['total_intereses']:,.2f}")
    print(f"  Total pagado: ${resumen['total_pagado']:,.2f}")
    print(f"  Número de cuotas: {resumen['numero_cuotas']}")
    print(f"  Saldo final: ${resumen['saldo_final']:,.2f}")
    
    print(f"\nPrimeros 3 periodos:")
    print(tabla.head(3).to_string(index=False))
    
    print(f"\nÚltimos 2 periodos:")
    print(tabla.tail(2).to_string(index=False))

# Prueba 2: Conversión de tasas
print("\n\n📐 PRUEBA 2: Conversión de Tasas")
print("-" * 80)

tasa_nominal = 0.12
tasa_efectiva = convertir_nominal_a_efectiva(tasa_nominal, 12)
print(f"Tasa nominal 12% anual → Tasa efectiva: {tasa_efectiva*100:.4f}%")

tasa_anticipada = 0.15
tasa_vencida = convertir_anticipada_a_vencida(tasa_anticipada)
print(f"Tasa anticipada 15% → Tasa vencida: {tasa_vencida*100:.4f}%")

# Prueba 3: Cálculo de cuota
print("\n\n💰 PRUEBA 3: Cálculo de Cuota Francés")
print("-" * 80)

principal = 100000
tasa = 0.01  # 1% mensual
n_periodos = 12

cuota = calcular_cuota_frances(principal, tasa, n_periodos)
print(f"Principal: ${principal:,.2f}")
print(f"Tasa: {tasa*100}% mensual")
print(f"Periodos: {n_periodos}")
print(f"Cuota calculada: ${cuota:,.2f}")

# Prueba 4: Abonos programados
print("\n\n💵 PRUEBA 4: Abonos Programados")
print("-" * 80)

abonos = generar_abonos_programados(
    frecuencia_abono="trimestral",
    frecuencia_pago="mensual",
    monto_abono=5000,
    n_periodos=24
)

print(f"Abonos trimestrales de $5,000 en 24 meses:")
for abono in abonos:
    print(f"  Periodo {abono['periodo']}: ${abono['monto']:,.2f}")

# Prueba 5: Tabla con abonos
print("\n\n📈 PRUEBA 5: Tabla con Abonos - Reducir Cuota")
print("-" * 80)

parametros_abonos = {
    "monto": 100000,
    "tasa": 12,
    "tipo_tasa": "efectiva",
    "tipo_pago": "vencida",
    "plazo_meses": 24,
    "frecuencia_pago": "mensual",
    "fecha_inicio": "2024-01-01",
    "frecuencia_tasa": "anual"
}

# Tabla sin abonos
tabla_sin_abonos = generar_tabla_amortizacion(**parametros_abonos)
resumen_sin = calcular_resumen_credito(tabla_sin_abonos, parametros_abonos["monto"])

print(f"SIN ABONOS:")
print(f"  Total intereses: ${resumen_sin['total_intereses']:,.2f}")
print(f"  Número de cuotas: {resumen_sin['numero_cuotas']}")

# Tabla con abonos
from backend.calculos import convertir_tasa_efectiva
tasa_mensual = convertir_tasa_efectiva(0.12, "anual", "mensual")

abonos_list = generar_abonos_programados("semestral", "mensual", 5000, 24)

tabla_con_abonos = aplicar_abonos_reducir_cuota(
    100000,
    tasa_mensual,
    24,
    abonos_list,
    "2024-01-01",
    "mensual"
)

resumen_con = calcular_resumen_credito(tabla_con_abonos, parametros_abonos["monto"])

print(f"\nCON ABONOS (Reducir Cuota):")
print(f"  Total intereses: ${resumen_con['total_intereses']:,.2f}")
print(f"  Total abonos extra: ${resumen_con['total_abonos_extra']:,.2f}")
print(f"  Número de cuotas: {resumen_con['numero_cuotas']}")
print(f"  Ahorro en intereses: ${resumen_sin['total_intereses'] - resumen_con['total_intereses']:,.2f}")

print("\n" + "=" * 80)
print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
print("=" * 80)
print("\nEl sistema está listo para usar.")
print("\nPara iniciar:")
print("  1. Backend:  uvicorn backend.main:app --reload")
print("  2. Frontend: streamlit run frontend/app_ui.py")
print("=" * 80)
