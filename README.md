# Acai_Zen
# Simulador de Delivery de Alimentos

Este script simula cómo cambia la temperatura de los alimentos durante la entrega a domicilio, utilizando principios básicos de física térmica.

## 📝 Descripción General

Este simulador permite calcular cómo cambiará la temperatura de un alimento o bebida durante su transporte, considerando:
- Tipo de alimento o bebida
- Tipo de empaque
- Medio de transporte
- Distancia a recorrer

El modelo físico utiliza la Ley de Enfriamiento de Newton para predecir la temperatura final del producto después de la entrega.

## 💻 Requisitos

- Python 3.7+
- Bibliotecas: 
  - numpy: para cálculos matemáticos (como la función exponencial)
  - PIL (Pillow): para generar imágenes con el resumen
  - dataclasses: para crear clases de datos estructurados

## 🧩 Estructura del Código

El código se organiza en:

1. **Diccionarios de datos** - Contienen información precargada sobre los productos, empaques y métodos de transporte
2. **Clases** - Modelan los elementos del sistema y la simulación
3. **Función principal** - Controla el flujo de la aplicación

## 📚 Diccionarios de Datos

### 1. `productos`
Almacena información sobre los alimentos disponibles, organizados por categorías:

- **Bebidas calientes (IDs 1-5)**: café, té, chocolate caliente, etc.
- **Bebidas frías (IDs 6-11)**: refrescos, jugos, etc.
- **Comidas calientes (IDs 12-16)**: sopa, pizza, etc.
- **Comidas frías (IDs 17-20)**: helado, ensalada, etc.

Cada producto contiene:
- `nombre`: Nombre del producto
- `categoria`: Categoría a la que pertenece
- `vol_std`: Volumen estándar en litros (para bebidas)
- `masa_std`: Masa estándar en kg (para comidas)
- `temp_std`: Temperatura estándar inicial en °C

### 2. `propiedades`
Contiene propiedades físicas de cada categoría de alimento:

- `cp`: Capacidad calorífica específica (J/kg·°C) - Mide cuánta energía térmica puede almacenar el material
- `densidad`: Densidad en kg/m³ - Relación entre masa y volumen

### 3. `empaques`
Tipos de contenedores disponibles:

- `nombre`: Descripción del empaque
- `u_val`: Valor U (coeficiente de transferencia térmica) - Más bajo significa mejor aislamiento

### 4. `transportes`
Medios de transporte para la entrega:

- `nombre`: Tipo de transporte
- `vel_kmh`: Velocidad promedio en km/h

### 5. Variables Constantes
- `DIM_BEBIDA` y `DIM_COMIDA`: Dimensiones estándar (largo, ancho, alto) en metros
- `TEMP_AMBIENTE`: Temperatura ambiente en °C (25°C por defecto)

## 📦 Clases

### 1. `Food`
Representa el alimento o bebida con sus propiedades físicas:

```python
@dataclass
class Food:
    """Modelo físico del alimento/bebida"""
    id: int                # ID del producto
    nombre: str            # Nombre del producto
    categoria: str         # Categoría (bebida_caliente, comida_fria, etc.)
    temp_inicial: float    # Temperatura inicial en °C
    vol: float = None      # Volumen en litros (opcional)
    masa: float = None     # Masa en kg (opcional)
    cp: float = field(init=False)      # Capacidad calorífica (calculada automáticamente)
    dens: float = field(init=False)    # Densidad (calculada automáticamente)
```

El método `__post_init__` se ejecuta después de la inicialización para:
1. Asignar valores de capacidad calorífica y densidad según la categoría
2. Calcular la masa a partir del volumen si la masa no se proporciona

### 2. `Packaging`
Modelo del empaque:

```python
@dataclass
class Packaging:
    """Datos y geometría del empaque"""
    nombre: str    # Nombre del empaque
    u_val: float   # Coeficiente de transferencia térmica
    dims: tuple    # Dimensiones (largo, ancho, alto) en metros
    
    def area(self):
        # Calcula el área superficial del empaque (suma de las 6 caras)
        l,w,h = self.dims
        return 2*(l*w + l*h + w*h)
```

### 3. `DeliverySim`
Realiza la simulación de entrega:

```python
@dataclass
class DeliverySim:
    """Simulación del enfriamiento por convección según Newton."""
    food: Food             # Alimento a entregar
    pack: Packaging        # Empaque utilizado
    tiempo_min: float      # Tiempo de entrega en minutos
    transporte: str        # Método de transporte
    k: float = field(init=False)       # Constante de proporcionalidad (calculada)
    temp_final: float = field(init=False)  # Temperatura final calculada
```

Métodos importantes:
- `__post_init__`: Calcula:
  1. La constante `k` para la ecuación de enfriamiento
  2. La temperatura final después del tiempo de entrega
- `summary_terminal`: Muestra un resumen de la entrega en la terminal
- `generate_image`: Crea una imagen con el resumen de la entrega

## 🔄 Flujo del Programa

La función `main()` controla el flujo del programa:

1. Muestra el menú principal para seleccionar la categoría de producto
2. Presenta los productos disponibles en esa categoría
3. Permite elegir el tipo de empaque
4. Solicita el tipo de transporte y la distancia
5. Calcula el tiempo de entrega según la distancia y velocidad
6. Crea los objetos necesarios para la simulación:
   - Objeto `Food` con los datos del producto
   - Objeto `Packaging` con los datos del empaque
   - Objeto `DeliverySim` para realizar la simulación
7. Muestra el resultado en la terminal y genera una imagen

8. 

## 🚀 Guía de Uso

1. Ejecuta el programa: `python nombre_del_archivo.py`

2. Sigue las instrucciones en pantalla:
   - Selecciona el tipo de producto (bebida caliente/fría, comida caliente/fría)
   - Elige un producto específico de la categoría
   - Selecciona el tipo de empaque
   - Elige el método de transporte
   - Ingresa la distancia de entrega

3. El programa calculará y mostrará:
   - Un resumen de la entrega en la terminal
   - Una imagen con el resultado guardada como "resumen.png"

## 🔍 Ejemplo de Uso

```
=== Bienvenido al simulador de delivery ===
1) Ordenar bebida caliente
2) Ordenar bebida fría
3) Ordenar comida caliente
4) Ordenar comida fría
Seleccione opción (1-4): 1

Productos disponibles (bebida_caliente):
#1: Café
#2: Té
#3: Chocolate caliente
#4: Matcha latte
#5: Chai
ID producto: 1

Empaques:
#1: Simple sin aislamiento
#2: Contenedor estándar
#3: Bolsa térmica básica
#4: Bolsa térmica premium
#5: Vaso térmico
ID empaque: 5

Transportes:
#1: Moto/Scooter
#2: Automóvil
#3: Bicicleta
#4: A pie
ID transporte: 3
Distancia al local (km): 2

--- Resumen de entrega ---
Producto     : Café
Transporte   : Bicicleta
Tiempo (min) : 8.0
Temp inicial : 85.0°C
Temp final   : 65.3°C
Imagen guardada en: resumen.png
```
