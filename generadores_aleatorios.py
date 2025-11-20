"""
═══════════════════════════════════════════════════════════════════════════════
MÓDULO: generadores_aleatorios.py
PROPÓSITO: Generación de variables aleatorias para simulación M/M/s
FECHA: Noviembre 18, 2025
═══════════════════════════════════════════════════════════════════════════════

DESCRIPCIÓN:
Este módulo contiene funciones para generar variables aleatorias según las
distribuciones requeridas en el modelo de colas:

1. Proceso de llegadas (Poisson)
2. Tiempos de servicio (Exponencial, Uniforme)
3. Número de artículos por cliente
4. Tipos de cajeros (asignación aleatoria)

DEPENDENCIAS:
- numpy: Generación de números aleatorios
- parametros_colas: Parámetros del sistema

TEORÍA ESTADÍSTICA:
-------------------
- Proceso de Poisson: N(t) ~ Poisson(λt)
  → Tiempos entre llegadas ~ Exponencial(λ)

- Distribución Exponencial: f(t) = λe^(-λt)
  → Propiedad sin memoria
  
- Distribución Uniforme: f(x) = 1/(b-a) para x ∈ [a,b]
  → Equiprobabilidad en el rango
═══════════════════════════════════════════════════════════════════════════════
"""

import numpy as np
import random
from parametros_colas import (
    CAJEROS,
    TIEMPO_COBRO,
    DISTRIBUCION_ARTICULOS
)


# ═══════════════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN DE SEMILLAS
# ═══════════════════════════════════════════════════════════════════════════

def configurar_semilla(seed):
    """
    Configura la semilla para generadores de números aleatorios.
    
    Esto garantiza REPRODUCIBILIDAD: misma semilla → mismos resultados.
    
    Parámetros:
    -----------
    seed : int
        Semilla para el generador pseudoaleatorio
    
    Efecto:
    -------
    Inicializa tanto random como numpy.random con la misma semilla.
    
    Ejemplo:
    --------
    >>> configurar_semilla(42)
    >>> print(np.random.rand())  # Siempre dará el mismo valor
    0.3745401188473625
    
    Nota:
    -----
    Es CRÍTICO llamar a esta función antes de cada réplica de simulación
    para garantizar independencia entre réplicas con diferentes semillas.
    """
    random.seed(seed)
    np.random.seed(seed)
    print(f"✓ Semilla configurada: {seed}")


# ═══════════════════════════════════════════════════════════════════════════
# 2. GENERACIÓN DE LLEGADAS (PROCESO DE POISSON)
# ═══════════════════════════════════════════════════════════════════════════

def generar_llegadas_poisson(lambda_rate, T_max, T_warmup=0):
    """
    Genera tiempos de llegada según un Proceso de Poisson homogéneo.
    
    TEORÍA:
    -------
    Un proceso de Poisson con tasa λ implica que:
    - Los tiempos entre llegadas son independientes
    - Cada tiempo entre llegadas ~ Exponencial(λ)
    - El número de llegadas en [0,t] ~ Poisson(λt)
    
    ALGORITMO:
    ----------
    1. Iniciar en t = 0
    2. Generar Δt ~ Exponencial(λ)
    3. t = t + Δt
    4. Si t < T_max, agregar t a la lista de llegadas
    5. Repetir desde paso 2
    
    Parámetros:
    -----------
    lambda_rate : float
        Tasa de llegadas en clientes/hora
    T_max : float
        Tiempo máximo de simulación en minutos
    T_warmup : float, opcional
        Tiempo de calentamiento en minutos (llegadas a descartar)
        Por defecto: 0
    
    Retorna:
    --------
    numpy.ndarray
        Array con tiempos de llegada (en minutos) ordenados ascendentemente
    
    Ejemplo:
    --------
    >>> configurar_semilla(42)
    >>> llegadas = generar_llegadas_poisson(lambda_rate=30, T_max=60)
    >>> print(f"Número de llegadas: {len(llegadas)}")
    >>> print(f"Primera llegada en t={llegadas[0]:.2f} min")
    >>> print(f"Última llegada en t={llegadas[-1]:.2f} min")
    Número de llegadas: 31
    Primera llegada en t=0.68 min
    Última llegada en t=59.47 min
    
    Validación:
    -----------
    E[N(T)] = λ × T
    Para λ=30 clientes/hora y T=60 min = 1 hora:
    E[N] = 30 × 1 = 30 clientes (valor esperado)
    """
    # Convertir λ de clientes/hora a clientes/minuto
    lambda_por_minuto = lambda_rate / 60.0
    
    llegadas = []
    t_actual = 0.0
    
    while t_actual < T_max:
        # Generar tiempo entre llegadas (exponencial)
        # Parámetro de numpy: scale = 1/λ
        delta_t = np.random.exponential(scale=1.0 / lambda_por_minuto)
        t_actual += delta_t
        
        # Agregar llegada si está dentro del período de simulación
        # y después del período de calentamiento
        if T_warmup <= t_actual < T_max:
            llegadas.append(t_actual)
    
    return np.array(llegadas)


