from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Jugador, Combate, Temporada

class JugadorAdmin(admin.ModelAdmin):
    list_display = ('mostrar_avatar', 'nickname_pokemmo', 'puntuacion', 'rango')
    actions = ['reiniciar_puntuaciones_masivo']

    def mostrar_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 50%;" />', obj.avatar.url)
        return "Sin foto"

    def reiniciar_puntuaciones_masivo(self, request, queryset):
        queryset.update(puntuacion=500, rango='Bronce', victorias=0, derrotas=0)
        self.message_user(request, "Jugadores reiniciados.", messages.SUCCESS)
    reiniciar_puntuaciones_masivo.short_description = "Reiniciar PTS y Rango"

admin.site.register(Jugador, JugadorAdmin)
admin.site.register(Combate)
admin.site.register(Temporada)