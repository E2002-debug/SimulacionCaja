"""
═══════════════════════════════════════════════════════════════════════════════
MÓDULO: parametros_colas.py
PROPÓSITO: Definición centralizada de parámetros para simulación M/M/s
FECHA: Noviembre 18, 2025
AUTOR: Sistema de Simulación de Colas
═══════════════════════════════════════════════════════════════════════════════

DESCRIPCIÓN:
Este módulo contiene todos los parámetros necesarios para ejecutar el
simulador de colas tipo M/M/s aplicado al problema de decisión de cajas
en supermercado.

COMPONENTES PRINCIPALES:
1. Parámetros de llegadas (λ) por franja horaria
2. Parámetros de servicio (μ) según tipo de cajero
3. Costos operativos y penalizaciones
4. Objetivos de nivel de servicio (SLA)
5. Configuraciones de experimentación
6. Distribuciones estadísticas

NOTACIÓN:
- λ (lambda): Tasa de llegadas (clientes/hora)
- μ (mu): Tasa de servicio (clientes/hora por caja)
- s: Número de servidores (cajas activas)
- ρ (rho): Utilización del sistema = λ/(s×μ)
- W: Tiempo en sistema (minutos)
- Wq: Tiempo en cola (minutos)
- L: Número de clientes en sistema
- Lq: Número de clientes en cola
═══════════════════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════════════════
# 1. PARÁMETROS DE LLEGADAS (λ) POR FRANJA HORARIA
# ═══════════════════════════════════════════════════════════════════════════

"""
Las tasas de llegada varían según la franja horaria del día.
Estas tasas se obtienen típicamente del análisis histórico de transacciones
del sistema POS o conteo de entradas al establecimiento.

UNIDAD: clientes/hora
DISTRIBUCIÓN: Proceso de Poisson
"""

TASAS_LLEGADA = {
    'matutina': {
        'nombre': 'Matutina (8:00 - 11:00)',
        'lambda': 20,           # Tasa promedio: 20 clientes/hora
        'lambda_min': 15,       # Rango inferior (para análisis de sensibilidad)
        'lambda_max': 25,       # Rango superior
        'desv_std': 4,          # Desviación estándar observada
        'descripcion': 'Período de baja afluencia, compras pequeñas'
    },
    'almuerzo': {
        'nombre': 'Almuerzo (11:00 - 14:00)',
        'lambda': 35,
        'lambda_min': 30,
        'lambda_max': 40,
        'desv_std': 6,
        'descripcion': 'Período de afluencia media-alta, compras rápidas'
    },
    'tarde': {
        'nombre': 'Tarde (14:00 - 18:00)',
        'lambda': 25,
        'lambda_min': 20,
        'lambda_max': 30,
        'desv_std': 5,
        'descripcion': 'Período de afluencia media, compras variadas'
    },
    'vespertina': {
        'nombre': 'Vespertina (18:00 - 21:00)',
        'lambda': 50,
        'lambda_min': 40,
        'lambda_max': 60,
        'desv_std': 10,
        'descripcion': 'Hora pico, compras grandes y familiares'
    }
}

# Tasa de llegada para experimentación por defecto
LAMBDA_DEFAULT = TASAS_LLEGADA['vespertina']['lambda']


# ═══════════════════════════════════════════════════════════════════════════
# 2. PARÁMETROS DE SERVICIO (μ) SEGÚN TIPO DE CAJERO
# ═══════════════════════════════════════════════════════════════════════════

"""
El tiempo de servicio depende de:
1. Habilidad del cajero (Experto vs Principiante)
2. Número de artículos del cliente
3. Método de pago

