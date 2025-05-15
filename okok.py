import sys
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# -----------------------------
# Módulo: Datos y Constantes
# -----------------------------
TEMP_AMBIENTE = 25.0
DIM_BEBIDA = (0.1, 0.1, 0.2)
DIM_COMIDA = (0.2, 0.2, 0.1)

PRODUCTOS = {
    1: {"nombre": "Café", "categoria": "bebida_caliente", "vol_std": 0.3, "temp_std": 85},
    2: {"nombre": "Té", "categoria": "bebida_caliente", "vol_std": 0.3, "temp_std": 80},
    3: {"nombre": "Chocolate caliente", "categoria": "bebida_caliente", "vol_std": 0.25, "temp_std": 75},
    4: {"nombre": "Matcha latte", "categoria": "bebida_caliente", "vol_std": 0.3, "temp_std": 75},
    5: {"nombre": "Chai", "categoria": "bebida_caliente", "vol_std": 0.3, "temp_std": 78},
    6: {"nombre": "Refresco", "categoria": "bebida_fria", "vol_std": 0.5, "temp_std": 4},
    7: {"nombre": "Jugo natural", "categoria": "bebida_fria", "vol_std": 0.4, "temp_std": 6},
    8: {"nombre": "Agua fría", "categoria": "bebida_fria", "vol_std": 0.5, "temp_std": 7},
    9: {"nombre": "Smoothie", "categoria": "bebida_fria", "vol_std": 0.35, "temp_std": 5},
    10: {"nombre": "Limonada", "categoria": "bebida_fria", "vol_std": 0.4, "temp_std": 5},
    11: {"nombre": "Té helado", "categoria": "bebida_fria", "vol_std": 0.3, "temp_std": 6},
    12: {"nombre": "Sopa", "categoria": "comida_caliente", "vol_std": 0.5, "temp_std": 80},
    13: {"nombre": "Pizza", "categoria": "comida_caliente", "masa_std": 0.4, "temp_std": 75},
    14: {"nombre": "Pasta", "categoria": "comida_caliente", "masa_std": 0.35, "temp_std": 75},
    15: {"nombre": "Hamburguesa", "categoria": "comida_caliente", "masa_std": 0.3, "temp_std": 70},
    16: {"nombre": "Arroz con pollo", "categoria": "comida_caliente", "masa_std": 0.45, "temp_std": 75},
    17: {"nombre": "Helado", "categoria": "comida_fria", "vol_std": 0.15, "temp_std": -6},
    18: {"nombre": "Ensalada fría", "categoria": "comida_fria", "masa_std": 0.25, "temp_std": 5},
    19: {"nombre": "Sushi", "categoria": "comida_fria", "masa_std": 0.35, "temp_std": 8},
    20: {"nombre": "Ensalada de frutas", "categoria": "comida_fria", "vol_std": 0.3, "temp_std": 5},
}

PROPIEDADES = {
    "bebida_caliente": {"cp": 4100, "densidad": 1000},
    "comida_caliente": {"cp": 2500, "densidad": 700},
    "bebida_fria": {"cp": 4180, "densidad": 1000},
    "comida_fria": {"cp": 2000, "densidad": 600},
}

EMPAQUES = {
    1: {"nombre": "Simple sin aislamiento", "u_val": 15},
    2: {"nombre": "Contenedor estándar", "u_val": 10},
    3: {"nombre": "Bolsa térmica básica", "u_val": 7},
    4: {"nombre": "Bolsa térmica premium", "u_val": 4},
    5: {"nombre": "Vaso térmico", "u_val": 3},
}

TRANSPORTES = {
    1: {"nombre": "Moto/Scooter", "vel_kmh": 40},
    2: {"nombre": "Automóvil", "vel_kmh": 50},
    3: {"nombre": "Bicicleta", "vel_kmh": 15},
    4: {"nombre": "A pie", "vel_kmh": 5},
}

