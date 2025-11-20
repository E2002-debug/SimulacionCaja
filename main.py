"""
MAIN UNIFICADO:
- Simulación con Tkinter
- Taller 4 (openbox)

Permite elegir qué ejecutar.
"""

import tkinter as tk
from interfaz import InterfazSimulador
import openbox   # Importa el script del Taller 4


def iniciar_simulacion():
    """Inicia la interfaz gráfica original"""
    root = tk.Tk()
    app = InterfazSimulador(root)
    root.mainloop()


def ejecutar_taller4():
    """Ejecuta la simulación estadística del Taller 4"""
    print("\n=== EJECUTANDO TALLER 4 (OpenBox) ===\n")
    openbox.ejecutar_openbox()
    print("\n=== TALLER 4 COMPLETADO ===\n")


def mostrar_menu():
    """Menú simple en consola"""
    print("\n===============================")
    print("   SELECCIONA LA OPCIÓN")
    print("===============================")
    print("1. Ejecutar simulación gráfica (Tkinter)")
    print("2. Ejecutar análisis Taller 4 (OpenBox)")
    print("3. Ejecutar ambos (primero Taller 4, luego Tkinter)")
    print("0. Salir")
    
    opcion = input("\nIngresa una opción: ")

    if opcion == "1":
        iniciar_simulacion()

    elif opcion == "2":
        ejecutar_taller4()

    elif opcion == "3":
        ejecutar_taller4()
        iniciar_simulacion()

    elif opcion == "0":
        print("Saliendo...")
    else:
        print("Opción inválida.")
        mostrar_menu()


def main():
    """Función principal"""
    mostrar_menu()


if __name__ == "__main__":
    main()