COMPONENTES DEL SERVICIO:
- T_servicio = T_escaneo + T_cobro
- T_escaneo = n_artículos × tiempo_por_artículo
- T_cobro = tiempo_fijo_de_pago
"""

CAJEROS = {
    'experto': {
        'nombre': 'Cajero Experto',
        'tiempo_escaneo_min': 2.5,      # segundos por artículo
        'tiempo_escaneo_max': 4.0,
        'tiempo_escaneo_promedio': 3.25,
        'distribucion_escaneo': 'uniforme',
        'eficiencia': 1.0,
        'descripcion': 'Cajero con >1 año de experiencia, movimientos eficientes'
    },
    'principiante': {
        'nombre': 'Cajero Principiante',
        'tiempo_escaneo_min': 4.5,
        'tiempo_escaneo_max': 7.0,
        'tiempo_escaneo_promedio': 5.75,
        'distribucion_escaneo': 'uniforme',
        'eficiencia': 0.57,  # ~57% de la velocidad de un experto
        'descripcion': 'Cajero con <6 meses de experiencia, requiere más tiempo'
    }
}

# Tiempo de cobro (independiente del cajero)
TIEMPO_COBRO = {
    'min': 15,          # segundos
    'max': 30,
    'promedio': 22.5,
    'distribucion': 'uniforme',
    'descripcion': 'Tiempo de procesamiento de pago (efectivo, tarjeta, etc.)'
}

# Distribución de artículos según tipo de caja
DISTRIBUCION_ARTICULOS = {
    'normal': {
        'nombre': 'Caja Normal',
        'articulos_min': 1,
        'articulos_max': 50,
        'articulos_promedio': 20,
        'distribucion': [
            {'prob': 0.50, 'rango': (1, 20), 'descripcion': '50% clientes con compras pequeñas'},
            {'prob': 0.30, 'rango': (21, 35), 'descripcion': '30% clientes con compras medianas'},
            {'prob': 0.20, 'rango': (36, 50), 'descripcion': '20% clientes con compras grandes'}
        ],
        'restriccion': 'Máximo 50 artículos'
    },
    'express': {
        'nombre': 'Caja Express',
        'articulos_min': 1,
        'articulos_max': 10,
        'articulos_promedio': 5,
        'distribucion': [
            {'prob': 0.70, 'rango': (1, 5), 'descripcion': '70% clientes con 1-5 artículos'},
            {'prob': 0.30, 'rango': (6, 10), 'descripcion': '30% clientes con 6-10 artículos'}
        ],
        'restriccion': 'Máximo 10 artículos (restricción estricta)'
    }
}

# Cálculo de μ (tasa de servicio en clientes/hora)
def calcular_mu(tipo_cajero='experto', tipo_caja='normal'):
    """
    Calcula la tasa de servicio μ basada en el tipo de cajero y caja.
    
    Parámetros:
    -----------
    tipo_cajero : str
        'experto' o 'principiante'
    tipo_caja : str
        'normal' o 'express'
    
    Retorna:
    --------
    float
        Tasa de servicio en clientes/hora
    
    Fórmula:
    --------
    μ = 1 / E[T_servicio]
    E[T_servicio] = E[n_articulos] × E[t_escaneo] + E[t_cobro]
    
    Ejemplo:
    --------
    >>> calcular_mu('experto', 'express')
    >>> # Cliente promedio: 5 artículos
    >>> # Tiempo escaneo: 3.25 seg/art
    >>> # Tiempo cobro: 22.5 seg
    >>> # T_servicio = 5 × 3.25 + 22.5 = 38.75 seg = 0.646 min
    >>> # μ = 60 / 0.646 = 92.8 clientes/hora
    """
    # Obtener parámetros
    cajero = CAJEROS[tipo_cajero]
    caja = DISTRIBUCION_ARTICULOS[tipo_caja]
    
    # Tiempo promedio de escaneo por artículo (segundos)
    t_escaneo_articulo = cajero['tiempo_escaneo_promedio']
    
    # Número promedio de artículos
    n_articulos_promedio = caja['articulos_promedio']
    
    # Tiempo promedio de cobro (segundos)
    t_cobro = TIEMPO_COBRO['promedio']
    
    # Tiempo total de servicio (segundos)
    t_servicio_seg = n_articulos_promedio * t_escaneo_articulo + t_cobro
    
    # Convertir a minutos
    t_servicio_min = t_servicio_seg / 60.0
    
    # Calcular μ en clientes/hora
    mu = 60.0 / t_servicio_min
    
    return mu

# Tasas de servicio precalculadas para referencia rápida
MU_PRECALCULADO = {
    'experto_normal': calcular_mu('experto', 'normal'),      # ~42 clientes/hora
    'experto_express': calcular_mu('experto', 'express'),    # ~93 clientes/hora
    'principiante_normal': calcular_mu('principiante', 'normal'),  # ~30 clientes/hora
    'principiante_express': calcular_mu('principiante', 'express') # ~66 clientes/hora
}


# ═══════════════════════════════════════════════════════════════════════════
# 3. COSTOS OPERATIVOS Y PENALIZACIONES
# ═══════════════════════════════════════════════════════════════════════════

"""
El modelo de costos integra tres componentes que deben ser minimizados:

