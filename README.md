# SimulacionCaja
Simulación visual de un sistema de cajeros de supermercado con interfaz gráfica

## 📋 Descripción
Sistema de simulación que modela el funcionamiento de cajas de supermercado con diferentes tipos de cajeros (normal, principiante y express). Visualiza en tiempo real el flujo de clientes (representados como círculos/partículas) en cada caja (representadas como rectángulos).

## 🗂️ Estructura del Proyecto

```
SimulacionCaja/
├── main.py          # Punto de entrada principal
├── interfaz.py      # Interfaz gráfica con tkinter
├── clases.py        # Clases Persona, Caja y SimuladorSupermercado
├── variables.py     # Variables globales (legacy)
└── README.md        # Este archivo
```

## 🎯 Características

- **3 tipos de cajas**: Normal, Principiante y Express
- **Visualización en tiempo real**: Las cajas se muestran como rectángulos de colores
- **Clientes como partículas**: Cada cliente es un círculo pequeño con su cantidad de artículos
- **Simulación paralela**: Múltiples cajas atienden simultáneamente usando hilos
- **Análisis automático**: Determina cuál caja fue la más rápida

## 🚀 Cómo Ejecutar

```bash
python main.py
```

## 🎮 Uso

1. Presiona **"Iniciar Simulación"** para comenzar
2. Observa cómo cada caja atiende a sus clientes en tiempo real
3. Los números dentro de los círculos indican la cantidad de artículos de cada cliente
4. Al finalizar, se marca la caja ganadora con una estrella ⭐
5. Usa **"Reiniciar"** para comenzar una nueva simulación

## 🎨 Elementos Visuales

- **Rectángulos (Cajas)**: 
  - 🟢 Verde = Caja Normal
  - 🔵 Azul = Caja Principiante  
  - 🟠 Naranja = Caja Express

- **Círculos (Clientes/Partículas)**: 
  - 🟡 Amarillo = Cliente en fila
  - Número = Cantidad de artículos

## ⚙️ Configuración

Las variables de simulación se encuentran en `clases.py`:
- `tiempo_escaneo`: [5, 10, 3] segundos por artículo
- `personas`: Entre 1 y 20 por caja (aleatorio)
- `articulos`: Entre 1 y 10 por persona (aleatorio)

## 📦 Dependencias

- Python 3.x
- tkinter (incluido con Python)
- threading (incluido con Python)
 
