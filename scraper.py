import praw
import re  # Importamos regex para validar enlaces
from config import Config
from textblob import TextBlob  # Importamos TextBlob para análisis de sentimientos

class RedditScraper:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=Config.CLIENT_ID,
            client_secret=Config.CLIENT_SECRET,
            user_agent=Config.USER_AGENT
        )

    def contiene_enlace(self, texto):
        """
        Valida si el texto contiene un enlace (URL).
        """
        # Expresión regular para detectar URLs
        regex_url = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.search(regex_url, texto) is not None

    def obtener_historias(self, subreddit, limite=10):
        historias = []
        try:
            # Extraer posts hasta que tengamos el número deseado de historias válidas
            for post in self.reddit.subreddit(subreddit).hot(limit=None):  # None para extraer todos los posts necesarios
                if len(historias) >= limite:
                    break  # Detener si ya tenemos suficientes historias válidas

                if not post.stickied:  # Ignorar posts fijados
                    historia = post.selftext
                    titulo = post.title

                    # Validar que ni el título ni la historia contengan URLs
                    if (not self.contiene_enlace(historia) and 
                        not self.contiene_enlace(titulo) and 
                        len(historia) >= 50):  # Solo historias con más de 50 caracteres

                        # 🔹 Análisis de sentimiento con TextBlob
                        blob = TextBlob(historia)
                        sentimiento = blob.sentiment.polarity  # Polaridad entre -1 (negativo) y 1 (positivo)

                        historias.append({
                            "Indice": f"[{int((sentimiento + 1) * 50)}]",  # Escala 0-100
                            "Upvotes": f"{{{post.score}}}",  # Upvotes entre llaves
                            "Titulo": titulo,  # Título del post
                            "Usuario": post.author.name if post.author else "Desconocido",  # Autor del post
                            "Historia": historia  # Texto completo de la historia
                        })
        except Exception as e:
            print(f"Error al obtener datos: {e}")
        return historias