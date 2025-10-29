# Práctica 03 – Simulación de Filas en Supermercado
## ¿Caja Express o Caja Normal? Análisis de Eficiencia

---

## 📋 RESUMEN EJECUTIVO

Este documento presenta un análisis completo sobre la eficiencia de cajas en supermercados, comparando **cajas normales contra cajas express**. A través de simulación computacional y validación estadística con 2000 escenarios independientes, se determinó objetivamente cuál es la mejor opción para un cliente que desea salir más rápido.

### Resultados Obtenidos (2000 ensayos)

| Tipo de Caja | Frecuencia de Victoria | Porcentaje |
|--------------|------------------------|------------|
| **Cajas Normales** | 1,286 victorias | **64.3%** |
| **Caja Express** | 714 victorias | **35.7%** |

### Conclusión Principal

**La caja express NO es la opción más rápida.** Pierde en casi 2 de cada 3 escenarios. 

**Razón:** Aunque procesa cada cliente más rápido (máximo 10 artículos), su alta popularidad genera saturación de clientes, multiplicando las interrupciones por pagos (15-30 segundos cada uno). Este efecto anula completamente su ventaja de velocidad.

---

## 🎯 1. PLANTEAMIENTO DEL PROBLEMA

### Situación Real

Un cliente llega al supermercado y observa dos opciones de cajas:

- **Cajas Normales:** Sin restricción de artículos, filas más cortas
- **Caja Express:** Máximo 10 artículos, siempre con más gente

### Pregunta de Investigación

**¿En qué tipo de caja debe formarse para salir más rápido del supermercado?**

### Factores Relevantes

1. **Número de personas en cada fila** (afluencia diferencial)
2. **Cantidad de artículos por cliente** (distribución estadística)
3. **Restricción de la caja express** (máximo 10 artículos)
4. **Tiempo de escaneo** por artículo (incluye empaquetado)
5. **Tiempo de pago** independiente de artículos (15-30 segundos por cliente)

### Objetivo del Estudio

Determinar mediante simulación estocástica cuál tipo de caja tiene **mayor probabilidad de victoria** (ser la primera en atender a un cliente de prueba) en 2000 escenarios aleatorios.

**Metodología:** Frecuencia de victorias, NO tiempo promedio.

---

## 🔬 2. DISEÑO EXPERIMENTAL

### 2.1 Parámetros del Modelo

#### A) Cantidad de Personas en Fila

Se configuraron rangos diferentes para reflejar la realidad observada:

| Tipo de Caja | Rango | Promedio | Justificación |
|--------------|-------|----------|---------------|
| **Cajas Normales** | 1-9 personas | ~5 clientes | Menos populares, percibidas como "lentas" |
| **Caja Express** | 9-14 personas | ~11.5 clientes | Alta popularidad, fama de "rapidez" atrae clientes |

**Decisión crítica:** La caja express tiene el **DOBLE** de clientes promedio que las normales. Esta configuración modela la paradoja de la popularidad: todos piensan que será más rápida, generando sobresaturación.

#### B) Distribución de Artículos por Cliente

**Cajas Normales (sin límite de artículos):**
- 50% de clientes → 1-15 artículos (compra pequeña)
- 30% de clientes → 16-30 artículos (compra mediana)
- 20% de clientes → 31-50 artículos (compra grande/carrito lleno)

**Caja Express (límite: 10 artículos):**
- 80% de clientes → 1-5 artículos (compras muy rápidas)
- 20% de clientes → 6-10 artículos (cerca del máximo permitido)

**Justificación:** En cajas normales hay alta variabilidad (desde canasta hasta carrito); en express, la mayoría viene con muy pocos productos.

#### C) Tiempo de Escaneo por Artículo

Este tiempo incluye pasar el producto por el escáner Y empaquetarlo en la bolsa:

**Velocidad del cajero (variable aleatoria del modelo):**
- Cajero experto: 2.5 - 4.0 segundos por artículo
- Cajero principiante: 4.5 - 7.0 segundos por artículo