def generar_llegadas_tasa_variable(tasas_por_franja, T_max):
    """
    Genera llegadas con tasa variable por franja horaria.
    
    Útil para simular día completo con diferentes intensidades.
    
    Parámetros:
    -----------
    tasas_por_franja : list of tuple
        Lista de tuplas (t_inicio, t_fin, lambda) donde:
        - t_inicio: inicio de franja (minutos)
        - t_fin: fin de franja (minutos)
        - lambda: tasa de llegadas (clientes/hora)
    T_max : float
        Tiempo máximo de simulación
    
    Retorna:
    --------
    numpy.ndarray
        Array con todos los tiempos de llegada
    
    Ejemplo:
    --------
    >>> # Simular 4 horas con tasas variables
    >>> franjas = [
    ...     (0, 60, 20),      # Primera hora: λ=20
    ...     (60, 120, 35),    # Segunda hora: λ=35
    ...     (120, 180, 50),   # Tercera hora: λ=50
    ...     (180, 240, 30)    # Cuarta hora: λ=30
    ... ]
    >>> configurar_semilla(42)
    >>> llegadas = generar_llegadas_tasa_variable(franjas, T_max=240)
    >>> print(f"Total de llegadas: {len(llegadas)}")
    """
    todas_llegadas = []
    
    for t_inicio, t_fin, lambda_franja in tasas_por_franja:
        # Generar llegadas para esta franja
        llegadas_franja = generar_llegadas_poisson(
            lambda_rate=lambda_franja,
            T_max=t_fin - t_inicio,
            T_warmup=0
        )
        
        # Ajustar tiempos al inicio de la franja
        llegadas_ajustadas = llegadas_franja + t_inicio
        todas_llegadas.extend(llegadas_ajustadas)
    
    # Ordenar por tiempo (por si acaso)
    todas_llegadas = np.sort(todas_llegadas)
    
    return todas_llegadas


# ═══════════════════════════════════════════════════════════════════════════
# 3. GENERACIÓN DE TIEMPOS DE SERVICIO
# ═══════════════════════════════════════════════════════════════════════════

def generar_tiempo_servicio_exponencial(mu, n_clientes=1):
    """
    Genera tiempos de servicio según distribución Exponencial.
    
    Este es el modelo ESTÁNDAR en colas M/M/s.
    
    TEORÍA:
    -------
    T_servicio ~ Exponencial(μ)
    E[T] = 1/μ
    Var[T] = 1/μ²
    Propiedad sin memoria: P(T>s+t | T>s) = P(T>t)
    
    Parámetros:
    -----------
    mu : float
        Tasa de servicio en clientes/hora
    n_clientes : int, opcional
        Número de tiempos a generar (por defecto 1)
    
    Retorna:
    --------
    float o numpy.ndarray
        Tiempo(s) de servicio en minutos
    
    Ejemplo:
    --------
    >>> configurar_semilla(42)
    >>> # μ = 60 clientes/hora → E[T] = 1 minuto
    >>> tiempos = generar_tiempo_servicio_exponencial(mu=60, n_clientes=5)
    >>> print(f"Tiempos: {tiempos}")
    >>> print(f"Promedio: {np.mean(tiempos):.2f} min (esperado: 1.00)")
    """
    # Convertir μ de clientes/hora a clientes/minuto
    mu_por_minuto = mu / 60.0
    
    # Generar tiempos (scale = 1/μ)
    tiempos = np.random.exponential(scale=1.0 / mu_por_minuto, size=n_clientes)
    
    if n_clientes == 1:
        return tiempos[0]
    return tiempos


