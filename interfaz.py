import tkinter as tk
import threading
import time
from clases import SimuladorSupermercado
from generador_ensayos import EnsayoSimulador


class InterfazSimulador:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Cajas de Supermercado")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')
        
        # Asegurar que la ventana aparezca al frente
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        
        self.simulador = SimuladorSupermercado(num_cajas=3)
        self.canvas_width = 950
        self.canvas_height = 650  # Aumentado para filas verticales largas
        self.caja_width = 280
        self.caja_height = 250  # Cajas más pequeñas
        self.persona_radius = 8
        self.colores_caja = ['#2196F3', '#2196F3', '#9C27B0']  # Azul, Azul, Morado
        
        # Multiplicador de tiempo para acelerar la animación visual
        self.acelerador_tiempo = 15  # La simulación va 15x más rápida visualmente
        
        # Frame superior para controles
        self.frame_controles = tk.Frame(root, bg='#f0f0f0')
        self.frame_controles.pack(pady=10)
        
        self.btn_iniciar = tk.Button(
            self.frame_controles,
            text="Iniciar Simulación",
            command=self.iniciar_simulacion,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=10)
        
        self.btn_reiniciar = tk.Button(
            self.frame_controles,
            text="Reiniciar",
            command=self.reiniciar,
            bg='#f44336',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.btn_reiniciar.pack(side=tk.LEFT, padx=10)
        
        self.btn_ensayos = tk.Button(
            self.frame_controles,
            text="Generar 2000 Ensayos",
            command=self.generar_ensayos,
            bg='#9C27B0',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.btn_ensayos.pack(side=tk.LEFT, padx=10)
        
        # Control de velocidad
        tk.Label(
            self.frame_controles,
            text="Velocidad:",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.velocidad_var = tk.StringVar(value="15")
        self.combo_velocidad = tk.Spinbox(
            self.frame_controles,
            from_=1,
            to=50,
            textvariable=self.velocidad_var,
            width=5,
            font=('Arial', 10),
            command=self.actualizar_velocidad
        )
        self.combo_velocidad.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            self.frame_controles,
            text="x más rápido",
            font=('Arial', 10),
            bg='#f0f0f0'
        ).pack(side=tk.LEFT, padx=5)
        
        # Canvas para dibujar
        self.canvas = tk.Canvas(
            root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='white',
            highlightthickness=2,
            highlightbackground='#ccc'
        )
        self.canvas.pack(pady=10)
        
        # Frame inferior para información
        self.frame_info = tk.Frame(root, bg='#f0f0f0')
        self.frame_info.pack(pady=10)
        
        self.label_info = tk.Label(
            self.frame_info,
            text="🟡 Esperando | 🔴 Atendiendo | 🟢 Cliente Objetivo (está en las 3 filas simultáneamente)",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#333'
        )
        self.label_info.pack()
        
        # Label para mostrar tiempo transcurrido
        self.label_tiempo = tk.Label(
            self.frame_info,
            text="",  # Vacío inicialmente, se muestra solo al finalizar
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            fg='#FF5722'
        )
        self.label_tiempo.pack(pady=5)
        
        self.simulacion_en_curso = False
        self.tiempo_inicio = None
        self.actualizar_velocidad()  # Aplicar velocidad inicial
        self.dibujar_cajas_iniciales()
    
    def actualizar_velocidad(self):
        """Actualiza el acelerador de tiempo según el valor del spinbox"""
        try:
            self.acelerador_tiempo = int(self.velocidad_var.get())
            if self.acelerador_tiempo < 1:
                self.acelerador_tiempo = 1
                self.velocidad_var.set("1")
        except ValueError:
            self.acelerador_tiempo = 15
            self.velocidad_var.set("15")
    
    def dibujar_cajas_iniciales(self):
        """Dibuja las cajas vacías al inicio"""
        self.canvas.delete("all")
        
        spacing = 20
        start_x = (self.canvas_width - (3 * self.caja_width + 2 * spacing)) // 2
        
        cajeros = ['EXPERTO', 'PRINCIPIANTE', 'EXPERTO']
        tipos = ['NORMAL', 'NORMAL', 'EXPRESS']
        limites = ['(≤50 art.)', '(≤50 art.)', '(≤10 art.)']
        velocidades = ['3-5s/art.', '6-9s/art.', '3-5s/art.']
        
        for i in range(3):
            x = start_x + i * (self.caja_width + spacing)
            y = 50
            
            # Dibujar caja
            self.canvas.create_rectangle(
                x, y, x + self.caja_width, y + self.caja_height,
                fill=self.colores_caja[i],
                outline='#333',
                width=3,
                tags=f'caja_{i}'
            )
            
            # Título de la caja
            self.canvas.create_text(
                x + self.caja_width // 2,
                y + 12,
                text=f"CAJA {i + 1} - {tipos[i]}",
                font=('Arial', 12, 'bold'),
                fill='white',
                tags=f'titulo_caja_{i}'
            )
            
            # Tipo de cajero
            self.canvas.create_text(
                x + self.caja_width // 2,
                y + 28,
                text=f"Cajero {cajeros[i]}",
                font=('Arial', 10, 'bold'),
                fill='white',
                tags=f'cajero_{i}'
            )
            
            # Velocidad
            self.canvas.create_text(
                x + self.caja_width // 2,
                y + 43,
                text=f"⚡ {velocidades[i]}",
                font=('Arial', 9),
                fill='white',
                tags=f'velocidad_{i}'
            )
            
            # Límite de artículos
            self.canvas.create_text(
                x + self.caja_width // 2,
                y + 57,
                text=limites[i],
                font=('Arial', 8),
                fill='white',
                tags=f'limite_{i}'
            )
    
    def dibujar_estado(self):
        """Dibuja el estado actual de las cajas y personas"""
        self.dibujar_cajas_iniciales()
        
        spacing = 20
        start_x = (self.canvas_width - (3 * self.caja_width + 2 * spacing)) // 2
        
        for i, caja in enumerate(self.simulador.cajas):
            x = start_x + i * (self.caja_width + spacing)
            y = 50
            
            # Los títulos ya están dibujados en dibujar_cajas_iniciales()
            
            # Dibujar personas en la fila
            personas_restantes = len(caja.personas)
            self.canvas.create_text(
                x + self.caja_width // 2,
                y + 80,
                text=f"👥 En fila: {personas_restantes}",
                font=('Arial', 10, 'bold'),
                fill='white'
            )
            
            # Dibujar círculos para cada persona FUERA de la caja, en fila VERTICAL
            persona_spacing = 20  # Espaciado vertical entre personas
            caja_bottom = y + self.caja_height  # Parte inferior de la caja
            fila_x = x + self.caja_width // 2  # Centrado horizontalmente en la caja
            start_fila_y = caja_bottom + 30  # Posición Y inicial de la fila (debajo de la caja)
            
            for idx, persona in enumerate(caja.personas):
                px = fila_x
                py = start_fila_y + idx * persona_spacing
                
                # Color según el tipo de persona
                if persona.es_objetivo:
                    # Cliente OBJETIVO en VERDE (está en las 3 filas simultáneamente)
                    color_persona = '#00FF00'  # Verde brillante
                    outline_color = '#00AA00'
                    outline_width = 3
                elif idx == 0 and caja.atendiendo:
                    # Primera persona siendo atendida en ROJO
                    color_persona = '#FF6B6B'
                    outline_color = '#C92A2A'
                    outline_width = 3
                else:
                    # Personas esperando en AMARILLO
                    color_persona = '#FFD700'
                    outline_color = '#333'
                    outline_width = 2
                
                # Círculo para la persona (partícula)
                self.canvas.create_oval(
                    px - self.persona_radius,
                    py - self.persona_radius,
                    px + self.persona_radius,
                    py + self.persona_radius,
                    fill=color_persona,
                    outline=outline_color,
                    width=outline_width
                )
                
                # Número de artículos dentro del círculo
                self.canvas.create_text(
                    px,
                    py,
                    text=str(persona.articulos),
                    font=('Arial', 8, 'bold'),
                    fill='#333' if not persona.es_objetivo else '#000'
                )
    
    def actualizar_visualizacion(self):
        """Actualiza la visualización durante la simulación"""
        if not self.simulacion_en_curso:
            return
        
        self.dibujar_estado()
        
        # Actualizar información con detalles de tiempos
        info_texto = "⏱️ Simulación en curso... | "
        for i, caja in enumerate(self.simulador.cajas):
            personas_restantes = len(caja.personas)
            estado = "⚡ Atendiendo" if caja.atendiendo else "⏸️ Esperando"
            info_texto += f"Caja {i+1} ({caja.t_escaneo:.1f}s/art): {personas_restantes}p {estado} | "
        
        self.label_info.config(text=info_texto)
        
        # NO mostrar tiempo durante la simulación, solo al finalizar
        
        # Verificar si el cliente objetivo fue atendido (finaliza la simulación)
        if self.simulador.objetivo_atendido:
            self.finalizar_simulacion()
        else:
            self.root.after(500, self.actualizar_visualizacion)
    
    def iniciar_simulacion(self):
        """Inicia la simulación"""
        if self.simulacion_en_curso:
            return
        
        self.simulacion_en_curso = True
        self.btn_iniciar.config(state='disabled')
        
        # Actualizar velocidad antes de iniciar
        self.actualizar_velocidad()
        
        # Iniciar contador de tiempo
        self.tiempo_inicio = time.time()
        
        # Pasar el acelerador de tiempo al simulador
        self.simulador.acelerador_tiempo = self.acelerador_tiempo
        
        # Generar personas
        self.simulador.iniciar_cajas()
        self.simulador.generar_personas_para_todas()
        self.dibujar_estado()
        
        # Iniciar simulación en un hilo separado
        def ejecutar():
            self.simulador.ejecutar_simulacion()
        
        threading.Thread(target=ejecutar, daemon=True).start()
        
        # Actualizar visualización
        self.root.after(500, self.actualizar_visualizacion)
    
    def finalizar_simulacion(self):
        """Finaliza la simulación y muestra resultados"""
        self.simulacion_en_curso = False
        self.btn_iniciar.config(state='normal')
        
        # Calcular tiempo REAL (multiplicando el tiempo de animación por el acelerador)
        tiempo_animacion = time.time() - self.tiempo_inicio if self.tiempo_inicio else 0
        tiempo_real = tiempo_animacion * self.acelerador_tiempo
        
        caja_objetivo = self.simulador.caja_ganadora_objetivo
        articulos_objetivo = self.simulador.cliente_objetivo.articulos if self.simulador.cliente_objetivo else 0
        
        resultado_texto = f"✓ ¡Cliente Objetivo atendido! Simulación finalizada.\n"
        resultado_texto += f"🟢 Cliente Objetivo ({articulos_objetivo} artículos) atendido PRIMERO en: 🏆 CAJA {caja_objetivo} 🏆\n"
        resultado_texto += f"Las otras cajas se detuvieron automáticamente."
        
        self.label_info.config(text=resultado_texto, fg='#4CAF50')
        self.label_tiempo.config(text=f"⏱️ Tiempo en ser atendido: {tiempo_real:.1f}s (tiempo real calculado)", fg='#4CAF50')
        
        # Marcar la caja que atendió primero al cliente objetivo
        self.dibujar_estado()
        spacing = 20
        start_x = (self.canvas_width - (3 * self.caja_width + 2 * spacing)) // 2
        
        if caja_objetivo:
            idx_objetivo = caja_objetivo - 1
            x_objetivo = start_x + idx_objetivo * (self.caja_width + spacing)
            y = 50
            
            self.canvas.create_text(
                x_objetivo + self.caja_width // 2,
                y + self.caja_height - 40,
                text="🏆 GANADORA 🏆\nAtendió primero\nal cliente objetivo",
                font=('Arial', 13, 'bold'),
                fill='#00FF00'
            )
    
    def reiniciar(self):
        """Reinicia la simulación"""
        self.simulacion_en_curso = False
        self.tiempo_inicio = None
        self.btn_iniciar.config(state='normal')
        self.simulador = SimuladorSupermercado(num_cajas=3)
        self.dibujar_cajas_iniciales()
        self.label_info.config(
            text="🟡 Esperando | 🔴 Atendiendo | 🟢 Cliente Objetivo (está en las 3 filas simultáneamente)",
            fg='#333'
        )
        self.label_tiempo.config(text="", fg='#FF5722')  # Vacío hasta que termine
    
    def generar_ensayos(self):
        """Genera 2000 ensayos y exporta a Excel"""
        self.btn_ensayos.config(state='disabled', text="Generando...")
        self.label_info.config(text="⏳ Generando 2000 ensayos instantáneos...", fg='#FF9800')
        
        def ejecutar_ensayos():
            simulador_ensayos = EnsayoSimulador()
            simulador_ensayos.generar_ensayos(2000)
            archivo = simulador_ensayos.exportar_excel()
            
            # Mostrar estadísticas
            total = len(simulador_ensayos.resultados)
            ganadores_express = sum(1 for r in simulador_ensayos.resultados if r['tipo_ganador'] == 'Express')
            ganadores_normal = total - ganadores_express
            
            mensaje = f"✓ 2000 ensayos completados!\n"
            mensaje += f"Cajas Normales ganaron: {ganadores_normal} ({ganadores_normal/20:.1f}%)\n"
            mensaje += f"Caja Express ganó: {ganadores_express} ({ganadores_express/20:.1f}%)\n"
            mensaje += f"Archivo Excel: {archivo}"
            
            self.label_info.config(text=mensaje, fg='#4CAF50')
            self.btn_ensayos.config(state='normal', text="Generar 2000 Ensayos Excel")
        
        # Ejecutar en un hilo separado para no bloquear la interfaz
        threading.Thread(target=ejecutar_ensayos, daemon=True).start()
