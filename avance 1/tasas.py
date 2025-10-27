"""
Sistema de Amortización de Créditos
Aplicación completa para cálculo y gestión de tablas de amortización
con soporte para diferentes tipos de tasas y abonos extraordinarios.
"""

class TasaInteres:
    """Maneja conversiones entre diferentes tipos de tasas de interés"""
    
    @staticmethod
    def nominal_a_efectiva(tasa_nominal, frecuencia_capitalizacion, periodos_por_año=12):
        """Convierte tasa nominal a efectiva"""
        m = frecuencia_capitalizacion
        return (1 + tasa_nominal / m) ** m - 1
    
    @staticmethod
    def efectiva_a_nominal(tasa_efectiva, frecuencia_capitalizacion, periodos_por_año=12):
        """Convierte tasa efectiva a nominal"""
        m = frecuencia_capitalizacion
        return m * ((1 + tasa_efectiva) ** (1/m) - 1)
    
    @staticmethod
    def anticipada_a_vencida(tasa_anticipada):
        """Convierte tasa anticipada a vencida"""
        return tasa_anticipada / (1 - tasa_anticipada)
    
    @staticmethod
    def vencida_a_anticipada(tasa_vencida):
        """Convierte tasa vencida a anticipada"""
        return tasa_vencida / (1 + tasa_vencida)
    
    @staticmethod
    def calcular_tasa_periodo(tasa_anual, tipo_tasa, modalidad, frecuencia_pago):
        """
        Calcula la tasa equivalente al periodo de pago
        
        Parámetros:
        - tasa_anual: Tasa anual en decimal (ej: 0.12 para 12%)
        - tipo_tasa: 'nominal' o 'efectiva'
        - modalidad: 'vencida' o 'anticipada'
        - frecuencia_pago: número de pagos por año (12=mensual, 4=trimestral, etc)
        """
        # Primero convertimos a tasa efectiva anual vencida
        if tipo_tasa == 'nominal':
            tasa_efectiva_anual = TasaInteres.nominal_a_efectiva(tasa_anual, frecuencia_pago)
        else:
            tasa_efectiva_anual = tasa_anual
        
        if modalidad == 'anticipada':
            tasa_efectiva_anual = TasaInteres.anticipada_a_vencida(tasa_efectiva_anual)
        
        # Calculamos la tasa del periodo
        tasa_periodo = (1 + tasa_efectiva_anual) ** (1/frecuencia_pago) - 1
        
        return tasa_periodo