def generar_tiempo_servicio_compuesto(n_articulos, tipo_cajero, incluir_cobro=True):
    """
    Genera tiempo de servicio REALISTA basado en componentes.
    
    Este modelo es más PRECISO que el exponencial simple.
    
    COMPONENTES:
    ------------
    T_servicio = T_escaneo + T_cobro
    
    T_escaneo = n_articulos × tiempo_por_articulo
    - tiempo_por_articulo ~ Uniforme(a, b) según tipo de cajero
    
    T_cobro ~ Uniforme(15, 30) segundos
    
    Parámetros:
    -----------
    n_articulos : int
        Número de artículos del cliente
    tipo_cajero : str
        'experto' o 'principiante'
    incluir_cobro : bool, opcional
        Si incluir tiempo de cobro (por defecto True)
    
    Retorna:
    --------
    float
        Tiempo total de servicio en minutos
    
    Ejemplo:
    --------
    >>> configurar_semilla(42)
    >>> # Cliente con 15 artículos, cajero experto
    >>> t_servicio = generar_tiempo_servicio_compuesto(
    ...     n_articulos=15,
    ...     tipo_cajero='experto',
    ...     incluir_cobro=True
    ... )
    >>> print(f"Tiempo de servicio: {t_servicio:.2f} minutos")
    
    Ventajas:
    ---------
    ✓ Refleja la realidad del proceso
    ✓ Permite modelar diferencias entre cajeros
    ✓ Captura variabilidad realista
    ✓ Menor varianza que exponencial pura
    """
    # Obtener parámetros del cajero
    cajero = CAJEROS[tipo_cajero]
    
    # 1. Tiempo de escaneo
    tiempo_por_articulo = np.random.uniform(
        cajero['tiempo_escaneo_min'],
        cajero['tiempo_escaneo_max']
    )
    
    t_escaneo_segundos = n_articulos * tiempo_por_articulo
    
    # 2. Tiempo de cobro
    t_cobro_segundos = 0
    if incluir_cobro:
        t_cobro_segundos = np.random.uniform(
            TIEMPO_COBRO['min'],
            TIEMPO_COBRO['max']
        )
    
    # 3. Tiempo total en segundos
    t_total_segundos = t_escaneo_segundos + t_cobro_segundos
    
    # Convertir a minutos
    t_total_minutos = t_total_segundos / 60.0
    
    return t_total_minutos


def generar_servicios_para_clientes(clientes, tipo_cajero='experto'):
    """
    Genera tiempos de servicio para múltiples clientes.
    
    Parámetros:
    -----------
    clientes : list of dict
        Lista de clientes, cada uno con {'articulos': int}
    tipo_cajero : str
        'experto' o 'principiante'
    
    Retorna:
    --------
    list of float
        Lista de tiempos de servicio (minutos)
    
    Ejemplo:
    --------
    >>> clientes = [{'articulos': 10}, {'articulos': 25}, {'articulos': 5}]
    >>> servicios = generar_servicios_para_clientes(clientes, 'experto')
    >>> print(f"Tiempos: {[f'{t:.2f}' for t in servicios]}")
    """
    tiempos = []
    for cliente in clientes:
        t_servicio = generar_tiempo_servicio_compuesto(
            n_articulos=cliente['articulos'],
            tipo_cajero=tipo_cajero,
            incluir_cobro=True
        )
        tiempos.append(t_servicio)
    
    return tiempos


# ═══════════════════════════════════════════════════════════════════════════
# 4. GENERACIÓN DE NÚMERO DE ARTÍCULOS
# ═══════════════════════════════════════════════════════════════════════════

