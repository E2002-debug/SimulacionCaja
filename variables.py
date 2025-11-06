
# Número total de cajas en el supermercado
num_cajas = 0

# Lista con la cantidad de personas en cada caja
personas_por_caja = []

# Lista con el número de artículos que tiene cada persona
num_articulos = []

# Tiempo promedio de escaneo por artículo (segundos)
tiempo_escaneo = 0

# Tiempo promedio de cobro por cliente (segundos)
tiempo_cobro = 0

# Tiempo total estimado por cada caja
tiempo_total_caja = []

# Identificador de la mejor caja (la más rápida)
mejor_caja = None

# Variable que representará la caja express
caja_express = {
    "personas": 0,
    "tiempo_escaneo": 0,
    "tiempo_cobro": 0,
    "tiempo_total": 0
}

# Cantidad de ensayos para las simulaciones estadísticas
CANTIDAD_ENSAYOS = 1000

# Configuraciones de casos de prueba
# Cada caso define las variables para simular diferentes escenarios
CASOS_PRUEBA = {
    "Sesgo": {
        'descripcion': 'Caso Sesgo: 2 cajas normales + 1 express (cajeros asignados aleatoriamente: Experto o Principiante)',
        'cantidad_ensayos': CANTIDAD_ENSAYOS,
        'cajas': [
            {
                'tipo': 'Normal',
                'express': False,
                'personas_min': 1,
                'personas_max': 7,
                'articulos_distribucion': [
                    (0.5, 1, 20),   # 50% de clientes: 1-20 artículos
                    (0.3, 21, 30),  # 30% de clientes: 21-30 artículos
                    (0.2, 31, 50)   # 20% de clientes: 31-50 artículos
                ]
            },
            {
                'tipo': 'Normal',
                'express': False,
                'personas_min': 1,
                'personas_max': 7,
                'articulos_distribucion': [
                    (0.5, 1, 20),  # 50% de clientes: 1-20 artículos
                    (0.3, 21, 30),  # 30% de clientes: 21-30 artículos
                    (0.2, 31, 50)   # 20% de clientes: 31-50 artículos
                ]
            },
            {
                'tipo': 'Express',
                'express': True,
                'personas_min': 3,# sesgo hacia más personas
                'personas_max': 9,
                'articulos_distribucion': [
                    (0.8, 1, 5),   # 80% de clientes: 1-5 artículos
                    (0.2, 6, 10)   # 20% de clientes: 6-10 artículos
                ]
            }
        ],
        'cliente_objetivo': {
            'articulos_min': 3,
            'articulos_max': 8,
            'tiempo_cobro_min': 15,
            'tiempo_cobro_max': 30
        },
        'tiempo_cobro_min': 15,
        'tiempo_cobro_max': 30
    },
    "Uniforme": {
        'descripcion': 'Caso Uniforme: Distribuciones uniformes completas dentro de especificaciones',
        'cantidad_ensayos': CANTIDAD_ENSAYOS,
        'cajas': [
            {
                'tipo': 'Normal',
                'express': False,
                'personas_min': 1,
                'personas_max': 9,  # Uniforme entre 1-9 personas
                'articulos_distribucion': [
                    (1.0, 1, 50)   # Distribución uniforme: cualquier cantidad entre 1-50 artículos
                ]
            },
            {
                'tipo': 'Normal',
                'express': False,
                'personas_min': 1,
                'personas_max': 9,
                'articulos_distribucion': [
                    (1.0, 1, 50)
                ]
            },
            {
                'tipo': 'Express',
                'express': True,
                'personas_min': 1,
                'personas_max': 9,  # Uniforme entre 9-16 personas
                'articulos_distribucion': [
                    (1.0, 1, 10)   # Distribución uniforme: cualquier cantidad entre 1-10 artículos
                ]
            }
        ],
        'cliente_objetivo': {
            'articulos_min': 3,
            'articulos_max': 8,
            'tiempo_cobro_min': 15,
            'tiempo_cobro_max': 30
        },
        'tiempo_cobro_min': 15,
        'tiempo_cobro_max': 30
    }
    # Aquí se pueden agregar más casos de prueba fácilmente
    # 3: { ... },
    # 4: { ... }
}
