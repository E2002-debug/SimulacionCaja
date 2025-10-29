"""
Simulador de Cajas de Supermercado
Punto de entrada principal de la aplicación
"""
import tkinter as tk
from interfaz import InterfazSimulador


def main():
    """Función principal que inicia la aplicación"""
    root = tk.Tk()
    app = InterfazSimulador(root)
    root.mainloop()


if __name__ == "__main__":
    main()
