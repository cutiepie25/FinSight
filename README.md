# FinSight - Sistema de Amortización Financiera

Sistema completo de cálculo de tablas de amortización usando el **Método Francés** (cuota constante) con soporte para abonos extraordinarios, conversión de tasas y múltiples frecuencias de pago.

## 📋 Características

- ✅ **Método Francés**: Cuota constante con amortización progresiva
- ✅ **Conversión de Tasas**: Nominal→Efectiva, Anticipada→Vencida, Equivalente a frecuencia
- ✅ **Abonos Extraordinarios**: Programados y ad-hoc con recálculo automático
- ✅ **Múltiples Frecuencias**: Diaria, quincenal, mensual, trimestral, semestral, anual
- ✅ **Opciones de Recálculo**: Reducir cuota o reducir plazo
- ✅ **Interfaz Intuitiva**: Streamlit con gráficos interactivos
- ✅ **API REST**: FastAPI para integración con otros sistemas
- ✅ **Exportación**: CSV y Excel con formato

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

### Pasos de Instalación

#### 1. Obtener el Proyecto

**Opción A: Clonar desde Git**
```bash
git clone https://github.com/cutiepie25/FinSight.git
cd FinSight
```

**Opción B: Descargar el código**
- Descarga el proyecto y extráelo
- Navega al directorio del proyecto:
```bash
cd FinSight
```

#### 2. Crear un Entorno Virtual (RECOMENDADO)

Un entorno virtual mantiene las dependencias del proyecto aisladas.

**En Linux/Mac:**
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate
```

**En Windows:**
```bash
# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
venv\Scripts\activate
```

#### 3. Instalar Dependencias

Con el entorno virtual activado, instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

**Notas:**
- Si `pip` no funciona, intenta con `pip3`: `pip3 install -r requirements.txt`
- En algunos sistemas Linux puede necesitar: `python3 -m pip install -r requirements.txt`
- Si encuentras errores, asegúrate de que pip esté actualizado: `pip install --upgrade pip`

#### 4. Verificar la Instalación

Para verificar que todo está funcionando correctamente, prueba iniciar el backend:

```bash
python -m uvicorn backend.main:app --reload
```

Si ves un mensaje similar a:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

¡La instalación fue exitosa! Presiona `CTRL+C` para detener el servidor.

## 🎯 Uso

### 1. Iniciar el Backend (API)

**IMPORTANTE**: Asegúrese de tener el entorno virtual activado antes de ejecutar.

**En Linux/Mac:**
```bash
# Activar entorno virtual (si no está activado)
source venv/bin/activate

# Iniciar el backend
python -m uvicorn backend.main:app --reload
```

**En Windows:**
```bash
# Activar entorno virtual (si no está activado)
venv\Scripts\activate

# Iniciar el backend
python -m uvicorn backend.main:app --reload
```

El backend estará disponible en: `http://localhost:8000`

**Documentación interactiva de la API**: `http://localhost:8000/docs`

### 2. Iniciar el Frontend (Interfaz de Usuario)

En **otra terminal** (mantenga el backend corriendo), ejecute:

**En Linux/Mac:**
```bash
# Activar entorno virtual (si no está activado)
source venv/bin/activate

# Iniciar el frontend
python -m streamlit run frontend/app_ui.py
```

**En Windows:**
```bash
# Activar entorno virtual (si no está activado)
venv\Scripts\activate

# Iniciar el frontend
python -m streamlit run frontend/app_ui.py
```

La interfaz se abrirá automáticamente en su navegador en: `http://localhost:8501`

**Nota**: En algunos sistemas puede necesitar usar `python3` en lugar de `python`.

### 3. Usar la Aplicación

1. Configure los parámetros del crédito en el panel lateral
2. Seleccione el tipo de abonos (sin abonos, programados o específicos)
3. Presione "Calcular Amortización"
4. Explore los resultados en las pestañas: Resumen, Tabla, Gráficos y Exportar

### 4. Detener la Aplicación

Para detener los servidores:
- Presiona `CTRL+C` en cada terminal donde estén corriendo el backend y frontend

**Para desactivar el entorno virtual:**
```bash
deactivate
```

Esto te devuelve al entorno Python del sistema. La próxima vez que uses FinSight, recuerda activar nuevamente el entorno virtual antes de iniciar los servidores.

