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
        
        # Asegura que la ventana aparezca al frente
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        
        # Inicializa el simulador con 3 cajas
        self.simulador = SimuladorSupermercado(num_cajas=3)
        
        # Dimensiones y visualización
        self.canvas_width = 950
        self.canvas_height = 650
        self.caja_width = 280
        self.caja_height = 250
        self.persona_radius = 8
        self.colores_caja = ['#2196F3', '#2196F3', '#9C27B0']  # Azul, Azul, Morado
        
        # Multiplicador de tiempo para acelerar animación
        self.acelerador_tiempo = 15
        
        # Frame superior con controles
        self.frame_controles = tk.Frame(root, bg='#f0f0f0')
        self.frame_controles.pack(pady=10)
        
        # Botón iniciar simulación
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
        
        # Botón reiniciar
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
        
        # Botón generar ensayos
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
        ).pack(side=tk.LEFT, padx=(20,5))
        
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
        
        # Canvas principal para dibujar cajas y personas
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
        
        # Label informativo de estado de personas
        self.label_info = tk.Label(
            self.frame_info,
            text="🟡 Esperando | 🔴 Atendiendo | 🟢 Cliente Objetivo (está en las 3 filas simultáneamente)",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#333'
        )
        self.label_info.pack()
        
        # Label de tiempo transcurrido / resultado final
        self.label_tiempo = tk.Label(
            self.frame_info,
            text="",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            fg='#FF5722'
        )
        self.label_tiempo.pack(pady=5)
        
        # Variables de control
        self.simulacion_en_curso = False
        self.tiempo_inicio = None
        self.actualizar_velocidad()
        self.dibujar_cajas_iniciales()
    
    # --------------------------- Funciones de velocidad ---------------------------
    def actualizar_velocidad(self):
        """Actualiza el acelerador de tiempo según Spinbox"""
        try:
            self.acelerador_tiempo = int(self.velocidad_var.get())
            if self.acelerador_tiempo < 1:
                self.acelerador_tiempo = 1
                self.velocidad_var.set("1")
        except ValueError:
            self.acelerador_tiempo = 15
            self.velocidad_var.set("15")
    
    # --------------------------- Dibujado inicial ---------------------------
    def dibujar_cajas_iniciales(self):
        """Dibuja las cajas vacías al inicio con títulos y colores"""
        self.canvas.delete("all")
        
        spacing = 20
        start_x = (self.canvas_width - (3*self.caja_width + 2*spacing)) // 2
        
        for i, caja in enumerate(self.simulador.cajas):
            x = start_x + i*(self.caja_width + spacing)
            y = 50
            
            tipo_caja = "EXPRESS" if caja.express else "NORMAL"
            cajero = caja.cajero.upper()
            limite = "(≤10 art.)" if caja.express else "(≤50 art.)"
            velocidad = "⚡ 3-5s/art." if caja.cajero=="Experto" else "⚡ 6-9s/art."
            
            # Rectángulo caja
            self.canvas.create_rectangle(
                x, y, x+self.caja_width, y+self.caja_height,
                fill=self.colores_caja[i],
                outline='#333',
                width=3,
                tags=f'caja_{i}'
            )
            
            # Textos de caja
            self.canvas.create_text(x+self.caja_width//2, y+12,
                                    text=f"CAJA {i+1} - {tipo_caja}",
                                    font=('Arial', 12, 'bold'),
                                    fill='white')
            self.canvas.create_text(x+self.caja_width//2, y+28,
                                    text=f"Cajero {cajero}",
                                    font=('Arial', 10, 'bold'),
                                    fill='white')
            self.canvas.create_text(x+self.caja_width//2, y+43,
                                    text=velocidad,
                                    font=('Arial', 9),
                                    fill='white')
            self.canvas.create_text(x+self.caja_width//2, y+57,
                                    text=limite,
                                    font=('Arial', 8),
                                    fill='white')
    
    # --------------------------- Dibujado de estado ---------------------------
    def dibujar_estado(self):
        """Dibuja el estado actual de las cajas y personas"""
        self.dibujar_cajas_iniciales()
        
        spacing = 20
        start_x = (self.canvas_width - (3*self.caja_width + 2*spacing)) // 2
        
        for i, caja in enumerate(self.simulador.cajas):
            x = start_x + i*(self.caja_width + spacing)
            y = 50
            
            # Número de personas en fila
            personas_restantes = len(caja.personas)
            self.canvas.create_text(x+self.caja_width//2,
                                    y+80,
                                    text=f"👥 En fila: {personas_restantes}",
                                    font=('Arial', 10, 'bold'),
                                    fill='white')
            
            # Dibujar personas en fila vertical debajo de la caja
            persona_spacing = 20
            caja_bottom = y+self.caja_height
            fila_x = x+self.caja_width//2
            start_fila_y = caja_bottom+30
            
            for idx, persona in enumerate(caja.personas):
                px = fila_x
                py = start_fila_y + idx*persona_spacing
                
                # Color según estado
                if persona.es_objetivo:
                    color_persona = '#00FF00'  # Verde brillante
                    outline_color = '#00AA00'
                    outline_width = 3
                elif idx==0 and caja.atendiendo:
                    color_persona = '#FF6B6B'  # Rojo
                    outline_color = '#C92A2A'
                    outline_width = 3
                else:
                    color_persona = '#FFD700'  # Amarillo
                    outline_color = '#333'
                    outline_width = 2
                
                # Dibujar círculo
                self.canvas.create_oval(
                    px-self.persona_radius,
                    py-self.persona_radius,
                    px+self.persona_radius,
                    py+self.persona_radius,
                    fill=color_persona,
                    outline=outline_color,
                    width=outline_width
                )
                
                # Número de artículos
                self.canvas.create_text(
                    px, py,
                    text=str(persona.articulos),
                    font=('Arial', 8, 'bold'),
                    fill='#333' if not persona.es_objetivo else '#000'
                )
    
    # --------------------------- Actualización visual ---------------------------
    def actualizar_visualizacion(self):
        """Actualiza la visualización durante la simulación"""
        if not self.simulacion_en_curso:
            return
        
        self.dibujar_estado()
        
        # Información de estado en label
        info_texto = "⏱️ Simulación en curso... | "
        for i, caja in enumerate(self.simulador.cajas):
            personas_restantes = len(caja.personas)
            estado = "⚡ Atendiendo" if caja.atendiendo else "⏸️ Esperando"
            info_texto += f"Caja {i+1} ({caja.t_escaneo:.1f}s/art): {personas_restantes}p {estado} | "
        
        self.label_info.config(text=info_texto)
        
        # Revisar si la simulación terminó (cliente objetivo atendido)
        if self.simulador.objetivo_atendido:
            self.finalizar_simulacion()
        else:
            self.root.after(500, self.actualizar_visualizacion)
    
    # --------------------------- Iniciar simulación ---------------------------
    def iniciar_simulacion(self):
        """Inicia la simulación"""
        if self.simulacion_en_curso:
            return
        
        self.simulacion_en_curso = True
        self.btn_iniciar.config(state='disabled')
        self.actualizar_velocidad()
        
        # Guardar tiempo de inicio
        self.tiempo_inicio = time.time()
        self.simulador.acelerador_tiempo = self.acelerador_tiempo
        
        # Inicializar cajas y generar personas
        self.simulador.iniciar_cajas()
        self.simulador.generar_personas_para_todas()
        self.dibujar_estado()
        
        # Ejecutar simulación en hilo separado
        def ejecutar():
            self.simulador.ejecutar_simulacion()
        
        threading.Thread(target=ejecutar, daemon=True).start()
        
        # Actualizar visualización en tiempo real
        self.root.after(500, self.actualizar_visualizacion)
        
    # --------------------------- Finalizar simulación ---------------------------
    def finalizar_simulacion(self):
        #Finaliza la simulación mostrando tiempos y resaltando ganadora#
        self.simulacion_en_curso = False
        self.btn_iniciar.config(state='normal')
        
        # Dibujar estado final
        self.dibujar_estado()
        
        # ---------------- Mostrar tiempos en un label ----------------
        resultado_texto = "Tiempos de atención por caja:\n"
        for caja in self.simulador.cajas:
            resultado_texto += f"Caja {caja.id_caja}: {caja.tiempo_total:.1f}s\n"
        
        # Primera caja que atendió al cliente objetivo
        if self.simulador.caja_ganadora_objetivo:
            resultado_texto += f"\nPrimera caja que atendió al cliente objetivo: Caja {self.simulador.caja_ganadora_objetivo}"
        
        # Mostrar en label_tiempo
        self.label_tiempo.config(text=resultado_texto, fg='#FF5722')
        
        # ---------------- Resaltar caja ganadora en canvas ----------------
        spacing = 20
        start_x = (self.canvas_width - (3*self.caja_width + 2*spacing)) // 2
        caja_objetivo = self.simulador.caja_ganadora_objetivo
        idx_objetivo = -1  # Default value if no winner
        
        if caja_objetivo:
            idx_objetivo = caja_objetivo - 1
            if 0 <= idx_objetivo < len(self.simulador.cajas):
                x_objetivo = start_x + idx_objetivo*(self.caja_width + spacing)
                y = 50
                # Usar la caja correcta para el tiempo
                caja_ganadora = self.simulador.cajas[idx_objetivo]
                self.canvas.create_text(
                    x_objetivo + self.caja_width//2,
                    y + self.caja_height - 40,
                    text=f"🏆 CAJA GANADORA 🏆",
                    font=('Arial', 13, 'bold'),
                    fill='#00FF00'
                )
        
        # ---------------- Dibujar tiempos sobre cada caja ----------------
        for i, caja in enumerate(self.simulador.cajas):
            x = start_x + i*(self.caja_width + spacing)
            y = 50
            color_texto = '#00FF00' if (i == idx_objetivo) else '#FF5722'
            self.canvas.create_text(
            x + self.caja_width//2,
                y + self.caja_height - 60,
                text=f"El tiempo de atención fue: {caja.tiempo_total:.1f}s",
                font=('Arial', 12, 'bold'),
                fill=color_texto
            )

    # --------------------------- Reiniciar ---------------------------
    def reiniciar(self):
        """Reinicia la simulación"""
        self.simulacion_en_curso = False
        self.tiempo_inicio = None
        self.btn_iniciar.config(state='normal')
        self.simulador = SimuladorSupermercado(num_cajas=3)
        self.dibujar_cajas_iniciales()
        self.label_info.config(
            text="● Esperando | ● Atendiendo | ● Cliente Objetivo (está en las 3 filas simultáneamente)",
            fg='#333'
        )
        self.label_tiempo.config(text="", fg='#FF5722')
    
    # --------------------------- Generar 2000 ensayos ---------------------------
    def generar_ensayos(self):
        """Genera 2000 ensayos y exporta a Excel"""
        self.btn_ensayos.config(state='disabled', text="Generando...")
        self.label_info.config(text="⏳ Generando 2000 ensayos instantáneos...", fg='#FF9800')
        
        def ejecutar_ensayos():
            simulador_ensayos = EnsayoSimulador()
            simulador_ensayos.generar_ensayos(2000)
            archivo = simulador_ensayos.exportar_excel()
            
            total = len(simulador_ensayos.resultados)
            ganadores_express = sum(1 for r in simulador_ensayos.resultados if r['tipo_ganador']=='Express')
            ganadores_normal = total - ganadores_express
            
            mensaje = f"✓ 2000 ensayos completados!\n"
            mensaje += f"Cajas Normales ganaron: {ganadores_normal} ({ganadores_normal/20:.1f}%)\n"
            mensaje += f"Caja Express ganó: {ganadores_express} ({ganadores_express/20:.1f}%)\n"
            mensaje += f"Archivo Excel: {archivo}"
            
            self.label_info.config(text=mensaje, fg='#4CAF50')
            self.btn_ensayos.config(state='normal', text="Generar 2000 Ensayos Excel")
        
        threading.Thread(target=ejecutar_ensayos, daemon=True).start()
