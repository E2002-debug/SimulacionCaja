import random
import time
import threading
import variables

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
        Genera aleatoriamente personas en la fila según la configuración del caso de prueba
        """
        config = self.config_personas
        self.cantidad_personas = random.randint(config['personas_min'], config['personas_max'])
        self.personas = []

        for _ in range(self.cantidad_personas):
            r = random.random()
            articulos = None
            for prob, min_art, max_art in config['articulos_distribucion']:
                if r <= prob:
                    articulos = random.randint(min_art, max_art)
                    break
            # Si no se asignó (por algún error), usar valores por defecto
            if articulos is None:
                articulos = random.randint(1, 10)
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
            acelerador = getattr(simulador, 'acelerador_tiempo', 50)
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
    def __init__(self, num_cajas=3, caso_prueba=1):
        """
        Simulador de todas las cajas.
        :param num_cajas: número de cajas (debe coincidir con la configuración del caso)
        :param caso_prueba: número del caso de prueba a usar
        """
        self.caso_prueba = caso_prueba
        self.config = variables.CASOS_PRUEBA[caso_prueba]
        self.num_cajas = len(self.config['cajas'])  # Usar el número de cajas del caso
        self.cajas = []
        self.acelerador_tiempo = 50
        self.tiempo_total_caja = []
        self.mejor_caja = None
        self.cliente_objetivo = None
        self.caja_ganadora_objetivo = None
        self.objetivo_atendido = False
        self.iniciar_cajas()

    def iniciar_cajas(self):
        """
        Inicializa las cajas según la configuración del caso de prueba
        """
        self.cajas = []
        for i, caja_config in enumerate(self.config['cajas']):
            # Asignar cajero aleatoriamente (Experto o Principiante)
            cajero_aleatorio = random.choice(['Experto', 'Principiante'])
            
            # Determinar tiempos de escaneo según el cajero asignado
            if cajero_aleatorio == 'Experto':
                t_escaneo = random.uniform(2.5, 4.0)
            else:  # Principiante
                t_escaneo = random.uniform(4.5, 7.0)
            
            caja = Caja(i+1, t_escaneo, caja_config['express'])
            caja.cajero = cajero_aleatorio
            caja.tipo = caja_config['tipo']
            caja.config_personas = caja_config  # Guardar config para generar_personas
            self.cajas.append(caja)

    def generar_personas_para_todas(self):
        """
        Genera personas para todas las cajas y agrega al cliente objetivo al final de cada fila
        """
        config_obj = self.config['cliente_objetivo']
        articulos_objetivo = random.randint(
            config_obj['articulos_min'], 
            config_obj['articulos_max']
        )
        tiempo_cobro_objetivo = random.randint(
            self.config['tiempo_cobro_min'], 
            self.config['tiempo_cobro_max']
        )

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