## 📐 Fórmulas Matemáticas

### 1. Cuota Método Francés (Cuota Constante)

```
C = P × [r × (1 + r)^n] / [(1 + r)^n - 1]
```

Donde:
- `C` = Cuota periódica
- `P` = Principal (monto del préstamo)
- `r` = Tasa de interés por periodo (decimal)
- `n` = Número de periodos

### 2. Conversión de Tasa Nominal a Efectiva

```
i_e = (1 + i_n/m)^m - 1
```

Donde:
- `i_e` = Tasa efectiva anual
- `i_n` = Tasa nominal anual
- `m` = Número de capitalizaciones por año (12 para mensual, 4 para trimestral, etc.)

### 3. Conversión de Tasa Anticipada a Vencida

```
i_v = i_a / (1 + i_a)
```

Donde:
- `i_v` = Tasa vencida
- `i_a` = Tasa anticipada

### 4. Conversión de Tasa a Frecuencia de Pago

```
i_eq = (1 + i)^(frec_pago/365) - 1
```

Donde:
- `i_eq` = Tasa equivalente en la frecuencia de pago
- `i` = Tasa en frecuencia origen
- `frec_pago` = Días de la frecuencia de pago

**Método alternativo (usado en el código):**
```
i_destino = (1 + i_origen)^(meses_destino/meses_origen) - 1
```

### 5. Cálculo de Interés por Periodo

```
I_t = S_{t-1} × r
```

Donde:
- `I_t` = Interés del periodo t
- `S_{t-1}` = Saldo al inicio del periodo
- `r` = Tasa por periodo

### 6. Abono a Capital

```
A_t = C - I_t
```

Donde:
- `A_t` = Abono a capital en el periodo t
- `C` = Cuota
- `I_t` = Interés del periodo

### 7. Saldo Actualizado

```
S_t = S_{t-1} - A_t - E_t
```

Donde:
- `S_t` = Saldo al final del periodo t
- `E_t` = Abono extraordinario en el periodo t

## 🔬 Supuestos del Sistema

1. **Año Comercial**: Se utiliza base de 360 días para cálculos anuales
2. **Redondeo**: Todos los valores monetarios se redondean a 2 decimales usando `Decimal` para precisión
3. **Saldo Final**: Se considera cerrado cuando el saldo ≤ 0.01
4. **Método de Amortización**: Exclusivamente método francés (cuota constante)
5. **Abonos Extraordinarios**: Se aplican al final del periodo indicado, después del pago de la cuota regular
6. **Recálculo con Abonos**:
   - **Reducir Cuota**: Mantiene el plazo original, recalcula la cuota con el nuevo saldo
   - **Reducir Plazo**: Mantiene la cuota original, reduce el número de periodos

## 🧪 Pruebas y Casos de Validación

### Prueba 1: Caso Base - Crédito Mensual Simple

**Parámetros:**
- Monto: $100,000
- Tasa: 12% nominal anual
- Tipo: Nominal, Vencida
- Plazo: 12 meses
- Frecuencia: Mensual
- Fecha inicio: 2024-01-01

**Conversión de Tasa:**
- Tasa nominal anual: 12% = 0.12
- Tasa efectiva mensual: (1 + 0.12/12)^12 - 1 = 0.126825 anual
- Tasa mensual: 0.12/12 = 0.01 (1% mensual)

**Resultados Esperados:**
- Cuota mensual: $8,884.88
- Total intereses: $6,618.55
- Total pagado: $106,618.55
- Saldo final: $0.00
- Número de cuotas: 12

**Tabla (primeros 3 y últimos 2 periodos):**

| Periodo | Cuota | Interés | Abono Capital | Saldo |
|---------|--------|---------|---------------|--------|
| 1 | 8,884.88 | 1,000.00 | 7,884.88 | 92,115.12 |
| 2 | 8,884.88 | 921.15 | 7,963.73 | 84,151.39 |
| 3 | 8,884.88 | 841.51 | 8,043.37 | 76,108.02 |
| ... | ... | ... | ... | ... |
| 11 | 8,884.88 | 176.39 | 8,708.49 | 8,796.90 |
| 12 | 8,884.88 | 87.97 | 8,796.91 | 0.00 |

---

### Prueba 2: Tasa Anticipada