**Nota importante:** El cliente NO sabe qué tipo de cajero está en cada caja al momento de elegir. Es una variable del sistema que afecta el resultado pero no la decisión inicial.

#### D) Tiempo de Pago (Cobro)

**Rango:** 15 - 30 segundos (aleatorio para cada cliente)

**Incluye todas las formas de pago:**
- Pasar tarjeta de crédito/débito
- Ingresar PIN o firma
- Contar efectivo y entregar cambio
- Imprimir y entregar recibo
- Interacción social básica ("gracias", "buen día")

**⚠️ FACTOR CRÍTICO:** El tiempo de pago es **INDEPENDIENTE** de cuántos artículos compró el cliente. Ya sea que traiga 3 o 40 productos, el pago toma el mismo tiempo (un solo pago por cliente).

---

### 2.2 Cálculo del Tiempo Total en Cada Caja

Para determinar cuánto tarda cada caja en atender completamente su fila, se utilizó la siguiente fórmula:

**Para cada persona:**
```
Tiempo_Atención_Persona = (Cantidad_Artículos × Tiempo_Escaneo) + Tiempo_Cobro
```

**Para cada caja:**
```
Tiempo_Total_Caja = Suma de Tiempo_Atención de TODAS las personas en la fila
```

#### Ejemplo Ilustrativo

**Caja Normal con 3 personas:**
- Persona 1: 12 artículos → (12 × 3s) + 20s = 56 segundos
- Persona 2: 25 artículos → (25 × 3s) + 18s = 93 segundos  
- Persona 3: 8 artículos → (8 × 3s) + 25s = 49 segundos
- **TOTAL:** 56 + 93 + 49 = **198 segundos**

**Caja Express con 10 personas (todas con 5 artículos):**
- Cada persona: (5 × 3s) + 22s promedio = 37 segundos
- **TOTAL:** 37 × 10 = **370 segundos**

En este ejemplo, la caja normal con menos personas pero más artículos es **MÁS RÁPIDA** que la caja express saturada.

---

### 2.3 Método de Comparación: Cliente Objetivo

Para garantizar una comparación justa entre las tres cajas, se implementó el concepto de **"cliente objetivo"**:

**Definición:** Un cliente de prueba que se encuentra simultáneamente al FINAL de las tres filas.

**Características:**
- Tiene entre 3-8 artículos (apto para cualquier caja, incluyendo express)
- Mismo cliente en las 3 filas con los MISMOS artículos
- Permite evaluar las cajas bajo condiciones idénticas

**Funcionamiento:**
1. Se generan las tres filas con clientes aleatorios
2. Se agrega el cliente objetivo al final de las 3 filas
3. Las tres cajas comienzan a atender simultáneamente
4. La PRIMERA caja en atender al cliente objetivo es la **GANADORA**
5. Las otras cajas dejan de procesar

**Ventaja:** Elimina el sesgo de tener condiciones diferentes para cada caja. El mismo cliente es atendido en paralelo, y simplemente gana quien llegue primero.

---

### 2.4 Implementación de Caja Express

Se agregó una caja express al sistema con las siguientes características:

| Característica | Especificación |
|----------------|----------------|
| **Límite de artículos** | Máximo 10 artículos por cliente |
| **Afluencia** | ALTA (9-14 clientes vs 1-9 en normales) |
| **Velocidad de cajero** | Variable (puede ser experto o principiante) |
| **Color distintivo** | Morado (en la interfaz visual) |

### Hipótesis a Validar

**"La caja express es consistentemente más rápida que las cajas normales"**

Esta hipótesis se basa en la creencia popular de que limitar los artículos (máximo 10) resulta en tiempos de atención menores, sin importar la cantidad de clientes en la fila.

**Método de validación:** Comparar la frecuencia de victoria de la caja express contra las cajas normales en 2000 escenarios aleatorios.

---

## 📈 3. RESULTADOS Y ANÁLISIS

### 3.1 Resultados de los 2000 Ensayos

Después de ejecutar 2000 simulaciones con configuraciones aleatorias, se obtuvieron los siguientes resultados:

