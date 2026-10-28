"""
Sistema de Gestión de Inventario y Registro de Ventas
"""

from pathlib import Path
from datetime import datetime

CARPETA = Path(__file__).resolve().parent
ARCHIVO_INVENTARIO = CARPETA / "inventario.txt"
ARCHIVO_VENTAS = CARPETA / "ventas.txt"


def cargar_inventario():
    """Lee productos desde inventario.txt y devuelve una lista de diccionarios."""
    productos = []

    try:
        with open(ARCHIVO_INVENTARIO, "r", encoding="utf-8") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                linea = linea.strip()
                if not linea:
                    continue

                partes = linea.split("|")
                if len(partes) != 4:
                    print(f"Aviso: se omitió la línea {numero_linea} por formato incorrecto.")
                    continue

                try:
                    codigo = partes[0].strip()
                    nombre = partes[1].strip()
                    precio = float(partes[2])
                    stock = int(partes[3])

                    if not codigo or not nombre or precio < 0 or stock < 0:
                        print(f"Aviso: se omitió la línea {numero_linea} por datos inválidos.")
                        continue

                    if any(producto["codigo"] == codigo for producto in productos):
                        print(f"Aviso: código duplicado '{codigo}' en la línea {numero_linea}.")
                        continue

                    productos.append({
                        "codigo": codigo,
                        "nombre": nombre,
                        "precio": precio,
                        "stock": stock
                    })
                except ValueError:
                    print(f"Aviso: se omitió la línea {numero_linea} por precio o stock inválido.")

    except FileNotFoundError:
        # Es normal la primera vez: el archivo se creará al guardar.
        pass
    except OSError as error:
        print(f"Error al leer el inventario: {error}")
    else:
        pass
    finally:
        # El bloque finally se ejecuta tanto si hubo error como si no.
        pass

    return productos


def guardar_inventario(productos):
    """Guarda la lista completa de productos en inventario.txt."""
    try:
        with open(ARCHIVO_INVENTARIO, "w", encoding="utf-8") as archivo:
            for producto in productos:
                linea = (
                    f'{producto["codigo"]}|{producto["nombre"]}|'
                    f'{producto["precio"]:.2f}|{producto["stock"]}\n'
                )
                archivo.write(linea)
    except OSError as error:
        print(f"Error al guardar el inventario: {error}")
        return False
    else:
        return True
    finally:
        pass


def registrar_producto(productos):
    """Solicita y registra un nuevo producto."""
    print("\n--- REGISTRAR PRODUCTO ---")
    try:
        codigo = input("Código del producto: ").strip()
        if not codigo:
            print("El código no puede estar vacío.")
            return

        if any(producto["codigo"] == codigo for producto in productos):
            print("Error: ya existe un producto con ese código.")
            return

        nombre = input("Nombre del producto: ").strip()
        if not nombre or "|" in nombre:
            print("El nombre no puede estar vacío ni contener el carácter '|'.")
            return

        precio = float(input("Precio (S/): "))
        if precio < 0:
            print("El precio no puede ser negativo.")
            return

        stock = int(input("Stock inicial: "))
        if stock < 0:
            print("El stock no puede ser negativo.")
            return

    except ValueError:
        print("Entrada inválida: el precio debe ser numérico y el stock debe ser entero.")
        return
    else:
        productos.append({
            "codigo": codigo,
            "nombre": nombre,
            "precio": precio,
            "stock": stock
        })

        if guardar_inventario(productos):
            print("Producto registrado correctamente.")
        else:
            # Evita dejar el producto agregado solo en memoria si falla el guardado.
            productos.pop()
            print("No se confirmó el registro porque no se pudo guardar el archivo.")
    finally:
        pass


def consultar_inventario(productos):
    """Muestra todos los productos registrados."""
    print("\n--- INVENTARIO ---")
    if not productos:
        print("No hay productos registrados.")
        return

    print(f'{"CÓDIGO":<12} {"PRODUCTO":<25} {"PRECIO (S/)":>12} {"STOCK":>8}')
    print("-" * 61)
    for producto in productos:
        print(
            f'{producto["codigo"]:<12} '
            f'{producto["nombre"][:25]:<25} '
            f'{producto["precio"]:>12.2f} '
            f'{producto["stock"]:>8}'
        )


def buscar_producto(productos):
    """Busca un producto por su código."""
    codigo = input("Ingrese el código que desea buscar: ").strip()
    for producto in productos:
        if producto["codigo"] == codigo:
            print(
                f'Código: {producto["codigo"]}\n'
                f'Nombre: {producto["nombre"]}\n'
                f'Precio: S/ {producto["precio"]:.2f}\n'
                f'Stock: {producto["stock"]}'
            )
            return producto
    print("No se encontró un producto con ese código.")
    return None


