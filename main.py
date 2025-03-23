from scraper import RedditScraper
from file_manager import FileManager
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import pandas as pd
from gtts import gTTS
from playsound import playsound


class App:
    def __init__(self, historias, file_manager, subreddit):
        self.historias = historias
        self.file_manager = file_manager
        self.subreddit = subreddit
        self.indice_actual = 0

        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("Revisar Historias de Reddit")
        self.root.geometry("600x700")  # Tamaño fijo para la ventana
        self.root.resizable(False, False)  # Deshabilitar redimensionamiento

        # Mostrar la primera historia
        self.mostrar_historia()

        # Iniciar el bucle de Tkinter
        self.root.mainloop()

    def mostrar_historia(self):
        """Muestra la historia actual en la interfaz gráfica."""
        # Limpiar la ventana
        for widget in self.root.winfo_children():
            widget.destroy()

        # Obtener la historia actual
        historia = self.historias[self.indice_actual]

        # Mostrar el título y el autor
        titulo_autor = f"{historia['Titulo']} ----- {historia['Usuario']}"
        label_titulo = tk.Label(self.root, text=titulo_autor, font=("Arial", 14, "bold"))
        label_titulo.pack(pady=10)

        # Mostrar los upvotes
        label_upvotes = tk.Label(self.root, text=f"Upvotes: {historia['Upvotes']}", font=("Arial", 12))
        label_upvotes.pack(pady=5)

        # Mostrar la historia con scroll
        frame_historia = tk.Frame(self.root)
        frame_historia.pack(pady=10, padx=10, fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_historia)
        scrollbar.pack(side="right", fill="y")

        text_historia = tk.Text(frame_historia, wrap="word", yscrollcommand=scrollbar.set)
        text_historia.insert("1.0", historia['Historia'])
        text_historia.config(state="disabled")  # Hacer el texto de solo lectura
        text_historia.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=text_historia.yview)

        # Botones de decisión
        frame_botones = tk.Frame(self.root)
        frame_botones.pack(pady=10)

        btn_escuchar = tk.Button(frame_botones, text="Escuchar (Inglés)", command=lambda: self.escuchar_historia(historia['Historia']))
        btn_escuchar.pack(side="left", padx=5)

        btn_buena = tk.Button(frame_botones, text="Buena", command=lambda: self.procesar_decision("buena"))
        btn_buena.pack(side="left", padx=5)

        btn_mala = tk.Button(frame_botones, text="Mala", command=lambda: self.procesar_decision("mala"))
        btn_mala.pack(side="left", padx=5)

        btn_rechazar = tk.Button(frame_botones, text="Rechazar", command=lambda: self.procesar_decision("rechazar"))
        btn_rechazar.pack(side="left", padx=5)

    def escuchar_historia(self, texto):
        """
        Convierte el texto a voz en inglés usando gTTS y lo reproduce directamente.
        """
        try:
            # Crear un archivo de audio temporal
            tts = gTTS(text=texto, lang='en', slow=False)  # Idioma inglés
            tts.save("temp_audio.mp3")

            # Reproducir el archivo de audio directamente
            playsound("temp_audio.mp3")

            # Eliminar el archivo temporal después de reproducirlo
            os.remove("temp_audio.mp3")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir la historia: {e}")

    def procesar_decision(self, decision):
        """Procesa la decisión del usuario sobre la historia actual."""
        historia = self.historias[self.indice_actual]

        if decision == "buena":
            # Aumentar el sentimiento (ajustar el índice)
            historia["Indice"] = f"[{int((float(historia['Indice'][1:-1]) + 10))}]"
        elif decision == "mala":
            # Disminuir el sentimiento (ajustar el índice)
            historia["Indice"] = f"[{int((float(historia['Indice'][1:-1]) - 10))}]"
        elif decision == "rechazar":
            # Omitir la historia (no se guarda)
            self.indice_actual += 1
            if self.indice_actual < len(self.historias):
                self.mostrar_historia()
            else:
                self.finalizar()
            return

        # Guardar la historia actual
        self.file_manager.guardar_csv([historia], self.subreddit)

        # Pasar a la siguiente historia
        self.indice_actual += 1
        if self.indice_actual < len(self.historias):
            self.mostrar_historia()
        else:
            self.finalizar()

    def finalizar(self):
        """Finaliza la revisión de historias."""
        messagebox.showinfo("Fin", "Todas las historias han sido revisadas.")
        self.root.destroy()


def menu_principal():
    """Muestra un menú principal con dos opciones: extraer nuevas historias o descargar CSV."""
    root = tk.Tk()
    root.title("Menú Principal")
    root.geometry("300x200")
    root.resizable(False, False)  # Deshabilitar redimensionamiento

    def extraer_historias():
        root.destroy()
        main()

    def descargar_csv():
        archivo_csv = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("CSV Files", "*.csv")])
        if archivo_csv:
            messagebox.showinfo("Éxito", f"Archivo CSV seleccionado: {archivo_csv}")

    btn_extraer = tk.Button(root, text="Extraer nuevas historias", command=extraer_historias)
    btn_extraer.pack(pady=20)

    btn_descargar = tk.Button(root, text="Descargar CSV", command=descargar_csv)
    btn_descargar.pack(pady=20)

    root.mainloop()


def main():
    """Función principal para iniciar el scraper y la interfaz gráfica."""
    root = tk.Tk()
    root.title("Configuración")
    root.geometry("300x350")
    root.resizable(False, False)  # Deshabilitar redimensionamiento

    label_subreddit = tk.Label(root, text="Introduce el nombre del subreddit:")
    label_subreddit.pack(pady=10)

    entry_subreddit = tk.Entry(root)
    entry_subreddit.pack(pady=5)

    label_limite = tk.Label(root, text="Introduce el número de posts a extraer:")
    label_limite.pack(pady=10)

    entry_limite = tk.Entry(root)
    entry_limite.pack(pady=5)

    def iniciar_scraper():
        subreddit = entry_subreddit.get()
        limite = int(entry_limite.get())
        root.destroy()

        scraper = RedditScraper()
        historias = scraper.obtener_historias(subreddit, limite)

        if historias:
            file_manager = FileManager()
            App(historias, file_manager, subreddit)  # Iniciar la interfaz gráfica
        else:
            messagebox.showinfo("Info", "No se encontraron historias.")

    btn_iniciar = tk.Button(root, text="Iniciar", command=iniciar_scraper)
    btn_iniciar.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    menu_principal()