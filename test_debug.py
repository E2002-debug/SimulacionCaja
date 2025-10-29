"""Script de depuración para identificar el problema"""
import sys

print("=" * 50)
print("INICIO DEL SCRIPT")
print("=" * 50)

print("\n1. Importando tkinter...")
import tkinter as tk
print("   ✓ tkinter importado correctamente")

print("\n2. Importando interfaz...")
from interfaz import InterfazSimulador
print("   ✓ interfaz importada correctamente")

print("\n3. Creando ventana Tk...")
root = tk.Tk()
print("   ✓ Ventana Tk creada")

print("\n4. Creando InterfazSimulador...")
app = InterfazSimulador(root)
print("   ✓ InterfazSimulador creado")

print("\n5. Iniciando mainloop...")
print("   La ventana debería aparecer AHORA")
print("=" * 50)

root.mainloop()