1. Costo por caja activa (c_caja):
   - Salarios proporcionales
   - Energía y equipamiento
   - Depreciación

2. Costo por tiempo de espera (c_espera):
   - Insatisfacción del cliente
   - Pérdida de ventas futuras
   - Daño a reputación

3. Penalización por incumplir SLA (c_SLA):
   - Multas o compensaciones
   - Pérdida de contratos
   - Imagen corporativa

UNIDADES: Pesos colombianos (COP)
"""

COSTOS = {
    'caja_activa': {
        'valor': 17500,  # COP/hora por caja
        'componentes': {
            'salario': 12500,       # Salario proporcional del cajero
            'energia': 2000,        # Consumo eléctrico (POS, scanner, iluminación)
            'equipos': 1500,        # Depreciación de equipos
            'espacio': 1500         # Costo de oportunidad del espacio
        },
        'unidad': 'COP/hora',
        'descripcion': 'Costo total de mantener una caja operativa durante 1 hora'
    },
    
    'tiempo_espera': {
        'valor': 500,  # COP/cliente-minuto
        'justificacion': """
            Este valor refleja el costo de oportunidad de que un cliente
            permanezca en el sistema. Se basa en:
            - Tasa de abandono: 5% por cada minuto adicional de espera
            - Valor promedio de compra: $50,000
            - Customer Lifetime Value: ~$2,000,000 (compras repetidas)
            - Pérdida esperada = 0.05 × 0.01 × 2,000,000 = $1,000/minuto
            - Se usa valor conservador de $500/minuto
        """,
        'unidad': 'COP/cliente-minuto',
        'rango_tipico': (200, 1000),
        'descripcion': 'Costo por cada minuto que un cliente permanece en sistema'
    },
    
    'penalizacion_SLA': {
        'valor': 10000,  # COP por violación
        'tipo': 'fijo',  # 'fijo' o 'proporcional'
        'justificacion': """
            Penalización aplicada por cada cliente que excede el SLA objetivo.
            Puede representar:
            - Descuentos o compensaciones al cliente
            - Multas contractuales (retail corporativo)
            - Pérdida estimada de fidelidad
        """,
        'unidad': 'COP/violación',
        'rango_tipico': (5000, 15000),
        'descripcion': 'Penalización por cada cliente que excede tiempo SLA'
    }
}

# Función de costo total
def calcular_costo_total(s, W_promedio, N_clientes, N_violaciones_SLA, T_horas):
    """
    Calcula el costo total de operación para una configuración dada.
    
    Parámetros:
    -----------
    s : int
        Número de cajas activas
    W_promedio : float
        Tiempo promedio en sistema (minutos)
    N_clientes : int
        Número total de clientes atendidos
    N_violaciones_SLA : int
        Número de clientes que excedieron el SLA
    T_horas : float
        Duración de la operación (horas)
    
    Retorna:
    --------
    dict
        Diccionario con costos desglosados y total
    
    Fórmula:
    --------
    Costo_Total = c_caja×s×T + c_espera×Σ(W_i) + c_SLA×N_violaciones
    
    Ejemplo:
    --------
    >>> calcular_costo_total(s=3, W_promedio=3.5, N_clientes=150, 
    ...                      N_violaciones_SLA=10, T_horas=3)
    >>> # Costo_Cajas = 17,500 × 3 × 3 = 157,500
    >>> # Costo_Espera = 500 × (3.5 × 150) = 262,500
    >>> # Costo_SLA = 10,000 × 10 = 100,000
    >>> # Costo_Total = 520,000 COP
    """
    # Costo de cajas activas
    costo_cajas = COSTOS['caja_activa']['valor'] * s * T_horas
    
    # Costo de tiempo de espera (total acumulado)
    tiempo_total_sistema = W_promedio * N_clientes
    costo_espera = COSTOS['tiempo_espera']['valor'] * tiempo_total_sistema
    
    # Costo por violaciones de SLA
    costo_SLA = COSTOS['penalizacion_SLA']['valor'] * N_violaciones_SLA
    
    # Costo total
    costo_total = costo_cajas + costo_espera + costo_SLA
    
    return {
        'costo_cajas': costo_cajas,
        'costo_espera': costo_espera,
        'costo_SLA': costo_SLA,
        'costo_total': costo_total,
        'detalle': {
            's': s,
            'T_horas': T_horas,
            'N_clientes': N_clientes,
            'W_promedio': W_promedio,
            'N_violaciones_SLA': N_violaciones_SLA
        }
    }


# ═══════════════════════════════════════════════════════════════════════════
# 4. OBJETIVOS DE NIVEL DE SERVICIO (SLA)
# ═══════════════════════════════════════════════════════════════════════════

"""
El SLA (Service Level Agreement) define el estándar de calidad de servicio
que el negocio se compromete a cumplir.

