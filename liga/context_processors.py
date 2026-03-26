from django.db.models import Q
from .models import Combate

def alertas_duelos(request):
    alertas = 0
    # Si el usuario inició sesión y tiene un jugador creado
    if request.user.is_authenticated and hasattr(request.user, 'jugador'):
        jugador = request.user.jugador
        
        # 1. Retos que le enviaron y aún no acepta
        pendientes = Combate.objects.filter(oponente=jugador, estado='PENDIENTE').count()
        
        # 2. Resultados que reportó el rival y que él debe confirmar
        por_confirmar = Combate.objects.filter(
            Q(retador=jugador) | Q(oponente=jugador),
            estado='ESPERANDO'
        ).exclude(reportado_por=jugador).count()
        
        # Sumamos ambos para el globito rojo
        alertas = pendientes + por_confirmar
        
    return {'num_alertas': alertas}