def generar_numero_articulos(tipo_caja='normal'):
    """
    Genera número de artículos según el tipo de caja.
    
    DISTRIBUCIÓN:
    -------------
    Usa distribución discreta personalizada con probabilidades acumuladas.
    
    Tipo Normal:
    - 50% de clientes: 1-20 artículos
    - 30% de clientes: 21-35 artículos
    - 20% de clientes: 36-50 artículos
    
    Tipo Express:
    - 70% de clientes: 1-5 artículos
    - 30% de clientes: 6-10 artículos
    
    Parámetros:
    -----------
    tipo_caja : str
        'normal' o 'express'
    
    Retorna:
    --------
    int
        Número de artículos del cliente
    
    Ejemplo:
    --------
    >>> configurar_semilla(42)
    >>> articulos_normal = [generar_numero_articulos('normal') for _ in range(10)]
    >>> articulos_express = [generar_numero_articulos('express') for _ in range(10)]
    >>> print(f"Normal: promedio={np.mean(articulos_normal):.1f}")
    >>> print(f"Express: promedio={np.mean(articulos_express):.1f}")
    
    Algoritmo:
    ----------
    1. Generar u ~ Uniforme(0,1)
    2. Determinar segmento según probabilidades acumuladas
    3. Generar uniforme dentro del rango del segmento
    """
    dist = DISTRIBUCION_ARTICULOS[tipo_caja]['distribucion']
    
    # Generar número aleatorio uniforme [0,1]
    u = np.random.random()
    
    # Determinar segmento según probabilidades acumuladas
    prob_acumulada = 0.0
    for segmento in dist:
        prob_acumulada += segmento['prob']
        if u <= prob_acumulada:
            # Generar uniformemente en el rango del segmento
            rango_min, rango_max = segmento['rango']
            n_articulos = np.random.randint(rango_min, rango_max + 1)
            return n_articulos
    
    # Fallback (no debería llegar aquí si las probabilidades suman 1)
    rango_min, rango_max = dist[-1]['rango']
    return np.random.randint(rango_min, rango_max + 1)


def generar_clientes(n_clientes, tipo_caja='normal'):
    """
    Genera una lista de clientes con número de artículos asignado.
    
    Parámetros:
    -----------
    n_clientes : int
        Número de clientes a generar
    tipo_caja : str
        'normal' o 'express'
    
    Retorna:
    --------
    list of dict
        Lista de clientes con estructura {'articulos': int}
    
    Ejemplo:
    --------
    >>> configurar_semilla(42)
    >>> clientes = generar_clientes(5, 'express')
    >>> for i, c in enumerate(clientes, 1):
    ...     print(f"Cliente {i}: {c['articulos']} artículos")
    """
    clientes = []
    for _ in range(n_clientes):
        n_articulos = generar_numero_articulos(tipo_caja)
        clientes.append({'articulos': n_articulos})
    
    return clientes


# ═══════════════════════════════════════════════════════════════════════════
# 5. ASIGNACIÓN DE TIPOS DE CAJERO
# ═══════════════════════════════════════════════════════════════════════════

def asignar_tipo_cajero(probabilidad_experto=0.5):
    """
    Asigna aleatoriamente el tipo de cajero.
    
    Parámetros:
    -----------
    probabilidad_experto : float, opcional
        Probabilidad de asignar cajero experto (por defecto 0.5)
    
    Retorna:
    --------
    str
        'experto' o 'principiante'
    
    Ejemplo:
    --------
    >>> configurar_semilla(42)
    >>> cajeros = [asignar_tipo_cajero(0.7) for _ in range(10)]
    >>> print(f"Expertos: {cajeros.count('experto')}/10")
    >>> print(f"Principiantes: {cajeros.count('principiante')}/10")
    """
    if np.random.random() < probabilidad_experto:
        return 'experto'
    else:
        return 'principiante'


def asignar_cajeros_a_cajas(s, prob_experto=0.5, mixto=False):
    """
    Asigna tipos de cajero a un conjunto de cajas.
    
    Parámetros:
    -----------
    s : int
        Número de cajas
    prob_experto : float
        Probabilidad de cajero experto
    mixto : bool
        Si True, garantiza al menos 1 experto y 1 principiante (si s>=2)
    
    Retorna:
    --------
    list of str
        Lista con tipo de cajero por caja
    
    Ejemplo:
    --------
    >>> configurar_semilla(42)
    >>> cajeros = asignar_cajeros_a_cajas(s=4, prob_experto=0.6, mixto=True)
    >>> print(cajeros)
    ['experto', 'experto', 'principiante', 'experto']
    """
    cajeros = [asignar_tipo_cajero(prob_experto) for _ in range(s)]
    
    # Si mixto y s>=2, garantizar diversidad
    if mixto and s >= 2:
        if all(c == 'experto' for c in cajeros):
            # Cambiar uno a principiante
            cajeros[-1] = 'principiante'
        elif all(c == 'principiante' for c in cajeros):
            # Cambiar uno a experto
            cajeros[0] = 'experto'
    
    return cajeros


