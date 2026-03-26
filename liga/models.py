from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# 1. PERFIL DE ENTRENADOR
class Jugador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname_pokemmo = models.CharField(max_length=100, unique=True)
    puntuacion = models.IntegerField(default=500)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    lema = models.CharField(max_length=150, blank=True, default="¡Listo para la batalla!")
    
    # Estadísticas acumuladas en la temporada
    victorias = models.PositiveIntegerField(default=0)
    derrotas = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nickname_pokemmo

    @property
    def winrate(self):
        total = self.victorias + self.derrotas
        return round((self.victorias / total) * 100, 1) if total > 0 else 0

    @property
    def rango(self):
        if self.puntuacion < 600: return "Bronce"
        if self.puntuacion < 800: return "Plata"
        if self.puntuacion < 1000: return "Oro"
        if self.puntuacion < 1200: return "Platino"
        if self.puntuacion < 1400: return "Diamante"
        return "Maestro"

# 2. SISTEMA DE DUELOS (La pieza que faltaba)
class Combate(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADO', 'Aceptado'),
        ('RECHAZADO', 'Rechazado'),
        ('ESPERANDO', 'Esperando Confirmación'),
        ('FINALIZADO', 'Finalizado'),
    ]

    retador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='retos_enviados')
    oponente = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='retos_recibidos')
    ganador = models.ForeignKey(Jugador, on_delete=models.SET_NULL, null=True, blank=True, related_name='combates_ganados')
    reportado_por = models.ForeignKey(Jugador, on_delete=models.SET_NULL, null=True, blank=True, related_name='combates_reportados')
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.retador} vs {self.oponente} ({self.estado})"

# 3. HISTÓRICO DE TEMPORADAS
class Temporada(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Nombres guardados en texto para que no se borren si el jugador se va
    puesto_1 = models.CharField(max_length=100, blank=True)
    puesto_2 = models.CharField(max_length=100, blank=True)
    puesto_3 = models.CharField(max_length=100, blank=True)
    
    foto_1 = models.ImageField(upload_to='hall_of_fame/', null=True, blank=True)

    def __str__(self):
        return f"Temporada {self.numero}: {self.nombre}"

# --- AUTOMATIZACIÓN (SIGNALS) ---

@receiver(post_save, sender=Temporada)
def procesar_cierre_temporada(sender, instance, created, **kwargs):
    """ Al crear una temporada nueva, captura el podio y resetea el ranking """
    if created:
        top_jugadores = Jugador.objects.all().order_by('-puntuacion')[:3]
        
        # Guardar ganadores en la ficha histórica
        if len(top_jugadores) >= 1:
            instance.puesto_1 = top_jugadores[0].nickname_pokemmo
            instance.foto_1 = top_jugadores[0].avatar
        if len(top_jugadores) >= 2:
            instance.puesto_2 = top_jugadores[1].nickname_pokemmo
        if len(top_jugadores) >= 3:
            instance.puesto_3 = top_jugadores[2].nickname_pokemmo
        
        # Guardado interno para no disparar el signal infinitamente
        sender.objects.filter(id=instance.id).update(
            puesto_1=instance.puesto_1, 
            puesto_2=instance.puesto_2, 
            puesto_3=instance.puesto_3,
            foto_1=instance.foto_1
        )

        # REINICIO MAESTRO: Puntos a 500 y récords a cero
        Jugador.objects.all().update(puntuacion=500, victorias=0, derrotas=0)

@receiver(post_delete, sender=Jugador)
def eliminar_usuario_al_borrar_jugador(sender, instance, **kwargs):
    if instance.usuario:
        instance.usuario.delete()