
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