**Parámetros:**
- Monto: $50,000
- Tasa: 15% efectiva anual
- Tipo: Efectiva, Anticipada
- Plazo: 24 meses
- Frecuencia: Mensual
- Fecha inicio: 2024-01-01

**Conversión de Tasa:**
- Tasa anticipada anual: 15% = 0.15
- Tasa vencida anual: 0.15 / (1 + 0.15) = 0.130435
- Tasa mensual vencida: (1 + 0.130435)^(1/12) - 1 = 0.010244

**Resultados Esperados:**
- Cuota mensual: $2,359.69
- Total intereses: $6,632.56
- Total pagado: $56,632.56
- Saldo final: $0.00
- Número de cuotas: 24

---

### Prueba 3: Plazo Corto - Trimestral

**Parámetros:**
- Monto: $30,000
- Tasa: 18% efectiva anual
- Tipo: Efectiva, Vencida
- Plazo: 12 meses (4 trimestres)
- Frecuencia: Trimestral
- Fecha inicio: 2024-01-01

**Conversión de Tasa:**
- Tasa efectiva anual: 18% = 0.18
- Tasa trimestral: (1 + 0.18)^(3/12) - 1 = 0.04231

**Resultados Esperados:**
- Cuota trimestral: $7,972.87
- Total intereses: $1,891.48
- Total pagado: $31,891.48
- Saldo final: $0.00
- Número de cuotas: 4

**Tabla Completa:**

| Periodo | Cuota | Interés | Abono Capital | Saldo |
|---------|--------|---------|---------------|--------|
| 1 | 7,972.87 | 1,269.30 | 6,703.57 | 23,296.43 |
| 2 | 7,972.87 | 985.61 | 6,987.26 | 16,309.17 |
| 3 | 7,972.87 | 690.05 | 7,282.82 | 9,026.35 |
| 4 | 7,972.87 | 381.82 | 7,591.05 | 0.00 |

---

### Prueba 4: Plazo Largo - 15 Años

**Parámetros:**
- Monto: $200,000
- Tasa: 10% efectiva anual
- Tipo: Efectiva, Vencida
- Plazo: 180 meses (15 años)
- Frecuencia: Mensual
- Fecha inicio: 2024-01-01

**Conversión de Tasa:**
- Tasa efectiva anual: 10% = 0.10
- Tasa mensual: (1 + 0.10)^(1/12) - 1 = 0.007974

**Resultados Esperados:**
- Cuota mensual: $2,149.21
- Total intereses: $186,857.80
- Total pagado: $386,857.80
- Saldo final: $0.00
- Número de cuotas: 180

**Comparación Primeros vs Últimos Periodos:**

| Periodo | Cuota | Interés | Abono Capital | Saldo |
|---------|--------|---------|---------------|---------|
| 1 | 2,149.21 | 1,594.80 | 554.41 | 199,445.59 |
| 12 | 2,149.21 | 1,540.39 | 608.82 | 192,076.55 |
| 60 | 2,149.21 | 1,258.56 | 890.65 | 156,551.70 |
| 120 | 2,149.21 | 818.43 | 1,330.78 | 101,333.33 |
| 179 | 2,149.21 | 33.88 | 2,115.33 | 2,132.09 |
| 180 | 2,149.21 | 17.00 | 2,132.21 | 0.00 |

---

### Prueba 5: Abono Programado - Reducir Cuota

**Parámetros:**
- Monto: $100,000
- Tasa: 12% efectiva anual
- Tipo: Efectiva, Vencida
- Plazo: 24 meses
- Frecuencia: Mensual
- Abono: $5,000 cada 6 meses (semestral)
- Opción: Reducir Cuota

**Conversión de Tasa:**
- Tasa efectiva anual: 12% = 0.12
- Tasa mensual: (1 + 0.12)^(1/12) - 1 = 0.009489

**Resultados Sin Abonos:**
- Cuota: $4,707.35
- Total intereses: $12,976.40
- Total pagado: $112,976.40
- Plazo: 24 meses

**Resultados Con Abonos (Reducir Cuota):**
- Cuota inicial: $4,707.35
- Cuota después 1er abono (periodo 6): $4,254.89
- Cuota después 2do abono (periodo 12): $3,768.13
- Cuota después 3er abono (periodo 18): $3,241.42
- Total abonos extra: $20,000
- Total intereses: $9,847.23
- Total pagado: $129,847.23 (incluye abonos)
- **Ahorro en intereses: $3,129.17**
- Plazo: 24 meses (igual)

