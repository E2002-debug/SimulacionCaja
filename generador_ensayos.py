"""
Generador de Ensayos para Simulación de Cajas
Genera múltiples ensayos sin transcurrir tiempo real, solo cálculos matemáticos
"""
import random
from datetime import datetime

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    TIENE_OPENPYXL = True
except ImportError:
    TIENE_OPENPYXL = False
    print("⚠️ Advertencia: openpyxl no está instalado. Instalando...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    TIENE_OPENPYXL = True


class EnsayoSimulador:
    """Simulador que calcula tiempos sin esperar (sin time.sleep)"""
    
    def __init__(self):
        self.resultados = []
    
    def generar_cliente_cuantico(self):
        """Genera un cliente cuántico con artículos aleatorios"""
        articulos = random.randint(3, 8)
        tiempo_cobro = random.randint(15, 30)
        return articulos, tiempo_cobro
    
    def generar_personas_caja(self, es_express):
        """Genera personas para una caja según su tipo"""
        if es_express:
            cantidad = random.randint(10, 16)
            personas = []
            for _ in range(cantidad):
                if random.random() < 0.8:
                    articulos = random.randint(1, 5)
                else:
                    articulos = random.randint(6, 10)
                tiempo_cobro = random.randint(15, 30)
                personas.append((articulos, tiempo_cobro))
        else:
            cantidad = random.randint(3, 7)
            personas = []
            for _ in range(cantidad):
                rand = random.random()
                if rand < 0.5:
                    articulos = random.randint(1, 15)
                elif rand < 0.8:
                    articulos = random.randint(16, 30)
                else:
                    articulos = random.randint(31, 50)
                tiempo_cobro = random.randint(15, 30)
                personas.append((articulos, tiempo_cobro))
        
        return personas
    
    def calcular_tiempo_hasta_cuantico(self, personas, cliente_cuantico, tiempo_escaneo):
        """Calcula el tiempo total hasta atender al cliente cuántico"""
        articulos_cuantico, tiempo_cobro_cuantico = cliente_cuantico
        
        # Agregar el cliente cuántico al final
        todas_personas = personas + [(articulos_cuantico, tiempo_cobro_cuantico)]
        
        tiempo_total = 0
        for articulos, tiempo_cobro in todas_personas:
            tiempo_persona = articulos * tiempo_escaneo + tiempo_cobro
            tiempo_total += tiempo_persona
        
        return tiempo_total
    
    def ejecutar_ensayo_simple(self, numero_ensayo):
        """Ejecuta un ensayo completo y retorna el resultado"""
        
        # Generar cliente cuántico (mismo para las 3 cajas)
        cliente_cuantico = self.generar_cliente_cuantico()
        articulos_cuantico, tiempo_cobro_cuantico = cliente_cuantico
        
        # Configuración de cajas
        cajas = [
            {
                'id': 1,
                'tipo': 'Normal',
                'cajero': 'Experto',
                'tiempo_escaneo': random.uniform(2.5, 4.0),  # Experto: 2.5-4s (incluye empaquetado)
                'express': False
            },
            {
                'id': 2,
                'tipo': 'Normal',
                'cajero': 'Principiante',
                'tiempo_escaneo': random.uniform(4.5, 7.0),  # Principiante: 4.5-7s (incluye empaquetado)
                'express': False
            },
            {
                'id': 3,
                'tipo': 'Express',
                'cajero': 'Experto',
                'tiempo_escaneo': random.uniform(2.5, 4.0),  # Experto: 2.5-4s (incluye empaquetado)
                'express': True
            }
        ]
        
        # Calcular tiempo para cada caja
        tiempos = []
        for caja in cajas:
            personas = self.generar_personas_caja(caja['express'])
            tiempo = self.calcular_tiempo_hasta_cuantico(
                personas, 
                cliente_cuantico, 
                caja['tiempo_escaneo']
            )
            tiempos.append({
                'caja_id': caja['id'],
                'tipo_caja': caja['tipo'],
                'cajero': caja['cajero'],
                'tiempo_escaneo': round(caja['tiempo_escaneo'], 2),
                'num_personas': len(personas),
                'tiempo_total': round(tiempo, 2)
            })
        
        # Encontrar la caja ganadora (menor tiempo)
        tiempos_ordenados = sorted(tiempos, key=lambda x: x['tiempo_total'])
        ganadora = tiempos_ordenados[0]
        
        # Clasificar ganador simplificado
        if ganadora['tipo_caja'] == 'Express':
            tipo_ganador = 'Express'
        else:
            tipo_ganador = 'Normal'
        
        return {
            'ensayo': numero_ensayo,
            'articulos_cuantico': articulos_cuantico,
            'caja_ganadora_id': ganadora['caja_id'],
            'tipo_ganador': tipo_ganador,
            'tiempo_ganador': ganadora['tiempo_total'],
            'caja1_tiempo': tiempos[0]['tiempo_total'],
            'caja1_personas': tiempos[0]['num_personas'],
            'caja2_tiempo': tiempos[1]['tiempo_total'],
            'caja2_personas': tiempos[1]['num_personas'],
            'caja3_tiempo': tiempos[2]['tiempo_total'],
            'caja3_personas': tiempos[2]['num_personas']
        }
    
    def generar_ensayos(self, cantidad=1000):
        """Genera múltiples ensayos y guarda en CSV"""
        print(f"Generando {cantidad} ensayos instantáneos...")
        
        resultados = []
        for i in range(1, cantidad + 1):
            resultado = self.ejecutar_ensayo_simple(i)
            resultados.append(resultado)
            
            if i % 100 == 0:
                print(f"  Progreso: {i}/{cantidad} ensayos completados")
        
        self.resultados = resultados
        return resultados
    
    def exportar_excel(self, nombre_archivo=None):
        """Exporta los resultados a un archivo Excel (.xlsx)"""
        if not self.resultados:
            print("No hay resultados para exportar")
            return
        
        if nombre_archivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"ensayos_cajas_{timestamp}.xlsx"
        
        # Asegurar extensión .xlsx
        if not nombre_archivo.endswith('.xlsx'):
            nombre_archivo += '.xlsx'
        
        # Crear libro de Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Ensayos"
        
        # Definir encabezados
        encabezados = [
            'Ensayo',
            'Articulos_Cuantico',
            'Caja_Ganadora_ID',
            'Tipo_Ganador',
            'Tiempo_Ganador',
            'Caja1_Tiempo',
            'Caja1_Personas',
            'Caja2_Tiempo',
            'Caja2_Personas',
            'Caja3_Tiempo',
            'Caja3_Personas'
        ]
        
        # Estilo para encabezados
        header_fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        center_alignment = Alignment(horizontal="center", vertical="center")
        
        # Escribir encabezados
        for col_idx, encabezado in enumerate(encabezados, start=1):
            cell = ws.cell(row=1, column=col_idx, value=encabezado)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_alignment
        
        # Escribir datos
        for row_idx, resultado in enumerate(self.resultados, start=2):
            ws.cell(row=row_idx, column=1, value=resultado['ensayo'])
            ws.cell(row=row_idx, column=2, value=resultado['articulos_cuantico'])
            ws.cell(row=row_idx, column=3, value=resultado['caja_ganadora_id'])
            ws.cell(row=row_idx, column=4, value=resultado['tipo_ganador'])
            ws.cell(row=row_idx, column=5, value=round(resultado['tiempo_ganador'], 3))
            ws.cell(row=row_idx, column=6, value=round(resultado['caja1_tiempo'], 3))
            ws.cell(row=row_idx, column=7, value=resultado['caja1_personas'])
            ws.cell(row=row_idx, column=8, value=round(resultado['caja2_tiempo'], 3))
            ws.cell(row=row_idx, column=9, value=resultado['caja2_personas'])
            ws.cell(row=row_idx, column=10, value=round(resultado['caja3_tiempo'], 3))
            ws.cell(row=row_idx, column=11, value=resultado['caja3_personas'])
            
            # Resaltar la caja ganadora
            ganadora_col = 3 + (resultado['caja_ganadora_id'] - 1) * 2 + 3  # Columna de tiempo ganadora
            cell_ganadora = ws.cell(row=row_idx, column=ganadora_col)
            cell_ganadora.fill = PatternFill(start_color="FFEB3B", end_color="FFEB3B", fill_type="solid")
        
        # Ajustar ancho de columnas
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width
        
        # Guardar archivo
        wb.save(nombre_archivo)
        
        print(f"\n✓ Archivo Excel exportado: {nombre_archivo}")
        return nombre_archivo
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas de los ensayos"""
        if not self.resultados:
            print("No hay resultados para analizar")
            return
        
        total = len(self.resultados)
        
        # Contar ganadores por tipo
        ganadores_express = sum(1 for r in self.resultados if r['tipo_ganador'] == 'Express')
        ganadores_normal = sum(1 for r in self.resultados if r['tipo_ganador'] == 'Normal')
        
        # Contar por caja específica
        ganadores_caja1 = sum(1 for r in self.resultados if r['caja_ganadora_id'] == 1)
        ganadores_caja2 = sum(1 for r in self.resultados if r['caja_ganadora_id'] == 2)
        ganadores_caja3 = sum(1 for r in self.resultados if r['caja_ganadora_id'] == 3)
        
        print("\n" + "="*60)
        print("ESTADÍSTICAS DE LOS ENSAYOS")
        print("="*60)
        print(f"Total de ensayos: {total}")
        print("\nGanadores por TIPO de caja:")
        print(f"  Cajas Normales:  {ganadores_normal} ({ganadores_normal/total*100:.1f}%)")
        print(f"  Caja Express:    {ganadores_express} ({ganadores_express/total*100:.1f}%)")
        print("\nGanadores por caja específica:")
        print(f"  Caja 1 (Normal-Experto):        {ganadores_caja1} ({ganadores_caja1/total*100:.1f}%)")
        print(f"  Caja 2 (Normal-Principiante):   {ganadores_caja2} ({ganadores_caja2/total*100:.1f}%)")
        print(f"  Caja 3 (Express-Experto):       {ganadores_caja3} ({ganadores_caja3/total*100:.1f}%)")
        print("="*60)


def main():
    """Función principal para ejecutar los ensayos"""
    print("="*60)
    print("GENERADOR DE ENSAYOS - SIMULACIÓN DE CAJAS")
    print("="*60)
    
    simulador = EnsayoSimulador()
    
    # Generar 1000 ensayos
    simulador.generar_ensayos(1000)
    
    # Mostrar estadísticas
    simulador.mostrar_estadisticas()
    
    # Exportar a Excel
    archivo = simulador.exportar_excel()
    
    print(f"\n✓ Proceso completado exitosamente!")
    print(f"  Archivo Excel generado: {archivo}")


if __name__ == "__main__":
    main()
