import random
import time
import threading

# ---------------------------
# Clase Persona
# ---------------------------
class Persona:
    def __init__(self, articulos, es_objetivo=False):
        """
        Representa a una persona en la fila de la caja.
        :param articulos: número de artículos que lleva.
        :param es_objetivo: si esta persona es el cliente objetivo.
        """
        self.articulos = articulos
        self.tiempo_cobro = random.randint(15, 30)  # Tiempo fijo de cobro aleatorio
        self.es_objetivo = es_objetivo

    def tiempo_atendido(self, t_escaneo):
        """
        Calcula el tiempo que tarda esta persona en la caja.
        :param t_escaneo: tiempo promedio de escaneo por artículo de la caja
        :return: tiempo total de atención
        """
        return self.articulos * t_escaneo + self.tiempo_cobro


# ---------------------------
# Clase Caja
# ---------------------------
class Caja:
    def __init__(self, id_caja, t_escaneo, express=False):
        """
        Representa una caja en el supermercado.
        :param id_caja: número identificador de la caja
        :param t_escaneo: tiempo promedio de escaneo por artículo
        :param express: si la caja es express
        """
        self.id_caja = id_caja
        self.t_escaneo = t_escaneo
        self.express = express
        self.personas = []  # Lista de personas en la fila
        self.tiempo_total = 0
        self.cantidad_personas = 0
        self.atendiendo = False
        self.atendio_objetivo = False  # Si atendió al cliente objetivo

    def generar_personas(self):
        """
        Genera aleatoriamente personas en la fila según el tipo de caja
        """
        self.cantidad_personas = random.randint(10, 16) if self.express else random.randint(3, 7)
        self.personas = []

        for _ in range(self.cantidad_personas):
            if self.express:
                # Caja express: la mayoría con pocos artículos
                articulos = random.randint(1,5) if random.random() < 0.8 else random.randint(6,10)
            else:
                # Caja normal: mezcla de compras
                r = random.random()
                if r < 0.5:
                    articulos = random.randint(1,15)
                elif r < 0.8:
                    articulos = random.randint(16,30)
                else:
                    articulos = random.randint(31,50)
            self.personas.append(Persona(articulos))
        return self.personas

    def atender(self, simulador=None):
        """
        Atiende a todas las personas de la fila. Marca al cliente objetivo si lo atiende primero.
        """
        self.tiempo_total = 0

        while self.personas:
            self.atendiendo = True
            persona = self.personas[0]
            tiempo_persona = persona.tiempo_atendido(self.t_escaneo)
            self.tiempo_total += tiempo_persona

            # Simula tiempo real acelerado
            acelerador = getattr(simulador, 'acelerador_tiempo', 15)
            time.sleep(tiempo_persona / acelerador)
            self.personas.pop(0)  # Elimina la persona atendida
            self.atendiendo = False

            # Verificar cliente objetivo
            if persona.es_objetivo and simulador and not self.atendio_objetivo:
                self.atendio_objetivo = True
                if simulador.caja_ganadora_objetivo is None:
                    simulador.caja_ganadora_objetivo = self.id_caja
        return self.tiempo_total


# ---------------------------
# Clase SimuladorSupermercado
# ---------------------------
class SimuladorSupermercado:
    def __init__(self, num_cajas=3):
        """
        Simulador de todas las cajas.
        """
        self.num_cajas = num_cajas
        self.cajas = []
        self.acelerador_tiempo = 15
        self.tiempo_total_caja = []
        self.mejor_caja = None
        self.cliente_objetivo = None
        self.caja_ganadora_objetivo = None
        self.objetivo_atendido = False
        self.iniciar_cajas()

    def iniciar_cajas(self):
        """
        Inicializa las cajas con cajeros aleatorios y tipo express
        """
        self.cajas = []
        for i in range(self.num_cajas):
            rol = random.choice(['Experto','Principiante'])
            t_escaneo = random.uniform(2.5,4.0) if rol=='Experto' else random.uniform(4.5,7.0)
            express = (i == 2)
            caja = Caja(i+1, t_escaneo, express)
            caja.cajero = rol
            self.cajas.append(caja)

    def generar_personas_para_todas(self):
        """
        Genera personas para todas las cajas y agrega al cliente objetivo al final de cada fila
        """
        articulos_objetivo = random.randint(3,8)
        tiempo_cobro_objetivo = random.randint(15,30)

        for caja in self.cajas:
            caja.generar_personas()
            cliente_obj = Persona(articulos_objetivo, es_objetivo=True)
            cliente_obj.tiempo_cobro = tiempo_cobro_objetivo
            caja.personas.append(cliente_obj)

        self.cliente_objetivo = self.cajas[0].personas[-1]

    def ejecutar_simulacion(self):
        """
        Ejecuta la simulación usando hilos para atender todas las cajas en paralelo
        """
        self.tiempo_total_caja = []
        self.caja_ganadora_objetivo = None
        hilos = []
        resultados = [None]*len(self.cajas)

        def atender_caja(caja, idx):
            resultados[idx] = caja.atender(self)

        for i, caja in enumerate(self.cajas):
            hilo = threading.Thread(target=atender_caja, args=(caja,i))
            hilos.append(hilo)
            hilo.start()

        for hilo in hilos:
            hilo.join()

        self.tiempo_total_caja = resultados
        self.calcular_mejor_caja()
        self.objetivo_atendido = True
        return resultados

    def calcular_mejor_caja(self):
        """
        Calcula la caja con menor tiempo total
        """
        if self.tiempo_total_caja:
            mejor_idx = self.tiempo_total_caja.index(min(self.tiempo_total_caja))
            self.mejor_caja = mejor_idx+1
        return self.mejor_caja
