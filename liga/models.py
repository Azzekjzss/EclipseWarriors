from django.db import models

class Jugador(models.Model):
    nickname_pokemmo = models.CharField(max_length=100, unique=True)
    puntuacion = models.IntegerField(default=500)
    rango = models.CharField(max_length=50, default='Bronce')
    victorias = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatares/', null=True, blank=True)
    lema = models.CharField(max_length=200, blank=True)
    equipo = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nickname_pokemmo

class Combate(models.Model):
    ESTADOS = [('PENDIENTE', 'Pendiente'), ('FINALIZADO', 'Finalizado')]
    retador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='retador')
    oponente = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='oponente')
    ganador = models.ForeignKey(Jugador, on_delete=models.SET_NULL, null=True, blank=True, related_name='ganador_combate')
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    puntos_ganados = models.IntegerField(default=20)
    puntos_perdidos = models.IntegerField(default=15)

    def __str__(self):
        return f"{self.retador} vs {self.oponente}"

class Temporada(models.Model):
    nombre = models.CharField(max_length=100, default="Temporada 1")
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    campeon = models.CharField(max_length=100, blank=True)
    subcampeon = models.CharField(max_length=100, blank=True)
    tercer_lugar = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            top_3 = Jugador.objects.order_by('-puntuacion')[:3]
            if len(top_3) >= 1: self.campeon = top_3[0].nickname_pokemmo
            if len(top_3) >= 2: self.subcampeon = top_3[1].nickname_pokemmo
            if len(top_3) >= 3: self.tercer_lugar = top_3[2].nickname_pokemmo
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre