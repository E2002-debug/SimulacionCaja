import random
import time
import threading


class Persona:
    def __init__(self, articulos, es_objetivo=False):
        self.articulos = articulos
        self.tiempo_cobro = random.randint(15, 30)
        self.es_objetivo = es_objetivo  # Cliente objetivo presente en todas las filas
    
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
        self.atendiendo = False  # Indica si está atendiendo a alguien
        self.atendio_objetivo = False  # Indica si esta caja atendió al cliente objetivo

    def generar_personas(self):
        # Caja express: 9-14 clientes antes del objetivo (siempre más que normal)
        # Cajas normales: 1-9 clientes antes del objetivo
        if self.express:
            self.cantidad_personas = random.randint(10, 16)
        else:
            self.cantidad_personas = random.randint(3, 7)
        
        self.personas = []

        for _ in range(self.cantidad_personas):
            if self.express:
                # Caja express: SESGO realista
                # 80% de las veces: 1-5 artículos (compras rápidas)
                # 20% de las veces: 6-10 artículos (máximo permitido)
                if random.random() < 0.8:
                    articulos = random.randint(1, 5)
                else:
                    articulos = random.randint(6, 10)
            else:
                # Cajas normales: SESGO realista
                # 50% de las veces: 1-15 artículos (compra pequeña)
                # 30% de las veces: 16-30 artículos (compra mediana)
                # 20% de las veces: 31-50 artículos (compra grande)
                rand = random.random()
                if rand < 0.5:
                    articulos = random.randint(1, 15)
                elif rand < 0.8:
                    articulos = random.randint(16, 30)
                else:
                    articulos = random.randint(31, 50)
            p = Persona(articulos)
            self.personas.append(p)

        return self.personas

    def atender(self, simulador=None):
        self.tiempo_total = 0

        while self.personas:
            self.atendiendo = True
            persona = self.personas[0]
            tiempo_persona = persona.tiempo_atendido(self.t_escaneo)
            self.tiempo_total += tiempo_persona
            
            # Usar el acelerador de tiempo del simulador para la animación
            acelerador = simulador.acelerador_tiempo if simulador and hasattr(simulador, 'acelerador_tiempo') else 15
            time.sleep(tiempo_persona / acelerador)
            self.personas.pop(0)  # Eliminar la persona atendida
            self.atendiendo = False
            
            # DESPUÉS de atender, verificar si era el cliente objetivo
            if persona.es_objetivo and simulador and not self.atendio_objetivo:
                self.atendio_objetivo = True
                if simulador.caja_ganadora_objetivo is None:
                    simulador.caja_ganadora_objetivo = self.id_caja
                    # DESPUÉS de atender al cliente objetivo, detener todas las cajas
                    simulador.objetivo_atendido = True
            
            # Si el cliente objetivo ya fue atendido en alguna caja, detener esta caja
            if simulador and simulador.objetivo_atendido:
                break

        return self.tiempo_total

    def get_info_personas(self):
        return [(p.articulos, p.tiempo_cobro) for p in self.personas]


class SimuladorSupermercado:
    def __init__(self, num_cajas=2):
        self.num_cajas = num_cajas
        self.cajas = []
        self.acelerador_tiempo = 15  # Por defecto 15x (se puede cambiar desde interfaz)
        # Tiempos de escaneo aleatorios según tipo de cajero (incluye empaquetado):
        # Caja 1 (Normal con EXPERTO): random 2.5-4s
        # Caja 2 (Normal con PRINCIPIANTE): random 4.5-7s
        # Caja 3 (Express con EXPERTO): random 2.5-4s
        self.tiempo_escaneo = [
            random.uniform(2.5, 4.0),  # Caja 1: experto
            random.uniform(4.5, 7.0),  # Caja 2: principiante
            random.uniform(2.5, 4.0)   # Caja 3: experto (express)
        ]
        self.tiempo_total_caja = []
        self.mejor_caja = None
        self.cliente_objetivo = None  # El cliente que está en las 3 filas
        self.caja_ganadora_objetivo = None  # Qué caja atendió primero al cliente objetivo
        self.objetivo_atendido = False  # Flag para detener todas las cajas cuando el objetivo es atendido
        self.iniciar_cajas()

    def iniciar_cajas(self):
        self.cajas = []
        roles_cajeros = ['Experto', 'Principiante']  # Tipos posibles
        random.shuffle(roles_cajeros)
        
        for i in range(self.num_cajas):
            # Asignar tipo de cajero aleatoriamente
            rol = random.choice(roles_cajeros)
            express = (i == 2)
            
            # Ajustar el tiempo de escaneo según el tipo de cajero
            if rol == 'Experto':
                t_escaneo = random.uniform(2.5, 4.0)
            else:
                t_escaneo = random.uniform(4.5, 7.0)
            
            caja = Caja(i + 1, t_escaneo, express)
            caja.cajero = rol  # Guardamos el rol del cajero para mostrarlo luego
            self.cajas.append(caja)

    def generar_personas_para_todas(self):
        personas_por_caja = []
        
        # Crear el cliente objetivo con un número aleatorio de artículos (apto para express)
        articulos_objetivo = random.randint(3, 8)
        tiempo_cobro_objetivo = random.randint(15, 30)
        
        for caja in self.cajas:
            personas = caja.generar_personas()
            
            # Agregar el cliente objetivo al FINAL de cada fila (última posición)
            cliente_objetivo = Persona(articulos_objetivo, es_objetivo=True)
            cliente_objetivo.tiempo_cobro = tiempo_cobro_objetivo  # Mismo tiempo de cobro
            caja.personas.append(cliente_objetivo)  # Al FINAL de la fila
            
            personas_por_caja.append(len(caja.personas))
        
        # Guardar referencia del cliente objetivo
        self.cliente_objetivo = self.cajas[0].personas[-1]  # Último de la primera caja
        
        return personas_por_caja

    def ejecutar_simulacion(self):
        self.tiempo_total_caja = []
        self.caja_ganadora_objetivo = None  # Resetear
        self.objetivo_atendido = False  # Resetear
        hilos = []
        resultados = [None] * len(self.cajas)

        def atender_caja(caja, idx):
            resultados[idx] = caja.atender(self)  # Pasar referencia del simulador

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
            'personas_por_caja': [caja.cantidad_personas for caja in self.cajas],
            'caja_ganadora_objetivo': self.caja_ganadora_objetivo
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
