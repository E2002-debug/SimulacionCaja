import tkinter as tk
import random
import time
import threading

class Persona:
    def __init__(self, articulos):
        self.articulos = articulos
        self.tiempo_cobro = random.randint(15, 30)
    
    def tiempo_atendido(self, t_escaneo):
        return self.articulos * t_escaneo + self.tiempo_cobro
    
class Caja:
    def __init__(self, id_caja, t_escaneo, express=False):
        self.id_caja = id_caja
        self.t_escaneo = t_escaneo
        self.express = express
        self.personas = []
        self.tiempo_total = 0
        self.cantidad_personas = 0

    def generar_personas(self):
        self.cantidad_personas = random.randint(1, 20)
        self.personas = []

        for _ in range(self.cantidad_personas):
            if self.express:
                articulos = random.randint(1, 10)
            else:
                articulos = random.randint(1, 10)
            p = Persona(articulos)
            self.personas.append(p)

        return self.personas

    def atender(self):
        self.tiempo_total = 0
        personas_restantes = self.personas.copy()

        while personas_restantes:
            persona = personas_restantes[0]
            tiempo_persona = persona.tiempo_atendido(self.t_escaneo)
            self.tiempo_total += tiempo_persona
            time.sleep(tiempo_persona / 15)  # velocidad simulación
            personas_restantes.pop(0)

        return self.tiempo_total

    def get_info_personas(self):
        return [(p.articulos, p.tiempo_cobro) for p in self.personas]
    
class SimuladorSupermercado:
    def __init__(self, num_cajas=2):
        self.num_cajas = num_cajas
        self.cajas = []
        self.tiempo_escaneo = [5, 10, 3]  # normal, principiante, express
        self.tiempo_total_caja = []
        self.mejor_caja = None
        self.iniciar_cajas()

    def iniciar_cajas(self):
        self.cajas = []
        for i in range(self.num_cajas):
            express = (i == 2)
            caja = Caja(i + 1, self.tiempo_escaneo[i], express)
            self.cajas.append(caja)

    def generar_personas_para_todas(self):
        personas_por_caja = []
        for caja in self.cajas:
            personas = caja.generar_personas()
            personas_por_caja.append(len(personas))
        return personas_por_caja

    def ejecutar_simulacion(self):
        self.tiempo_total_caja = []
        hilos = []
        resultados = [None] * len(self.cajas)

        def atender_caja(caja, idx):
            resultados[idx] = caja.atender()

        # Crear y ejecutar hilos
        for i, caja in enumerate(self.cajas):
            hilo = threading.Thread(target=atender_caja, args=(caja, i))
            hilos.append(hilo)
            hilo.start()

        # Esperar a que todos los hilos terminen
        for hilo in hilos:
            hilo.join()

        # Recoger resultados
        self.tiempo_total_caja = resultados
        self.calcular_mejor_caja()

        return {
            'tiempos_totales': self.tiempo_total_caja,
            'mejor_caja': self.mejor_caja,
            'personas_por_caja': [caja.cantidad_personas for caja in self.cajas]
        }

    def calcular_mejor_caja(self):
        if self.tiempo_total_caja:
            mejor_idx = self.tiempo_total_caja.index(min(self.tiempo_total_caja))
            self.mejor_caja = mejor_idx + 1
        return self.mejor_caja

    def get_info_cajas(self):
        info = []
        for i, caja in enumerate(self.cajas):
            info.append({
                'id': caja.id_caja,
                'tipo': 'Express' if caja.express else 'Normal',
                'tiempo_escaneo': caja.t_escaneo,
                'personas_en_fila': len(caja.personas),
                'tiempo_total': caja.tiempo_total
            })
        return info
    

if __name__ == "__main__":
    simulador = SimuladorSupermercado(num_cajas=3)
    personas_por_caja = simulador.generar_personas_para_todas()
    print("Personas por caja:", personas_por_caja)
    resultados = simulador.ejecutar_simulacion()
    print("Resultados de la simulación:", resultados)
    info_cajas = simulador.get_info_cajas()
    for info in info_cajas:
        print(f"Caja {info['id']} ({info['tipo']}): Tiempo total {info['tiempo_total']} segundos, Personas en fila {info['personas_en_fila']}")