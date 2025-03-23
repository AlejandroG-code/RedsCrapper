import os
import csv

class FileManager:
    def __init__(self, carpeta_salida="historias"):
        self.carpeta_salida = carpeta_salida
        os.makedirs(self.carpeta_salida, exist_ok=True)

    def guardar_csv(self, datos, subreddit):
        archivo_salida = os.path.join(self.carpeta_salida, f"{subreddit}.csv")

        # Verificar si el archivo ya existe
        archivo_existe = os.path.isfile(archivo_salida)

        try:
            with open(archivo_salida, mode="a" if archivo_existe else "w", encoding="utf-8", newline="") as f:
                fieldnames = ["Indice", "Upvotes", "Titulo", "Usuario", "Historia"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                # Escribir encabezados solo si el archivo no existe
                if not archivo_existe:
                    writer.writeheader()

                # Escribir datos
                for historia in datos:
                    writer.writerow({
                        "Indice": historia["Indice"],
                        "Upvotes": historia["Upvotes"],
                        "Titulo": historia["Titulo"],
                        "Usuario": historia["Usuario"],
                        "Historia": historia["Historia"]
                    })
                    
            print(f"✅ Historias guardadas en {archivo_salida}")
        except Exception as e:
            print(f"❌ Error al guardar el archivo: {e}")