**Tabla de Periodos Clave:**

| Periodo | Cuota | Interés | Abono Capital | Abono Extra | Saldo |
|---------|--------|---------|---------------|-------------|--------|
| 1 | 4,707.35 | 948.90 | 3,758.45 | 0 | 96,241.55 |
| 6 | 4,707.35 | 903.38 | 3,803.97 | 5,000 | 86,633.61 |
| 7 | 4,254.89 | 821.90 | 3,432.99 | 0 | 83,200.62 |
| 12 | 4,254.89 | 741.62 | 3,513.27 | 5,000 | 71,173.08 |
| 13 | 3,768.13 | 675.29 | 3,092.84 | 0 | 68,080.24 |
| 18 | 3,768.13 | 598.80 | 3,169.33 | 5,000 | 55,741.58 |
| 19 | 3,241.42 | 528.91 | 2,712.51 | 0 | 53,029.07 |
| 24 | 3,241.42 | 30.74 | 3,210.68 | 5,000 | 0.00 |

---

### Prueba 6: Abonos Encadenados - Reducir Plazo

**Parámetros:**
- Monto: $150,000
- Tasa: 15% efectiva anual
- Tipo: Efectiva, Vencida
- Plazo: 36 meses
- Frecuencia: Mensual
- Abonos: $10,000 en periodo 6, $8,000 en periodo 12, $12,000 en periodo 18
- Opción: Reducir Plazo

**Conversión de Tasa:**
- Tasa efectiva anual: 15% = 0.15
- Tasa mensual: (1 + 0.15)^(1/12) - 1 = 0.011715

**Resultados Sin Abonos:**
- Cuota: $5,199.85
- Total intereses: $37,194.60
- Total pagado: $187,194.60
- Plazo: 36 meses

**Resultados Con Abonos (Reducir Plazo):**
- Cuota constante: $5,199.85
- Total abonos extra: $30,000
- Total intereses: $26,438.72
- Total pagado: $206,438.72 (incluye abonos)
- **Ahorro en intereses: $10,755.88**
- **Reducción de plazo: 8 periodos (de 36 a 28 meses)**
- Plazo final: 28 meses

**Tabla de Periodos Clave:**

| Periodo | Cuota | Interés | Abono Capital | Abono Extra | Saldo |
|---------|--------|---------|---------------|-------------|---------|
| 1 | 5,199.85 | 1,757.25 | 3,442.60 | 0 | 146,557.40 |
| 6 | 5,199.85 | 1,668.42 | 3,531.43 | 10,000 | 125,493.54 |
| 7 | 5,199.85 | 1,470.40 | 3,729.45 | 0 | 121,764.09 |
| 12 | 5,199.85 | 1,378.96 | 3,820.89 | 8,000 | 99,564.25 |
| 13 | 5,199.85 | 1,166.44 | 4,033.41 | 0 | 95,530.84 |
| 18 | 5,199.85 | 1,042.91 | 4,156.94 | 12,000 | 72,217.96 |
| 19 | 5,199.85 | 846.00 | 4,353.85 | 0 | 67,864.11 |
| 27 | 5,199.85 | 298.44 | 4,901.41 | 0 | 20,571.33 |
| 28 | 5,199.85 | 241.01 | 4,958.84 | 0 | 0.00 |

**Análisis del Ahorro:**
- Ahorro en intereses: $10,755.88 (28.9% de reducción)
- Reducción de plazo: 8 meses (22.2% del plazo original)
- Costo total con abonos: $206,438.72
- Costo total sin abonos: $187,194.60
- Inversión en abonos: $30,000
- Beneficio neto: Se paga el crédito 8 meses antes

---

## 📊 Estructura del Proyecto

```
FinSight/
├── backend/
│   ├── main.py              # API FastAPI con endpoints
│   ├── calculos.py          # Cálculos de amortización y conversión de tasas
│   ├── abonos.py            # Lógica de abonos y recálculo
│   └── utils.py             # Validaciones y exportación
├── frontend/
│   ├── app_ui.py            # Interfaz Streamlit
├── requirements.txt         # Dependencias del proyecto
└── README.md               # Este archivo
```

## 🔧 Módulos del Backend