def actualizar_stock(productos):
    """Permite sumar unidades al stock de un producto existente."""
    print("\n--- ACTUALIZAR STOCK ---")
    producto = buscar_producto(productos)
    if producto is None:
        return

    try:
        cantidad = int(input("Cantidad que desea agregar: "))
        if cantidad <= 0:
            print("La cantidad debe ser mayor que cero.")
            return
    except ValueError:
        print("Entrada inválida: escriba un número entero.")
        return
    else:
        producto["stock"] += cantidad
        if guardar_inventario(productos):
            print(f'Stock actualizado. Nuevo stock: {producto["stock"]}')
        else:
            producto["stock"] -= cantidad
            print("No se pudo guardar el cambio; se revirtió en memoria.")
    finally:
        pass


def registrar_venta(productos):
    """Registra una venta, descuenta stock y agrega la operación al historial."""
    print("\n--- REGISTRAR VENTA ---")
    codigo = input("Código del producto vendido: ").strip()

    producto = None
    for elemento in productos:
        if elemento["codigo"] == codigo:
            producto = elemento
            break

    if producto is None:
        print("No existe un producto con ese código.")
        return

    try:
        cantidad = int(input("Cantidad vendida: "))
        if cantidad <= 0:
            print("La cantidad debe ser mayor que cero.")
            return
        if cantidad > producto["stock"]:
            print("No hay suficiente stock para completar la venta.")
            return
    except ValueError:
        print("Entrada inválida: la cantidad debe ser un número entero.")
        return

    subtotal = producto["precio"] * cantidad
    descuento = 0.0
    if subtotal >= 200:
        descuento = subtotal * 0.05

    total = subtotal - descuento
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registro = (
        f"{fecha}|{producto['codigo']}|{producto['nombre']}|{cantidad}|"
        f"{subtotal:.2f}|{descuento:.2f}|{total:.2f}\n"
    )

    stock_anterior = producto["stock"]
    producto["stock"] -= cantidad

    # Primero se guarda el nuevo inventario. Si falla, no se registra la venta.
    if not guardar_inventario(productos):
        producto["stock"] = stock_anterior
        print("No se completó la venta porque no se pudo guardar el inventario.")
        return

    try:
        with open(ARCHIVO_VENTAS, "a", encoding="utf-8") as archivo:
            archivo.write(registro)
    except OSError as error:
        # Se intenta restaurar el stock si el historial no pudo guardarse.
        producto["stock"] = stock_anterior
        guardar_inventario(productos)
        print(f"No se pudo guardar la venta: {error}")
        print("Se intentó restaurar el stock anterior.")
        return
    else:
        print("\nVenta registrada correctamente.")
        print(f"Producto: {producto['nombre']}")
        print(f"Cantidad: {cantidad}")
        print(f"Subtotal: S/ {subtotal:.2f}")
        print(f"Descuento: S/ {descuento:.2f}")
        print(f"Total a pagar: S/ {total:.2f}")
        print(f'Stock restante: {producto["stock"]}')
    finally:
        pass


def mostrar_reporte_ventas():
    """Lee y muestra el historial de ventas guardado en ventas.txt."""
    print("\n--- HISTORIAL DE VENTAS ---")
    try:
        with open(ARCHIVO_VENTAS, "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()
    except FileNotFoundError:
        print("Todavía no existe un historial de ventas.")
        return
    except OSError as error:
        print(f"Error al leer el historial: {error}")
        return
    else:
        if not lineas:
            print("No hay ventas registradas.")
            return

        acumulado = 0.0
        for linea in lineas:
            partes = linea.strip().split("|")
            if len(partes) != 7:
                print("Aviso: se encontró una venta con formato incorrecto.")
                continue
            try:
                total = float(partes[6])
            except ValueError:
                print("Aviso: se encontró un total de venta inválido.")
                continue

            print(
                f"Fecha: {partes[0]} | Código: {partes[1]} | "
                f"Producto: {partes[2]} | Cantidad: {partes[3]} | "
                f"Total: S/ {total:.2f}"
            )
            acumulado += total

        print(f"\nTotal acumulado de ventas: S/ {acumulado:.2f}")
    finally:
        pass


def mostrar_menu():
    """Muestra las opciones disponibles."""
    print("\n========== SISTEMA DE INVENTARIO Y VENTAS ==========")
    print("1. Registrar producto")
    print("2. Consultar inventario")
    print("3. Buscar producto")
    print("4. Actualizar stock")
    print("5. Registrar venta")
    print("6. Mostrar historial y reporte de ventas")
    print("0. Salir")


def main():
    """Coordina el menú y las operaciones del sistema."""
    productos = cargar_inventario()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_producto(productos)
        elif opcion == "2":
            consultar_inventario(productos)
        elif opcion == "3":
            buscar_producto(productos)
        elif opcion == "4":
            actualizar_stock(productos)
        elif opcion == "5":
            registrar_venta(productos)
        elif opcion == "6":
            mostrar_reporte_ventas()
        elif opcion == "0":
            print("Gracias por utilizar el sistema. ¡Hasta pronto!")
            break
        else:
            print("Opción inválida. Seleccione una opción del menú.")


if __name__ == "__main__":
    main()
