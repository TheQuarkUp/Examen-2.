import heapq
import json
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Style
import threading

class Tarea:
    def __init__(self, nombre, prioridad, dependencias=None, vencimiento=None):
        self.nombre = nombre
        self.prioridad = prioridad
        self.dependencias = dependencias if dependencias else []
        self.vencimiento = datetime.strptime(vencimiento, '%Y-%m-%d') if vencimiento else None
        self.completada = False

    def es_ejecutable(self, tareas):
        return all(tareas.get(dep, Tarea("", 0)).completada for dep in self.dependencias)

    def __lt__(self, other):
        if self.prioridad == other.prioridad:
            if self.vencimiento and other.vencimiento:
                return self.vencimiento < other.vencimiento
            return self.vencimiento is not None  # Prioriza tareas con vencimiento sobre las que no lo tienen
        return self.prioridad < other.prioridad

    def __repr__(self):
        return f"Tarea({self.nombre}, prioridad={self.prioridad}, vencimiento={self.vencimiento}, completada={self.completada})"

class SistemaDeTareas:
    def __init__(self):
        self.tareas = {}
        self.cola_prioridad = []

    def agregar_tarea(self, nombre, prioridad, dependencias=None, vencimiento=None):
        if nombre in self.tareas:
            raise ValueError("Ya existe una tarea con ese nombre.")
        nueva_tarea = Tarea(nombre, prioridad, dependencias, vencimiento)
        self.tareas[nombre] = nueva_tarea
        heapq.heappush(self.cola_prioridad, nueva_tarea)

    def mostrar_tareas_ordenadas(self):
        tareas_ordenadas = sorted([t for t in self.cola_prioridad if not t.completada], key=lambda x: (x.prioridad, x.vencimiento or datetime.max))
        tabla = [[
            tarea.nombre,
            tarea.prioridad,
            ', '.join(tarea.dependencias) if tarea.dependencias else "Ninguna",
            tarea.vencimiento.strftime('%Y-%m-%d') if tarea.vencimiento else "Sin vencimiento",
            Fore.GREEN + "Sí" + Style.RESET_ALL if tarea.completada else Fore.RED + "No" + Style.RESET_ALL
        ] for tarea in tareas_ordenadas]
        return tabulate(tabla, headers=["Nombre", "Prioridad", "Dependencias", "Vencimiento", "Completada"], tablefmt="fancy_grid")

    def completar_tarea(self, nombre):
        if nombre not in self.tareas:
            raise ValueError("La tarea no existe.")
        tarea = self.tareas[nombre]
        if tarea.completada:
            raise ValueError("La tarea ya está completada.")
        tarea.completada = True
        ejecutables = [t.nombre for t in self.tareas.values() if not t.completada and t.es_ejecutable(self.tareas)]
        if ejecutables:
            print(Fore.YELLOW + "Tareas ahora ejecutables: " + ", ".join(ejecutables) + Style.RESET_ALL)

    def obtener_tarea_mayor_prioridad(self):
        while self.cola_prioridad:
            tarea = heapq.heappop(self.cola_prioridad)
            if not tarea.completada:
                heapq.heappush(self.cola_prioridad, tarea)
                return tarea
        return None

    def guardar_en_archivo(self, archivo):
        with open(archivo, 'w') as f:
            json.dump({nombre: {
                "prioridad": tarea.prioridad,
                "dependencias": tarea.dependencias,
                "vencimiento": tarea.vencimiento.strftime('%Y-%m-%d') if tarea.vencimiento else None,
                "completada": tarea.completada
            } for nombre, tarea in self.tareas.items()}, f, indent=4)

    def cargar_desde_archivo(self, archivo):
        try:
            with open(archivo, 'r') as f:
                data = json.load(f)
                for nombre, info in data.items():
                    self.agregar_tarea(nombre, info['prioridad'], info['dependencias'], info['vencimiento'])
                    self.tareas[nombre].completada = info['completada']
        except FileNotFoundError:
            print(Fore.RED + "Archivo no encontrado. Se inicia un sistema vacío." + Style.RESET_ALL)

    def realizar_copia_seguridad(self, archivo):
        def copia():
            import shutil
            shutil.copyfile(archivo, archivo + ".bak")
            print(Fore.GREEN + "Copia de seguridad creada." + Style.RESET_ALL)
        thread = threading.Thread(target=copia)
        thread.start()

    def agregar_tarea_desde_input(self):
        try:
            nombre = input("Introduce el nombre de la tarea: ")
            prioridad = int(input("Introduce la prioridad de la tarea (número entero, menor es más prioritario): "))
            dependencias = input("Introduce las dependencias separadas por comas (o deja vacío si no hay): ").split(',')
            dependencias = [dep.strip() for dep in dependencias if dep.strip()]
            vencimiento = input("Introduce la fecha de vencimiento (YYYY-MM-DD) o deja vacío: ")
            vencimiento = vencimiento if vencimiento.strip() else None
            self.agregar_tarea(nombre, prioridad, dependencias, vencimiento)
        except ValueError as e:
            print(Fore.RED + "Entrada inválida: " + str(e) + Style.RESET_ALL)

# Ejemplo de uso con tareas predeterminadas
sistema = SistemaDeTareas()
sistema.agregar_tarea("Tarea Predeterminada 1", 1, vencimiento="2024-12-20")
sistema.agregar_tarea("Tarea Predeterminada 2", 2, ["Tarea Predeterminada 1"], vencimiento="2024-12-21")
sistema.agregar_tarea("Tarea Predeterminada 3", 3, vencimiento="2024-12-22")

while True:
    print("\nOpciones:")
    print("1. Agregar una nueva tarea")
    print("2. Mostrar tareas ordenadas")
    print("3. Completar una tarea")
    print("4. Obtener la tarea de mayor prioridad")
    print("5. Guardar y salir")
    opcion = input("Elige una opción: ")

    if opcion == "1":
        sistema.agregar_tarea_desde_input()
    elif opcion == "2":
        print("\nTareas ordenadas:")
        print(sistema.mostrar_tareas_ordenadas())
    elif opcion == "3":
        nombre = input("Introduce el nombre de la tarea a completar: ")
        try:
            sistema.completar_tarea(nombre)
            print(f"Tarea '{nombre}' completada.")
        except ValueError as e:
            print(Fore.RED + str(e) + Style.RESET_ALL)
    elif opcion == "4":
        tarea = sistema.obtener_tarea_mayor_prioridad()
        print("Tarea de mayor prioridad:", tarea)
    elif opcion == "5":
        sistema.guardar_en_archivo("tareas.json")
        sistema.realizar_copia_seguridad("tareas.json")
        print("Tareas guardadas. Saliendo...")
        break
    else:
        print(Fore.RED + "Opción no válida. Inténtalo de nuevo." + Style.RESET_ALL)

# Cambios realizados:
# 1. Validación robusta de entradas al agregar tareas, con manejo de excepciones y mensajes claros.
# 2. Feedback mejorado al completar tareas: se muestran las tareas que se vuelven ejecutables.
# 3. Mejora visual en la tabla de tareas, añadiendo colores para tareas completadas y pendientes.
# 4. Implementación de copias de seguridad automáticas al guardar, usando hilos para evitar bloqueos.
# 5. Mensajes más informativos en caso de errores, como archivo no encontrado o entradas inválidas.