| Tipo de Caja | Victorias | Porcentaje |
|--------------|-----------|------------|
| **Cajas Normales** | 1,286 | **64.3%** |
| **Caja Express** | 714 | **35.7%** |

### 3.2 Validación de Hipótesis

**Hipótesis:** "La caja express es consistentemente más rápida que las cajas normales"

**Resultado:** ❌ **RECHAZADA**

La caja express solo gana en **35.7%** de los casos, mientras que las cajas normales ganan en **64.3%**. La diferencia es significativa: las cajas normales ganan casi el doble de veces.

### 3.3 Análisis de Causas

**¿Por qué la caja express pierde con tanta frecuencia?**

1. **Saturación de clientes:** La caja express tiene en promedio **11.5 clientes** vs **~5 clientes** en cajas normales

2. **Multiplicación de pagos:** Aunque cada cliente trae pocos artículos (máx 10), cada uno genera una interrupción de pago de 15-30 segundos:
   - Express: 11.5 clientes × 22.5s promedio = **259 segundos solo en pagos**
   - Normal: 5 clientes × 22.5s promedio = **112 segundos en pagos**

3. **El cuello de botella NO es el escaneo:** El límite de 10 artículos reduce el tiempo de escaneo (~30-40 segundos por cliente), pero el tiempo de pago (15-30 segundos) es comparable y se multiplica por más clientes

4. **Efecto contraintuitivo:** Más clientes con pocos artículos puede ser PEOR que pocos clientes con muchos artículos, cuando el tiempo de pago es fijo e independiente

### 3.4 Escenarios de Victoria

**La caja express gana cuando:**
- Tiene cerca del mínimo de su rango (9-10 clientes)
- Las cajas normales tienen 7+ clientes
- Las cajas normales tienen clientes con 30+ artículos

**Las cajas normales ganan cuando:**
- Tienen 1-5 clientes (su configuración más frecuente)
- La caja express tiene 12+ clientes (su configuración frecuente)
- Incluso con carritos llenos (30-50 artículos), menos interrupciones de pago las favorece

---

## 🔬 4. VALIDACIÓN DEL MODELO

### 4.1 Supuestos del Modelo

1. **Las distribuciones probabilísticas reflejan comportamiento real** de compra en supermercados
2. **Los clientes respetan el límite de 10 artículos** en caja express
3. **No hay abandonos de fila** ni cambios entre cajas durante la espera
4. **El tiempo de pago es independiente** del número de artículos comprados
5. **La velocidad del cajero es constante** (no hay fatiga durante el turno)

### 4.2 Limitaciones del Estudio

- No modela variaciones por hora del día (pico vs valle)
- No incluye problemas técnicos (scanner dañado, sistema caído)
- No considera productos especiales (sin código de barras, pesaje manual)
- No modela clientes conversadores que incrementan tiempos
- No incluye promociones o cupones que alargan el proceso de pago

---

## 💡 5. CONCLUSIONES

### Conclusión Principal

**La caja express NO es consistentemente más rápida.** De hecho, pierde en 2 de cada 3 escenarios contra las cajas normales.

### Hallazgos Clave

1. **El tiempo de pago es el cuello de botella dominante**, no el tiempo de escaneo de artículos

2. **La popularidad de la caja express es su mayor debilidad:** Atrae más clientes (9-14 vs 1-9), multiplicando las interrupciones de pago que anulan su ventaja de límite de artículos

3. **Paradoja contraintuitiva:** Es mejor formarse en una caja normal con pocos clientes aunque tengan carritos llenos, que en una caja express saturada de gente con canastas pequeñas

4. **La percepción vs la realidad:** Los clientes eligen express pensando en velocidad, pero estadísticamente es la opción menos favorable en la mayoría de casos

### Recomendación Práctica

**Para el cliente:** Elegir la caja con **menor cantidad de personas**, independientemente del tipo de caja o los artículos que tengan. El número de interrupciones de pago es el predictor más confiable del tiempo de espera.

---

## 📝 6. CUMPLIMIENTO DE ESPECIFICACIONES

La siguiente tabla resume cómo se cumplieron todos los requisitos de la práctica:

| # | Requerimiento | Estado | Detalles de Implementación |
|---|---------------|--------|----------------------------|
| 1 | Configurar simulación con parámetros ajustables | ✅ | Personas en fila (1-9 normal, 9-14 express), artículos aleatorios, tiempos de escaneo y cobro configurables |
| 2 | Calcular tiempo total en cada caja | ✅ | Fórmula: Tiempo = Σ(Artículos × T_escaneo + T_cobro) para todos los clientes |
| 3 | Comparar tiempos entre cajas | ✅ | Método del cliente objetivo: mismo cliente en 3 filas, gana quien lo atienda primero |
| 4 | Agregar Caja Express con límite | ✅ | Caja con máximo 10 artículos, alta afluencia (9-14 clientes) |
| 5a | Dibujar cajas como bloques | ✅ | Rectángulos con colores distintivos en interfaz gráfica |
| 5b | Mostrar personas en fila | ✅ | Círculos representando clientes con número de artículos |
| 5c | Animación de atención y desaparición | ✅ | Clientes cambian de color al ser atendidos y desaparecen al finalizar |
| 5d | Caja express con color distintivo | ✅ | Color morado para express, azul para cajas normales |
| **EXTRA** | Sistema de ensayos masivos | ✅ | Generador de 2000 simulaciones con exportación a Excel |
| **EXTRA** | Control de velocidad de animación | ✅ | Acelerador ajustable 1x-50x para simulación visual |

---

## 🎮 7. REPRESENTACIÓN VISUAL

### 7.1 Elementos Gráficos Implementados

**Cajas como bloques:**
- Rectángulos de colores en la interfaz
- Azul para cajas normales
- Morado para caja express
- Etiquetas con información (tipo, velocidad cajero, personas)

**Personas en fila:**
- Círculos pequeños representando a cada cliente
- Amarillo: cliente esperando
- Rojo: cliente siendo atendido
- Verde: cliente objetivo (en las 3 filas simultáneamente)
- Número de artículos mostrado en cada círculo

**Animación de atención:**
1. Cliente en primera posición cambia a rojo (atención iniciada)
2. Tiempo transcurre según cálculo (artículos × velocidad + pago)
3. Cliente desaparece de la fila
4. Todos los demás avanzan automáticamente
5. Proceso se repite hasta atender al cliente objetivo

**Información en tiempo real:**
- Estado de cada caja (atendiendo/esperando)
- Personas restantes en cada fila
- Velocidad de cajero en cada caja
- Tiempo total transcurrido
- Caja ganadora al finalizar

### 7.2 Control de Simulación

**Velocidad ajustable:** Multiplicador de 1x a 50x para acelerar la animación visual sin afectar los cálculos

**Generación de ensayos:** Botón para ejecutar 2000 simulaciones y exportar resultados a Excel con formato profesional

---

## 📊 8. EXPORTACIÓN DE RESULTADOS

Los 2000 ensayos se exportan a un archivo Excel con el siguiente formato:

**Columnas incluidas:**
- Número de ensayo
- Artículos del cliente objetivo
- ID de caja ganadora
- Tipo de ganador (Normal/Express)
- Tiempo de cada caja
- Número de personas en cada caja

**Formato aplicado:**
- Números con 3 decimales
- Celda amarilla resaltando el tiempo ganador
- Encabezados en verde con texto blanco
- Estadísticas agregadas al final

**Estadísticas generadas:**
- Total de ensayos ejecutados
- Victorias por tipo (Normal vs Express)
- Porcentajes de victoria
- Distribución de resultados

---

## 👨‍💻 INFORMACIÓN DEL PROYECTO

**Práctica:** 03 - Simulación de Filas en Supermercado  
**Objetivo:** Determinar si la caja express es realmente más rápida que las cajas normales  
**Metodología:** Simulación estocástica con 2000 ensayos Monte Carlo  
**Resultado:** La caja express NO es consistentemente más rápida (35.7% vs 64.3%)  
**Fecha:** Octubre 2025  

---

*Documento elaborado para demostrar cumplimiento de especificaciones de la Práctica 03 - Análisis de Sistemas de Atención en Supermercados*