# -----------------------------
# Nivel 3: Modelo de Dominio
# -----------------------------
@dataclass
class Food:
    id: int
    nombre: str
    categoria: str
    temp_inicial: float
    vol: float = None
    masa: float = None
    cp: float = field(init=False)
    dens: float = field(init=False)

    def __post_init__(self):
        p = PROPIEDADES[self.categoria]
        self.cp, self.dens = p['cp'], p['densidad']
        if self.masa is None:
            if self.vol:
                self.masa = self.dens * self.vol * 0.001 # Asumiendo vol en litros para obtener masa en kg
            else: # Si no hay vol, asumimos masa unitaria (ej. 1 kg), podría necesitar ajuste
                self.masa = 1.0


@dataclass
class Packaging:
    nombre: str
    u_val: float
    dims: tuple

    def area(self) -> float:
        l, w, h = self.dims
        return 2 * (l*w + l*h + w*h)

@dataclass
class Transporte:
    nombre: str
    vel_kmh: float

# -----------------------------
# Nivel 1.c: Calibration híbrido
# -----------------------------
@dataclass
class Calibration:
    def correct(self, food_id:int, pack_id:int, trans_id:int, dist_km:float, temp_phys:float) -> float:
        # Comparar con datos reales (placeholder)
        return 0.0