TIPOS DE SLA IMPLEMENTADOS:
1. SLA sobre tiempo total en sistema (W)
2. SLA sobre tiempo de espera en cola (Wq)
3. SLA sobre número de personas en cola (Lq)
"""

SLA_CONFIG = {
    'tiempo_sistema': {
        'tipo': 'W',
        'valor_objetivo': 5.0,  # minutos
        'nivel_servicio': 0.90,  # 90% de cumplimiento
        'metrica': 'P(W ≤ 5 min) ≥ 0.90',
        'descripcion': 'El 90% de los clientes debe salir del sistema en ≤5 minutos',
        'activo': True  # Usar este SLA en la simulación
    },
    
    'tiempo_cola': {
        'tipo': 'Wq',
        'valor_objetivo': 3.0,  # minutos
        'nivel_servicio': 0.95,  # 95% de cumplimiento
        'metrica': 'P(Wq ≤ 3 min) ≥ 0.95',
        'descripcion': 'El 95% de los clientes debe esperar ≤3 minutos en fila',
        'activo': False
    },
    
    'clientes_cola': {
        'tipo': 'Lq',
        'valor_objetivo': 5,  # personas
        'nivel_servicio': 0.90,
        'metrica': 'P(Lq ≤ 5 personas) ≥ 0.90',
        'descripcion': 'El 90% del tiempo debe haber ≤5 personas en cola',
        'activo': False
    }
}

# SLA por defecto (el que está activo)
SLA_DEFAULT = next(sla for sla in SLA_CONFIG.values() if sla['activo'])


# ═══════════════════════════════════════════════════════════════════════════
# 5. CONFIGURACIONES DE EXPERIMENTACIÓN
# ═══════════════════════════════════════════════════════════════════════════

"""
Parámetros para diseño de experimentos (DOE - Design of Experiments)
"""

EXPERIMENTOS = {
    'replicas': 30,  # Número de réplicas independientes por configuración
    'seed_base': 42,  # Semilla base para reproducibilidad
    'nivel_confianza': 0.95,  # 95% para intervalos de confianza
    
    'duracion': {
        'T_simulacion': 8 * 60,  # 8 horas = 480 minutos
        'T_warmup': 60,  # 1 hora de calentamiento (descartar)
        'T_recoleccion': 7 * 60,  # 7 horas de recolección de datos
        'unidad': 'minutos'
    },
    
    'factores': {
        'lambda': [20, 30, 40, 50],  # 4 niveles de tasa de llegadas
        's': [2, 3, 4, 5, 6],  # 5 configuraciones de cajas
        'tipo_cajero': ['experto', 'principiante', 'mixto'],  # 3 tipos
        'tipo_caja': ['normal', 'express']  # 2 tipos
    },
    
    'metricas': {
        'principales': ['W', 'Wq', 'L', 'Lq', 'rho', 'P_SLA'],
        'secundarias': ['W_max', 'W_percentil_95', 'N_abandonos'],
        'economicas': ['costo_total', 'costo_cajas', 'costo_espera', 'costo_SLA']
    },
    
    'criterio_suficiencia': {
        'error_relativo_max': 0.05,  # 5% de error relativo en IC
        'metrica': 'W',  # Métrica para evaluar suficiencia
        'descripcion': 'Ancho_IC / W̄ < 0.05'
    }
}

# Número total de corridas experimentales
def calcular_total_corridas():
    """
    Calcula el número total de corridas en el diseño factorial completo.
    
    Total = (niveles de λ) × (niveles de s) × (tipos de cajero) × R
    
    Retorna:
    --------
    int
        Número total de corridas
    """
    factores = EXPERIMENTOS['factores']
    R = EXPERIMENTOS['replicas']
    
    total = (len(factores['lambda']) * 
             len(factores['s']) * 
             len(factores['tipo_cajero']) * 
             R)
    
    return total

# Total de corridas: 4 × 5 × 3 × 30 = 1,800 corridas


# ═══════════════════════════════════════════════════════════════════════════
# 6. RESTRICCIONES Y VALIDACIONES
# ═══════════════════════════════════════════════════════════════════════════

"""
Condiciones que debe cumplir el sistema para garantizar validez.
"""

def validar_estabilidad(lambda_val, mu_val, s):
    """
    Verifica la condición de estabilidad del sistema M/M/s.
    
    Condición: ρ = λ/(s×μ) < 1
    
    Si ρ ≥ 1, la cola crece infinitamente (sistema inestable).
    
    Parámetros:
    -----------
    lambda_val : float
        Tasa de llegadas (clientes/hora)
    mu_val : float
        Tasa de servicio por caja (clientes/hora)
    s : int
        Número de cajas activas
    
    Retorna:
    --------
    dict
        {'estable': bool, 'rho': float, 'mensaje': str}
    
    Ejemplo:
    --------
    >>> validar_estabilidad(lambda_val=50, mu_val=20, s=2)
    >>> {'estable': False, 'rho': 1.25, 'mensaje': '❌ Sistema inestable'}
    >>> 
    >>> validar_estabilidad(lambda_val=50, mu_val=20, s=3)
    >>> {'estable': True, 'rho': 0.833, 'mensaje': '✓ Sistema estable'}
    """
    rho = lambda_val / (s * mu_val)
    
    estable = rho < 1.0
    
    if estable:
        mensaje = f"✓ Sistema estable: ρ = {rho:.3f} < 1"
    else:
        mensaje = f"❌ Sistema inestable: ρ = {rho:.3f} ≥ 1 (cola crece indefinidamente)"
    
    return {
        'estable': estable,
        'rho': rho,
        'mensaje': mensaje,
        'utilizacion_porcentaje': rho * 100
    }

def calcular_s_minimo(lambda_val, mu_val):
    """
    Calcula el número mínimo de servidores para estabilidad.
    
    s_min = ⌈λ/μ⌉
    
    Parámetros:
    -----------
    lambda_val : float
        Tasa de llegadas
    mu_val : float
        Tasa de servicio por caja
    
    Retorna:
    --------
    int
        Número mínimo de cajas necesarias
    """
    import math
    s_min = math.ceil(lambda_val / mu_val)
    return s_min


# ═══════════════════════════════════════════════════════════════════════════
# 7. CONFIGURACIONES PREDEFINIDAS (CASOS DE ESTUDIO)
# ═══════════════════════════════════════════════════════════════════════════

"""
Escenarios predefinidos para análisis rápido.
"""

CASOS_ESTUDIO = {
    'base': {
        'nombre': 'Caso Base',
        'lambda': 30,
        'mu': calcular_mu('experto', 'normal'),
        's_rango': [2, 3, 4, 5],
        'descripcion': 'Escenario típico de tarde con cajeros expertos'
    },
    
    'hora_pico': {
        'nombre': 'Hora Pico',
        'lambda': 50,
        'mu': calcular_mu('experto', 'normal'),
        's_rango': [3, 4, 5, 6],
        'descripcion': 'Vespertino con alta demanda'
    },
    
    'baja_demanda': {
        'nombre': 'Baja Demanda',
        'lambda': 15,
        'mu': calcular_mu('principiante', 'normal'),
        's_rango': [1, 2, 3],
        'descripcion': 'Matutino con cajeros principiantes'
    }
}


# ═══════════════════════════════════════════════════════════════════════════
# 8. UTILIDADES Y FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════

def imprimir_resumen_parametros():
    """
    Imprime un resumen legible de todos los parámetros configurados.
    """
    print("═" * 80)
    print(" " * 20 + "RESUMEN DE PARÁMETROS DEL SISTEMA")
    print("═" * 80)
    
    print("\n1. TASAS DE LLEGADA (λ):")
    for franja, params in TASAS_LLEGADA.items():
        print(f"   {params['nombre']:30s}: λ = {params['lambda']:3d} clientes/hora")
    
    print("\n2. TASAS DE SERVICIO (μ) PRECALCULADAS:")
    for config, mu_val in MU_PRECALCULADO.items():
        print(f"   {config:25s}: μ = {mu_val:5.1f} clientes/hora")
    
    print("\n3. COSTOS:")
    print(f"   Caja activa:      ${COSTOS['caja_activa']['valor']:,} COP/hora")
    print(f"   Tiempo espera:    ${COSTOS['tiempo_espera']['valor']:,} COP/cliente-minuto")
    print(f"   Penalización SLA: ${COSTOS['penalizacion_SLA']['valor']:,} COP/violación")
    
    print("\n4. SLA ACTIVO:")
    print(f"   Tipo: {SLA_DEFAULT['tipo']}")
    print(f"   Objetivo: {SLA_DEFAULT['valor_objetivo']} {SLA_DEFAULT['tipo']}")
    print(f"   Nivel: {SLA_DEFAULT['nivel_servicio']*100:.0f}%")
    print(f"   Métrica: {SLA_DEFAULT['metrica']}")
    
    print("\n5. EXPERIMENTACIÓN:")
    print(f"   Réplicas por configuración: {EXPERIMENTOS['replicas']}")
    print(f"   Duración de simulación: {EXPERIMENTOS['duracion']['T_simulacion']} minutos")
    print(f"   Total de corridas: {calcular_total_corridas():,}")
    
    print("\n" + "═" * 80)


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE DE PRUEBA (ejecutar solo si es módulo principal)
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Mostrar resumen de parámetros
    imprimir_resumen_parametros()
    
    # Ejemplo de validación de estabilidad
    print("\n\nEJEMPLOS DE VALIDACIÓN DE ESTABILIDAD:")
    print("-" * 80)
    
    casos_prueba = [
        {'lambda': 30, 'mu': 15, 's': 2, 'nombre': 'Caso 1: ρ = 1 (límite)'},
        {'lambda': 30, 'mu': 15, 's': 3, 'nombre': 'Caso 2: ρ < 1 (estable)'},
        {'lambda': 50, 'mu': 20, 's': 2, 'nombre': 'Caso 3: ρ > 1 (inestable)'},
    ]
    
    for caso in casos_prueba:
        print(f"\n{caso['nombre']}")
        resultado = validar_estabilidad(caso['lambda'], caso['mu'], caso['s'])
        print(f"  λ={caso['lambda']}, μ={caso['mu']}, s={caso['s']}")
        print(f"  {resultado['mensaje']}")
        print(f"  Utilización: {resultado['utilizacion_porcentaje']:.1f}%")
    
    # Ejemplo de cálculo de costo
    print("\n\nEJEMPLO DE CÁLCULO DE COSTO:")
    print("-" * 80)
    costo = calcular_costo_total(s=3, W_promedio=3.5, N_clientes=150,
                                  N_violaciones_SLA=10, T_horas=3)
    print(f"Configuración: s=3 cajas, 3 horas de operación")
    print(f"  Costo de cajas:  ${costo['costo_cajas']:>10,} COP")
    print(f"  Costo de espera: ${costo['costo_espera']:>10,} COP")
    print(f"  Costo SLA:       ${costo['costo_SLA']:>10,} COP")
    print(f"  {'─' * 40}")
    print(f"  COSTO TOTAL:     ${costo['costo_total']:>10,} COP")
    print("═" * 80)
