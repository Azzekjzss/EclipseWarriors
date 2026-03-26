from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Jugador, Batalla, Temporada

# --- CONFIGURACIÓN DEL PANEL DE JUGADORES ---
class JugadorAdmin(admin.ModelAdmin):
    # Columnas que se ven en la lista principal
    list_display = ('mostrar_avatar', 'nickname_pokemmo', 'puntuacion', 'rango', 'mostrar_record', 'winrate_link')
    
    # Permitir editar el rango directamente desde la lista sin entrar al perfil
    list_editable = ('rango',)
    
    # Buscador y filtros laterales
    search_fields = ('nickname_pokemmo', 'lema')
    list_filter = ('rango', 'equipo')
    
    # ACCIONES MASIVAS: Solo dejamos la de reiniciar puntos
    actions = ['reiniciar_puntuaciones_masivo']

    # 1. Función para mostrar la foto circular en el Admin
    def mostrar_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid #ddd;" />', obj.avatar.url)
        return format_html('<div style="width: 40px; height: 40px; border-radius: 50%; background: #eee; display: flex; align-items: center; justify-content: center;"><i class="fas fa-user text-muted"></i></div>')
    mostrar_avatar.short_description = 'Avatar'

    # 2. Función para mostrar victorias y derrotas con colores
    def mostrar_record(self, obj):
        return format_html('<b style="color: #28a745;">{}V</b> - <b style="color: #dc3545;">{}D</b>', obj.victorias, obj.derrotas)
    mostrar_record.short_description = 'Récord'

    # 3. Cálculo rápido de Winrate
    def winrate_link(self, obj):
        total = obj.victorias + obj.derrotas
        if total > 0:
            porcentaje = (obj.victorias / total) * 100
            return f"{porcentaje:.1f}%"
        return "0%"
    winrate_link.short_description = 'Winrate'

    # --- ACCIÓN PARA REINICIAR TEMPORADA ---
    def reiniciar_puntuaciones_masivo(self, request, queryset):
        """
        Reinicia los puntos a 500 y el rango a Bronce de los jugadores seleccionados.
        """
        filas_actualizadas = queryset.update(puntuacion=500, rango='Bronce', victorias=0, derrotas=0)
        self.message_user(request, f"¡Éxito! Se han reseteado {filas_actualizadas} jugadores.", messages.SUCCESS)
    reiniciar_puntuaciones_masivo.short_description = "Reiniciar PTS, Rango y Récord (Seleccionados)"

# --- CONFIGURACIÓN DEL PANEL DE BATALLAS ---
class BatallaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'ganador', 'fecha_finalizacion', 'estado')
    list_filter = ('estado', 'fecha_finalizacion')
    search_fields = ('retador__nickname_pokemmo', 'oponente__nickname_pokemmo')

# --- CONFIGURACIÓN DEL PANEL DE TEMPORADAS ---
class TemporadaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'puesto_1')
    readonly_fields = ('fecha_inicio',) # La fecha de inicio suele ser automática

# --- REGISTRO DE MODELOS ---
admin.site.register(Jugador, JugadorAdmin)
admin.site.register(Batalla, BatallaAdmin)
admin.site.register(Temporada, TemporadaAdmin)