# -----------------------------
# Nivel 1.b: Simulador físico
# -----------------------------
@dataclass
class DeliverySim:
    food: Food
    pack: Packaging
    tiempo_min: float
    transporte: Transporte
    dist_km: float
    k: float = field(init=False)
    temp_final: float = field(init=False)
    temp_corrected: float = field(init=False)

    def __post_init__(self):
        A = self.pack.area()
        if self.food.masa == 0 or self.food.cp == 0:
            self.k = float('inf') 
        else:
            self.k = (self.pack.u_val * A) / (self.food.masa * self.food.cp)

        t = self.tiempo_min * 60
        
        if self.k == float('inf'):
             self.temp_final = TEMP_AMBIENTE
        elif np.isinf(self.k) or np.isnan(self.k):
             self.temp_final = TEMP_AMBIENTE
        else:
            self.temp_final = TEMP_AMBIENTE + (self.food.temp_inicial - TEMP_AMBIENTE) * np.exp(-self.k * t)
        
        corr = Calibration().correct(self.food.id, None, None, self.dist_km, self.temp_final)
        self.temp_corrected = self.temp_final + corr

    def summary_terminal(self):
        print("\n--- Resumen de entrega ---")
        print(f"Producto             : {self.food.nombre}")
        print(f"Transporte           : {self.transporte.nombre}")
        print(f"Distancia (km)       : {self.dist_km:.1f}")
        print(f"Tiempo (min)         : {self.tiempo_min:.1f}")
        print(f"Temp inicial         : {self.food.temp_inicial:.1f}°C")
        print(f"Temp final física   : {self.temp_final:.1f}°C")
        print(f"Temp final corregida : {self.temp_corrected:.1f}°C")

    def generate_image(self, path='resumen.png'):
        img = Image.new('RGB', (450, 250), 'white')
        draw = ImageDraw.Draw(img)
        posibles = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "arial.ttf", 
            "DejaVuSans.ttf"
        ]
        font = None
        for ruta in posibles:
            if os.path.exists(ruta):
                try:
                    font = ImageFont.truetype(ruta, 18)
                    break
                except:
                    continue
        if font is None:
            font = ImageFont.load_default()
        lines = [
            f"Producto             : {self.food.nombre}",
            f"Transporte           : {self.transporte.nombre}",
            f"Distancia (km)       : {self.dist_km:.1f}",
            f"Tiempo (min)         : {self.tiempo_min:.1f}",
            f"Temp inicial         : {self.food.temp_inicial:.1f}°C",
            f"Temp final física   : {self.temp_final:.1f}°C",
            f"Temp final corregida : {self.temp_corrected:.1f}°C",
        ]
        y = 20
        for line in lines:
            draw.text((20, y), line, fill='black', font=font)
            y += 30
        img.save(path)
        print(f"Imagen guardada en: {path}")
        return path

    def plot_temperature_profile(self, num_points=50, path=None):
        import matplotlib.pyplot as plt
        if self.k == float('inf') or np.isinf(self.k) or np.isnan(self.k):
             print("No se puede generar el perfil de temperatura debido a k inválido (masa/cp podría ser cero).")
             if path: 
                try:
                    fig, ax = plt.subplots(figsize=(6,4))
                    ax.text(0.5, 0.5, "Error: No se puede graficar el perfil de temperatura.\n(k inválido, posible masa/cp = 0)", 
                            horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
                    ax.set_xticks([])
                    ax.set_yticks([])
                    plt.title(f"Perfil temperatura: {self.food.nombre} - ERROR")
                    plt.savefig(path)
                    plt.close(fig)
                    print(f"Gráfico de error guardado en: {path}")
                except Exception as e:
                    print(f"Error al intentar guardar gráfico de error: {e}")
             else:
                 plt.figure(figsize=(6,4))
                 plt.text(0.5, 0.5, "Error: No se puede graficar el perfil de temperatura.\n(k inválido, posible masa/cp = 0)", 
                          horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                 plt.xticks([])
                 plt.yticks([])
                 plt.title(f"Perfil temperatura: {self.food.nombre} - ERROR")
                 plt.show()
             return

        tiempos = np.linspace(0, self.tiempo_min, num_points)
        temps = TEMP_AMBIENTE + (self.food.temp_inicial - TEMP_AMBIENTE) * np.exp(-self.k * (tiempos * 60))
        
        plt.figure(figsize=(6,4))
        plt.plot(tiempos, temps, marker='o', linestyle='-')
        plt.title(f"Perfil temperatura: {self.food.nombre}")
        plt.xlabel('Tiempo (min)')
        plt.ylabel('Temperatura (°C)')
        plt.grid(True)
        if path:
            plt.savefig(path)
            plt.close()
            print(f"Gráfico guardado en: {path}")
        else:
            plt.show()

    def time_to_temp(self, target_temp: float) -> float:
        if self.k <= 1e-9 or np.isinf(self.k) or np.isnan(self.k):
             return float('inf') 

        temp_diff_ratio_arg = (target_temp - TEMP_AMBIENTE) / (self.food.temp_inicial - TEMP_AMBIENTE + 1e-9)

        if temp_diff_ratio_arg <= 0: 
            if abs(target_temp - TEMP_AMBIENTE) < 1e-6 : 
                if abs(self.food.temp_inicial - TEMP_AMBIENTE) < 1e-6: return 0.0 
                else: return float('inf') 
            return float('inf')

        if ('caliente' in self.food.categoria and target_temp >= self.food.temp_inicial) or \
           ('fria' in self.food.categoria and target_temp <= self.food.temp_inicial) :
            return 0.0
        
        try:
            t_sec = -np.log(temp_diff_ratio_arg) / self.k
        except (ValueError,RuntimeWarning):
            return float('inf')
            
        return t_sec / 60.0

    def critical_time(self) -> float:
        crit_t = 60.0 if 'caliente' in self.food.categoria else 10.0
        return self.time_to_temp(crit_t)

    def analysis_report(self):
        print("\n--- Análisis de resultados ---")
        
        crit_temp = 60.0 if 'caliente' in self.food.categoria else 10.0
        initial_temp = self.food.temp_inicial
        corrected_temp = self.temp_corrected
        score_temp_0_1 = 0.0

        if 'caliente' in self.food.categoria:
            if initial_temp <= crit_temp: 
                score_temp_0_1 = 0.0
            else: 
                if (initial_temp - crit_temp) == 0: 
                    score_temp_0_1 = 0.0 if corrected_temp < initial_temp else 1.0
                else:
                    score_temp_0_1 = (corrected_temp - crit_temp) / (initial_temp - crit_temp)
        else: 
            if initial_temp >= crit_temp: 
                score_temp_0_1 = 0.0
            else: 
                if (crit_temp - initial_temp) == 0: 
                     score_temp_0_1 = 0.0 if corrected_temp > initial_temp else 1.0
                else:
                    score_temp_0_1 = (crit_temp - corrected_temp) / (crit_temp - initial_temp)
        
        score_temp_0_1 = max(0.0, min(score_temp_0_1, 1.0))

        max_vel_kmh = 0
        for t_info in TRANSPORTES.values():
            if t_info["vel_kmh"] > max_vel_kmh:
                max_vel_kmh = t_info["vel_kmh"]
        if max_vel_kmh == 0: max_vel_kmh = 50.0 

        ideal_time_for_dist = (self.dist_km / max_vel_kmh) * 60.0 if max_vel_kmh > 0 else float('inf')
        
        time_ratio = 1.0
        if self.dist_km <= 1e-6 : 
            time_ratio = 1.0 
        elif ideal_time_for_dist <= 1e-6: 
            time_ratio = 100.0 
        else:
            time_ratio = self.tiempo_min / ideal_time_for_dist

        score_time_0_1 = 0.0
        if time_ratio <= 1.2:
            score_time_0_1 = 1.0
        elif time_ratio <= 2.5:
            score_time_0_1 = 0.75
        elif time_ratio <= 4.0:
            score_time_0_1 = 0.40 
        else:
            score_time_0_1 = 0.10 

        if self.transporte.nombre == "A pie":
            if self.dist_km > 2.0: score_time_0_1 = min(score_time_0_1, 0.15)
            elif self.dist_km > 1.0: score_time_0_1 = min(score_time_0_1, 0.4)
        elif self.transporte.nombre == "Bicicleta":
            if self.dist_km > 7.0 and "caliente" in self.food.categoria : score_time_0_1 = min(score_time_0_1, 0.3)
            elif self.dist_km > 5.0 : score_time_0_1 = min(score_time_0_1, 0.5)
        
        if "Helado" == self.food.nombre or "Smoothie" == self.food.nombre: 
            if self.tiempo_min > 20: score_time_0_1 *= 0.5 
            elif self.tiempo_min > 15: score_time_0_1 *= 0.8
        elif "caliente" in self.food.categoria:
            if self.tiempo_min > 45: score_time_0_1 *= 0.7
            elif self.tiempo_min > 30: score_time_0_1 *= 0.9
            
        score_time_0_1 = max(0.0, min(score_time_0_1, 1.0))

        combined_score_0_1 = (0.65 * score_temp_0_1) + (0.35 * score_time_0_1)
        score_scaled = int(round(combined_score_0_1 * 9)) + 1
        
        comment = ""
        if score_scaled <= 3:
            comment = "Insatisfactorio (temperatura o tiempo deficientes)"
        elif score_scaled <= 6:
            comment = "Puede mejorar (aspectos de temperatura y/o tiempo son aceptables)"
        elif score_scaled <= 8:
            comment = "Buen nivel de conservación y tiempo de entrega"
        else:
            comment = "Excelente conservación y tiempo de entrega óptimo"
        
        print(f"Índice de satisfacción (1-10): {score_scaled} - {comment}")
        print(f"  (Debug: TempScore={score_temp_0_1:.2f}, TimeScore={score_time_0_1:.2f}, Combined={combined_score_0_1:.2f})")

        print(f"Tiempo crítico (hasta {crit_temp}°C): {self.critical_time():.1f} min")
        
        targets_display = []
        target_labels = []
        if 'caliente' in self.food.categoria:
            if abs(self.food.temp_inicial - TEMP_AMBIENTE) > 1e-6 : # Evitar división por cero o resultados extraños si temp_inicial == TEMP_AMBIENTE
                targets_display = [self.food.temp_inicial - 0.25 * (self.food.temp_inicial - TEMP_AMBIENTE), 
                                self.food.temp_inicial - 0.50 * (self.food.temp_inicial - TEMP_AMBIENTE),
                                self.food.temp_inicial - 0.75 * (self.food.temp_inicial - TEMP_AMBIENTE)]
                target_labels = ["25% pérdida calor", "50% pérdida calor", "75% pérdida calor"]
            else: # temp_inicial es igual a TEMP_AMBIENTE
                 print("La temperatura inicial es igual a la temperatura ambiente, no se calcula pérdida/ganancia de calor.")

        elif 'fria' in self.food.categoria:
            if abs(TEMP_AMBIENTE - self.food.temp_inicial) > 1e-6:
                targets_display = [self.food.temp_inicial + 0.25 * (TEMP_AMBIENTE - self.food.temp_inicial), 
                                self.food.temp_inicial + 0.50 * (TEMP_AMBIENTE - self.food.temp_inicial),
                                self.food.temp_inicial + 0.75 * (TEMP_AMBIENTE - self.food.temp_inicial)]
                target_labels = ["25% ganancia calor", "50% ganancia calor", "75% ganancia calor"]
            else: # temp_inicial es igual a TEMP_AMBIENTE
                 print("La temperatura inicial es igual a la temperatura ambiente, no se calcula pérdida/ganancia de calor.")


        for i, tgt_temp in enumerate(targets_display):
            tt = self.time_to_temp(tgt_temp)
            print(f"Tiempo hasta {target_labels[i]} ({tgt_temp:.1f}°C): {tt:.1f} min")

        best_u = min(e['u_val'] for e in EMPAQUES.values())
        area = self.pack.area()

        if self.food.masa > 0 and self.food.cp > 0 :
            k_best = (best_u * area) / (self.food.masa * self.food.cp)
            temp_best = TEMP_AMBIENTE + (self.food.temp_inicial - TEMP_AMBIENTE) * np.exp(-k_best * self.tiempo_min * 60)
            print(f"Temp final con aislamiento ideal (U={best_u}): {temp_best:.1f}°C")
        else:
            print(f"No se puede calcular Temp final con aislamiento ideal debido a masa/cp del producto.")


# Nivel 2: Controlador
def procesar_entrega(pid:int, eid:int, tid:int, dist:float) -> DeliverySim:
    info = PRODUCTOS[pid]
    dims = DIM_BEBIDA if 'bebida' in info['categoria'] else DIM_COMIDA
    
    vol_param = info.get('vol_std')
    masa_param = info.get('masa_std')
    
    food = Food(pid, info['nombre'], info['categoria'], info['temp_std'], 
                vol=vol_param, masa=masa_param)

    emp = EMPAQUES[eid]
    pack = Packaging(emp['nombre'], emp['u_val'], dims)
    tr = TRANSPORTES[tid]
    transporte = Transporte(tr['nombre'], tr['vel_kmh'])
    
    tiempo = 0.0
    if transporte.vel_kmh > 0:
        tiempo = dist / transporte.vel_kmh * 60 
    elif dist > 0: 
        tiempo = float('inf')
        print("Advertencia: El transporte tiene velocidad 0 km/h pero la distancia es > 0.")

    return DeliverySim(food, pack, tiempo, transporte, dist)

# --- NUEVA FUNCIÓN DE ENCABEZADO ---
def mostrar_encabezado():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(r"""
     █████╗  ██████╗ █████╗ ██╗    ███████╗███████╗███╗   ██╗
    ██╔══██╗██╔════╝██╔══██╗██║    ╚══███╔╝██╔════╝████╗  ██║
    ███████║██║     ███████║██║      ███╔╝ █████╗  ██╔██╗ ██║
    ██╔══██║██║     ██╔══██║██║     ███╔╝  ██╔══╝  ██║╚██╗██║
    ██║  ██║╚██████╗██║  ██║██║    ███████╗███████╗██║ ╚████║
    ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝    ╚══════╝╚══════╝╚═╝  ╚═══╝
    """)
    # Recuerda reemplazar "Tu Nombre", "@tusuario" y "[--]" con tu información real.
    print("\nAçai Zen Delivery Simulator [--]")
    print("Created by: Grupo E4") # CAMBIAR POR TU NOMBRE
    print("    Version: 1.0")
    print("    Codename: Tropical [--]")
    print("GitHub: @tusuario [--]\n") # CAMBIAR POR TU GITHUB


# Nivel 1: Interfaz Usuario
def main():
    mostrar_encabezado() # Llamada al nuevo encabezado
    
    prompt_prefix = "AcaiZen@Delivery ~ "

    opciones = {1:'bebida_caliente',2:'bebida_fria',3:'comida_caliente',4:'comida_fria'}
    print("Categorías disponibles:")
    for k,v in opciones.items(): print(f"  {k}) {v.replace('_',' ').title()}")
    
    cat_choice = 0
    while cat_choice not in opciones:
        try:
            cat_choice_input = input(f"{prompt_prefix}Seleccione categoría ({','.join(map(str, opciones.keys()))}): ").strip()
            if not cat_choice_input: continue # Permitir reintentar si la entrada está vacía
            cat_choice = int(cat_choice_input)
            if cat_choice not in opciones: print("Opción inválida. Intente de nuevo.")
        except ValueError:
            print("Entrada inválida. Por favor ingrese un número.")
    cat = opciones[cat_choice]

    print(f"\nProductos de {cat.replace('_',' ').title()}:")
    productos_en_categoria = {pid: info for pid, info in PRODUCTOS.items() if info['categoria']==cat}
    for pid_key, info in productos_en_categoria.items(): # Cambiado pid a pid_key para evitar conflicto
        print(f"  #{pid_key}: {info['nombre']}")
    
    pid = 0 # Renombrado de la variable de producto elegida
    while pid not in productos_en_categoria:
        try:
            pid_input = input(f"{prompt_prefix}ID producto ({','.join(map(str, productos_en_categoria.keys()))}): ").strip()
            if not pid_input: continue
            pid = int(pid_input)
            if pid not in productos_en_categoria: print("ID de producto no válido para esta categoría. Intente de nuevo.")
        except ValueError:
            print("Entrada inválida. Por favor ingrese un número.")

    print("\nEmpaques disponibles:")
    for eid_key, info in EMPAQUES.items(): print(f"  #{eid_key}: {info['nombre']}") # Cambiado eid a eid_key
    eid = 0 # Renombrado de la variable de empaque elegida
    while eid not in EMPAQUES:
        try:
            eid_input = input(f"{prompt_prefix}ID empaque ({','.join(map(str, EMPAQUES.keys()))}): ").strip()
            if not eid_input: continue
            eid = int(eid_input)
            if eid not in EMPAQUES: print("ID de empaque no válido. Intente de nuevo.")
        except ValueError:
            print("Entrada inválida. Por favor ingrese un número.")

    print("\nTransportes disponibles:")
    for tid_key, info in TRANSPORTES.items(): print(f"  #{tid_key}: {info['nombre']}") # Cambiado tid a tid_key
    tid = 0 # Renombrado de la variable de transporte elegida
    while tid not in TRANSPORTES:
        try:
            tid_input = input(f"{prompt_prefix}ID transporte ({','.join(map(str, TRANSPORTES.keys()))}): ").strip()
            if not tid_input: continue
            tid = int(tid_input)
            if tid not in TRANSPORTES: print("ID de transporte no válido. Intente de nuevo.")
        except ValueError:
            print("Entrada inválida. Por favor ingrese un número.")

    dist = -1.0
    while dist < 0:
        try:
            dist_input = input(f"{prompt_prefix}Distancia km (ej. 3.5): ").strip()
            if not dist_input: continue
            dist = float(dist_input)
            if dist < 0: print("La distancia no puede ser negativa. Intente de nuevo.")
        except ValueError:
            print("Entrada inválida. Por favor ingrese un número para la distancia.")

    sim = procesar_entrega(pid, eid, tid, dist)
    sim.summary_terminal()
    
    try:
        sim.generate_image()
    except Exception as e:
        print(f"Error generando imagen: {e}. Puede faltar una fuente o librería.")
        
    try:
        sim.plot_temperature_profile(path='perfil_temperatura.png')
    except ImportError:
        print("Matplotlib no está instalado. No se pudo generar el gráfico de perfil de temperatura.")
    except Exception as e:
        print(f"Error generando gráfico de perfil de temperatura: {e}")
        
    sim.analysis_report()
    print(f"\n{prompt_prefix}Simulación completada.")

if __name__=='__main__':
    main()