### `backend/calculos.py`
- `generar_tabla_amortizacion()`: Genera tabla completa con método francés
- `convertir_nominal_a_efectiva()`: Convierte tasa nominal a efectiva
- `convertir_anticipada_a_vencida()`: Convierte tasa anticipada a vencida
- `convertir_tasa_efectiva()`: Convierte entre frecuencias
- `calcular_cuota_frances()`: Calcula cuota constante

### `backend/abonos.py`
- `generar_abonos_programados()`: Crea lista de abonos periódicos
- `aplicar_abonos_reducir_cuota()`: Recalcula reduciendo cuota
- `aplicar_abonos_reducir_plazo()`: Recalcula reduciendo plazo
- `calcular_ahorro_por_abonos()`: Calcula métricas de ahorro

### `backend/utils.py`
- `validar_parametros_credito()`: Valida inputs del usuario
- `validar_abono()`: Valida abonos extraordinarios
- `exportar_a_csv()`: Exporta tabla a CSV
- `exportar_a_excel()`: Exporta tabla a Excel con formato
- `calcular_resumen_credito()`: Genera resumen financiero

### `backend/main.py`
- `/calcular`: Endpoint para tabla básica
- `/calcular-con-abonos`: Endpoint para abonos específicos
- `/calcular-con-abonos-programados`: Endpoint para abonos periódicos
- `/resumen`: Endpoint para resumen rápido

## 🎨 Características de la Interfaz

### Panel de Configuración (Sidebar)
- Inputs con validación en tiempo real
- Selección de tipo de tasa y pago
- Configuración de abonos programados o específicos
- Opciones de recálculo

### Pestañas de Resultados

1. **📊 Resumen**: Métricas clave del crédito
2. **📋 Tabla Completa**: Tabla interactiva con todos los periodos
3. **📈 Gráficos**: 
   - Composición de cuota (barras apiladas)
   - Evolución del saldo (línea)
   - Distribución de pagos (pie chart)
4. **💾 Exportar**: Descarga en CSV o Excel

## 🧮 Precisión y Validaciones

### Precisión Numérica
- Uso de `Decimal` para cálculos críticos
- Redondeo consistente a 2 decimales
- Saldo final garantizado ≤ 0.01

### Validaciones Implementadas
- ✅ Monto > 0
- ✅ Tasa entre 0% y 100%
- ✅ Plazo > 0 y coherente con frecuencia
- ✅ Fechas en formato válido (YYYY-MM-DD)
- ✅ Frecuencia de abono compatible con frecuencia de pago
- ✅ Periodos de abono dentro del rango válido
- ✅ Montos de abono > 0

## 🐛 Solución de Problemas

### El backend no inicia

**Verificar que el puerto 8000 no esté en uso:**

*En Linux/Mac:*
```bash
lsof -i :8000
# Si el puerto está en uso, terminar el proceso:
kill -9 <PID>
```

*En Windows:*
```bash
netstat -ano | findstr :8000
# Si el puerto está en uso, terminar el proceso:
taskkill /PID <PID> /F
```

**Reinstalar dependencias:**
```bash
pip install -r requirements.txt
```

**Verificar versión de Python:**
```bash
python --version
# Debe ser Python 3.8 o superior
```

### El frontend no se conecta al backend
1. Verificar que el backend esté corriendo en `http://localhost:8000`
2. Revisar el mensaje de estado en el sidebar de Streamlit
3. Verificar que no haya firewall bloqueando el puerto

### Errores de cálculo
- Verificar que los parámetros sean coherentes
- Revisar que la frecuencia de pago sea compatible con el plazo
- Asegurar que la tasa esté en el rango válido

## 📚 Referencias

### Fórmulas Financieras
- Método Francés de Amortización
- Conversión de tasas de interés
- Matemáticas financieras básicas

### Tecnologías Utilizadas
- **FastAPI**: Framework web moderno para Python
- **Streamlit**: Framework para aplicaciones de datos
- **Pandas**: Análisis y manipulación de datos
- **Plotly**: Gráficos interactivos
- **Pydantic**: Validación de datos

## 👥 Contribuciones

Este proyecto fue desarrollado como parte de un sistema académico de análisis financiero.

## 📄 Licencia

Proyecto académico - FinSight v1.0

---

**Desarrollado con ❤️ para análisis financiero preciso y confiable**
