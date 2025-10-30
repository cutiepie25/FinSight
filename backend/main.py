"""
API principal con FastAPI para cálculos de amortización.
Endpoints para generar tablas, aplicar abonos y exportar datos.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import pandas as pd

from backend.calculos import (
    generar_tabla_amortizacion,
    convertir_tasa_efectiva,
    FRECUENCIAS
)
from backend.abonos import (
    generar_abonos_programados,
    aplicar_abonos_reducir_cuota,
    aplicar_abonos_reducir_plazo,
    calcular_ahorro_por_abonos
)
from backend.utils import (
    validar_parametros_credito,
    validar_abono,
    validar_frecuencia_abono,
    calcular_resumen_credito,
    generar_reporte_comparativo,
    exportar_a_csv,
    exportar_a_excel
)

app = FastAPI(
    title="FinSight API",
    description="API para cálculo de tablas de amortización con método francés",
    version="1.0.0"
)

# Configurar CORS para permitir conexiones desde Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos Pydantic para validación de datos
class ParametrosCredito(BaseModel):
    monto: float = Field(..., gt=0, description="Monto del préstamo")
    tasa: float = Field(..., ge=0, le=100, description="Tasa de interés en porcentaje")
    tipo_tasa: str = Field(..., description="Tipo de tasa: nominal o efectiva")
    tipo_pago: str = Field(..., description="Tipo de pago: anticipada o vencida")
    plazo_meses: int = Field(..., gt=0, description="Plazo en meses")
    frecuencia_pago: str = Field(..., description="Frecuencia de pago")
    fecha_inicio: str = Field(..., description="Fecha de inicio (YYYY-MM-DD)")
    frecuencia_tasa: str = Field(default="anual", description="Frecuencia de la tasa")


class Abono(BaseModel):
    periodo: int = Field(..., gt=0, description="Periodo del abono")
    monto: float = Field(..., gt=0, description="Monto del abono")


class ParametrosConAbonos(BaseModel):
    parametros_credito: ParametrosCredito
    abonos: List[Abono] = Field(default=[], description="Lista de abonos extraordinarios")
    opcion_recalculo: str = Field(default="reducir_cuota", description="reducir_cuota o reducir_plazo")


class AbonosProgramados(BaseModel):
    parametros_credito: ParametrosCredito
    frecuencia_abono: str = Field(..., description="Frecuencia del abono programado")
    monto_abono: float = Field(..., gt=0, description="Monto del abono")
    opcion_recalculo: str = Field(default="reducir_cuota", description="reducir_cuota o reducir_plazo")


@app.get("/")
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "mensaje": "FinSight API - Sistema de Amortización",
        "version": "1.0.0",
        "endpoints": [
            "/calcular",
            "/calcular-con-abonos",
            "/calcular-con-abonos-programados",
            "/resumen",
            "/comparar"
        ]
    }


@app.post("/calcular")
async def calcular_amortizacion(params: ParametrosCredito):
    """
    Calcula la tabla de amortización básica sin abonos extraordinarios.
    """
    try:
        # Validar parámetros
        params_dict = params.dict()
        es_valido, mensaje = validar_parametros_credito(params_dict)
        
        if not es_valido:
            raise HTTPException(status_code=400, detail=mensaje)
        
        # Generar tabla
        tabla = generar_tabla_amortizacion(
            monto=params.monto,
            tasa=params.tasa,
            tipo_tasa=params.tipo_tasa,
            tipo_pago=params.tipo_pago,
            plazo_meses=params.plazo_meses,
            frecuencia_pago=params.frecuencia_pago,
            fecha_inicio=params.fecha_inicio,
            frecuencia_tasa=params.frecuencia_tasa
        )
        
        # Calcular resumen
        resumen = calcular_resumen_credito(tabla, params.monto)
        
        return {
            "tabla": tabla.to_dict(orient="records"),
            "resumen": resumen,
            "mensaje": "Tabla generada exitosamente"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular: {str(e)}")


@app.post("/calcular-con-abonos")
async def calcular_con_abonos(params: ParametrosConAbonos):
    """
    Calcula la tabla de amortización con abonos extraordinarios específicos.
    """
    try:
        # Validar parámetros del crédito
        params_dict = params.parametros_credito.dict()
        es_valido, mensaje = validar_parametros_credito(params_dict)
        
        if not es_valido:
            raise HTTPException(status_code=400, detail=mensaje)
        
        # Generar tabla sin abonos primero
        tabla_sin_abonos = generar_tabla_amortizacion(
            monto=params.parametros_credito.monto,
            tasa=params.parametros_credito.tasa,
            tipo_tasa=params.parametros_credito.tipo_tasa,
            tipo_pago=params.parametros_credito.tipo_pago,
            plazo_meses=params.parametros_credito.plazo_meses,
            frecuencia_pago=params.parametros_credito.frecuencia_pago,
            fecha_inicio=params.parametros_credito.fecha_inicio,
            frecuencia_tasa=params.parametros_credito.frecuencia_tasa
        )
        
        # Si no hay abonos, retornar tabla sin abonos
        if not params.abonos:
            resumen = calcular_resumen_credito(tabla_sin_abonos, params.parametros_credito.monto)
            return {
                "tabla": tabla_sin_abonos.to_dict(orient="records"),
                "resumen": resumen,
                "mensaje": "Tabla sin abonos generada"
            }
        
        # Validar abonos
        n_periodos = len(tabla_sin_abonos)
        for abono in params.abonos:
            es_valido, mensaje = validar_abono(abono.periodo, abono.monto, n_periodos)
            if not es_valido:
                raise HTTPException(status_code=400, detail=mensaje)
        
        # Convertir abonos a lista de diccionarios
        abonos_list = [{"periodo": a.periodo, "monto": a.monto} for a in params.abonos]
        
        # Calcular tasa por periodo
        tasa_decimal = params.parametros_credito.tasa / 100
        
        # Convertir tasa según tipo
        if params.parametros_credito.tipo_tasa == "nominal":
            from backend.calculos import convertir_nominal_a_efectiva
            m_map = {"mensual": 12, "trimestral": 4, "semestral": 2, "anual": 1}
            m = m_map.get(params.parametros_credito.frecuencia_tasa, 12)
            tasa_efectiva = convertir_nominal_a_efectiva(tasa_decimal, m)
        else:
            tasa_efectiva = tasa_decimal
        
        if params.parametros_credito.tipo_pago == "anticipada":
            from backend.calculos import convertir_anticipada_a_vencida
            tasa_efectiva = convertir_anticipada_a_vencida(tasa_efectiva)
        
        tasa_periodo = convertir_tasa_efectiva(
            tasa_efectiva,
            params.parametros_credito.frecuencia_tasa,
            params.parametros_credito.frecuencia_pago
        )
        
        # Aplicar abonos según opción
        if params.opcion_recalculo == "reducir_cuota":
            tabla_con_abonos = aplicar_abonos_reducir_cuota(
                params.parametros_credito.monto,
                tasa_periodo,
                n_periodos,
                abonos_list,
                params.parametros_credito.fecha_inicio,
                params.parametros_credito.frecuencia_pago
            )
        else:
            tabla_con_abonos = aplicar_abonos_reducir_plazo(
                params.parametros_credito.monto,
                tasa_periodo,
                n_periodos,
                abonos_list,
                params.parametros_credito.fecha_inicio,
                params.parametros_credito.frecuencia_pago
            )
        
        # Calcular ahorro
        ahorro = calcular_ahorro_por_abonos(tabla_sin_abonos, tabla_con_abonos)
        resumen = calcular_resumen_credito(tabla_con_abonos, params.parametros_credito.monto)
        
        return {
            "tabla": tabla_con_abonos.to_dict(orient="records"),
            "resumen": resumen,
            "ahorro": ahorro,
            "mensaje": "Tabla con abonos generada exitosamente"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular: {str(e)}")


@app.post("/calcular-con-abonos-programados")
async def calcular_con_abonos_programados(params: AbonosProgramados):
    """
    Calcula la tabla de amortización con abonos programados periódicos.
    """
    try:
        # Validar parámetros del crédito
        params_dict = params.parametros_credito.dict()
        es_valido, mensaje = validar_parametros_credito(params_dict)
        
        if not es_valido:
            raise HTTPException(status_code=400, detail=mensaje)
        
        # Validar frecuencia de abono
        es_valido, mensaje = validar_frecuencia_abono(
            params.frecuencia_abono,
            params.parametros_credito.frecuencia_pago
        )
        
        if not es_valido:
            raise HTTPException(status_code=400, detail=mensaje)
        
        # Generar tabla sin abonos
        tabla_sin_abonos = generar_tabla_amortizacion(
            monto=params.parametros_credito.monto,
            tasa=params.parametros_credito.tasa,
            tipo_tasa=params.parametros_credito.tipo_tasa,
            tipo_pago=params.parametros_credito.tipo_pago,
            plazo_meses=params.parametros_credito.plazo_meses,
            frecuencia_pago=params.parametros_credito.frecuencia_pago,
            fecha_inicio=params.parametros_credito.fecha_inicio,
            frecuencia_tasa=params.parametros_credito.frecuencia_tasa
        )
        
        n_periodos = len(tabla_sin_abonos)
        
        # Generar abonos programados
        abonos_list = generar_abonos_programados(
            params.frecuencia_abono,
            params.parametros_credito.frecuencia_pago,
            params.monto_abono,
            n_periodos
        )
        
        # Calcular tasa por periodo
        tasa_decimal = params.parametros_credito.tasa / 100
        
        if params.parametros_credito.tipo_tasa == "nominal":
            from backend.calculos import convertir_nominal_a_efectiva
            m_map = {"mensual": 12, "trimestral": 4, "semestral": 2, "anual": 1}
            m = m_map.get(params.parametros_credito.frecuencia_tasa, 12)
            tasa_efectiva = convertir_nominal_a_efectiva(tasa_decimal, m)
        else:
            tasa_efectiva = tasa_decimal
        
        if params.parametros_credito.tipo_pago == "anticipada":
            from backend.calculos import convertir_anticipada_a_vencida
            tasa_efectiva = convertir_anticipada_a_vencida(tasa_efectiva)
        
        tasa_periodo = convertir_tasa_efectiva(
            tasa_efectiva,
            params.parametros_credito.frecuencia_tasa,
            params.parametros_credito.frecuencia_pago
        )
        
        # Aplicar abonos
        if params.opcion_recalculo == "reducir_cuota":
            tabla_con_abonos = aplicar_abonos_reducir_cuota(
                params.parametros_credito.monto,
                tasa_periodo,
                n_periodos,
                abonos_list,
                params.parametros_credito.fecha_inicio,
                params.parametros_credito.frecuencia_pago
            )
        else:
            tabla_con_abonos = aplicar_abonos_reducir_plazo(
                params.parametros_credito.monto,
                tasa_periodo,
                n_periodos,
                abonos_list,
                params.parametros_credito.fecha_inicio,
                params.parametros_credito.frecuencia_pago
            )
        
        # Calcular ahorro
        ahorro = calcular_ahorro_por_abonos(tabla_sin_abonos, tabla_con_abonos)
        resumen = calcular_resumen_credito(tabla_con_abonos, params.parametros_credito.monto)
        
        return {
            "tabla": tabla_con_abonos.to_dict(orient="records"),
            "resumen": resumen,
            "ahorro": ahorro,
            "abonos_programados": [{"periodo": a["periodo"], "monto": a["monto"]} for a in abonos_list],
            "mensaje": "Tabla con abonos programados generada exitosamente"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular: {str(e)}")


@app.post("/resumen")
async def obtener_resumen(params: ParametrosCredito):
    """
    Obtiene un resumen del crédito sin generar la tabla completa.
    """
    try:
        # Validar parámetros
        params_dict = params.dict()
        es_valido, mensaje = validar_parametros_credito(params_dict)
        
        if not es_valido:
            raise HTTPException(status_code=400, detail=mensaje)
        
        # Generar tabla
        tabla = generar_tabla_amortizacion(
            monto=params.monto,
            tasa=params.tasa,
            tipo_tasa=params.tipo_tasa,
            tipo_pago=params.tipo_pago,
            plazo_meses=params.plazo_meses,
            frecuencia_pago=params.frecuencia_pago,
            fecha_inicio=params.fecha_inicio,
            frecuencia_tasa=params.frecuencia_tasa
        )
        
        # Calcular resumen
        resumen = calcular_resumen_credito(tabla, params.monto)
        
        return {
            "resumen": resumen,
            "mensaje": "Resumen calculado exitosamente"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular resumen: {str(e)}")


@app.get("/health")
async def health_check():
    """Endpoint de salud para verificar que la API está funcionando."""
    return {"status": "healthy", "service": "FinSight API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