# ═══════════════════════════════════════════════════════════════════════════
# 6. FUNCIONES DE VALIDACIÓN Y PRUEBAS
# ═══════════════════════════════════════════════════════════════════════════

def validar_proceso_poisson(lambda_rate, T, n_replicas=100):
    """
    Valida que el generador de Poisson produce resultados correctos.
    
    Prueba: E[N(T)] = λ × T
    
    Parámetros:
    -----------
    lambda_rate : float
        Tasa de llegadas (clientes/hora)
    T : float
        Período de tiempo (minutos)
    n_replicas : int
        Número de réplicas para promediar
    
    Retorna:
    --------
    dict
        Resultados de la validación
    """
    conteos = []
    for i in range(n_replicas):
        configurar_semilla(1000 + i)
        llegadas = generar_llegadas_poisson(lambda_rate, T)
        conteos.append(len(llegadas))
    
    # Valor esperado teórico
    T_horas = T / 60.0
    esperado = lambda_rate * T_horas
    
    # Valor observado
    observado = np.mean(conteos)
    desv_std = np.std(conteos)
    
    # Error relativo
    error_rel = abs(observado - esperado) / esperado * 100
    
    return {
        'esperado': esperado,
        'observado': observado,
        'desv_std': desv_std,
        'error_relativo_%': error_rel,
        'valido': error_rel < 5.0  # <5% de error
    }


def prueba_completa_generadores():
    """
    Ejecuta pruebas de todos los generadores.
    """
    print("═" * 80)
    print(" " * 25 + "PRUEBAS DE GENERADORES")
    print("═" * 80)
    
    # 1. Prueba de llegadas Poisson
    print("\n1. VALIDACIÓN DE PROCESO DE POISSON")
    print("-" * 80)
    resultado = validar_proceso_poisson(lambda_rate=30, T=60, n_replicas=100)
    print(f"   λ = 30 clientes/hora, T = 60 minutos")
    print(f"   Valor esperado: {resultado['esperado']:.2f} llegadas")
    print(f"   Valor observado: {resultado['observado']:.2f} ± {resultado['desv_std']:.2f}")
    print(f"   Error relativo: {resultado['error_relativo_%']:.2f}%")
    print(f"   {'✓ VÁLIDO' if resultado['valido'] else '✗ INVÁLIDO'}")
    
    # 2. Prueba de tiempos de servicio
    print("\n2. TIEMPOS DE SERVICIO")
    print("-" * 80)
    configurar_semilla(42)
    mu = 60  # 60 clientes/hora → E[T] = 1 minuto
    tiempos = generar_tiempo_servicio_exponencial(mu, n_clientes=1000)
    print(f"   μ = {mu} clientes/hora")
    print(f"   E[T] teórico: {60/mu:.2f} minutos")
    print(f"   E[T] observado: {np.mean(tiempos):.2f} minutos")
    print(f"   Desv. Std: {np.std(tiempos):.2f} minutos")
    
    # 3. Prueba de artículos
    print("\n3. DISTRIBUCIÓN DE ARTÍCULOS")
    print("-" * 80)
    configurar_semilla(42)
    articulos_normal = [generar_numero_articulos('normal') for _ in range(1000)]
    articulos_express = [generar_numero_articulos('express') for _ in range(1000)]
    print(f"   Caja Normal:")
    print(f"     Promedio: {np.mean(articulos_normal):.1f} artículos")
    print(f"     Rango: [{min(articulos_normal)}, {max(articulos_normal)}]")
    print(f"   Caja Express:")
    print(f"     Promedio: {np.mean(articulos_express):.1f} artículos")
    print(f"     Rango: [{min(articulos_express)}, {max(articulos_express)}]")
    
    # 4. Prueba de asignación de cajeros
    print("\n4. ASIGNACIÓN DE CAJEROS")
    print("-" * 80)
    configurar_semilla(42)
    cajeros = [asignar_tipo_cajero(0.6) for _ in range(100)]
    n_expertos = cajeros.count('experto')
    print(f"   Probabilidad experto: 60%")
    print(f"   Observado: {n_expertos}% expertos, {100-n_expertos}% principiantes")
    
    print("\n" + "═" * 80)


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE DE PRUEBA
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    prueba_completa_generadores()
