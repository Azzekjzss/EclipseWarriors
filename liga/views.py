from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
import requests

from .models import Jugador, Combate, Temporada
from .forms import JugadorPerfilForm

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1486548179594903673/OWbINfncud8TRopUZG-BrzBe6eoF93PmHsZDmcXoyZx9T1vg1kc9GbVsGXflMvh5irRS"

def ranking(request):
    query = request.GET.get('q')
    if query:
        jugadores_lista = Jugador.objects.filter(nickname_pokemmo__icontains=query).order_by('-puntuacion')
    else:
        jugadores_lista = Jugador.objects.all().order_by('-puntuacion')
    
    paginator = Paginator(jugadores_lista, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'liga/ranking.html', {'page_obj': page_obj, 'query': query})

@login_required
def retar(request, oponente_id):
    oponente = get_object_or_404(Jugador, id=oponente_id)
    retador = request.user.jugador

    # Evitar que se reten a sí mismos o que haya duelos duplicados pendientes
    if oponente != retador:
        Combate.objects.get_or_create(
            retador=retador,
            oponente=oponente,
            estado='PENDIENTE'
        )
        messages.success(request, f"¡Has desafiado a {oponente.nickname_pokemmo}! Espera a que acepte.")
    
    return redirect('ranking')
@login_required
def mis_combates(request):
    jugador = request.user.jugador
    # Obtenemos combates donde el jugador participa y no están finalizados ni rechazados
    combates = Combate.objects.filter(
        Q(retador=jugador) | Q(oponente=jugador)
    ).exclude(estado__in=['FINALIZADO', 'RECHAZADO']).order_by('-fecha_creacion')
    return render(request, 'liga/mis_combates.html', {'combates': combates})

@login_required
def gestionar_combate(request, combate_id, accion):
    combate = get_object_or_404(Combate, id=combate_id)
    jugador = request.user.jugador

    # Validar que el jugador sea parte del combate
    if combate.retador != jugador and combate.oponente != jugador:
        return redirect('mis_combates')

    if accion == "aceptar" and combate.oponente == jugador:
        combate.estado = 'ACEPTADO'
        messages.success(request, "¡Desafío aceptado! ¡A combatir!")
    
    elif accion == "rechazar" and combate.oponente == jugador:
        combate.estado = 'RECHAZADO'
        messages.warning(request, "Has rechazado el desafío.")
    
    elif accion == "gane" and combate.estado == 'ACEPTADO':
        combate.estado = 'ESPERANDO'
        combate.reportado_por = jugador
        combate.ganador = jugador
        messages.info(request, "Resultado enviado. Esperando que tu rival confirme.")

    elif accion == "confirmar" and combate.estado == 'ESPERANDO':
        # Solo el jugador que NO reportó el resultado puede confirmar
        if combate.reportado_por != jugador:
            ganador = combate.ganador
            perdedor = combate.retador if ganador == combate.oponente else combate.oponente
            
            # Reparto de puntos
            ganador.puntuacion += 25
            perdedor.puntuacion -= 15
            ganador.victorias += 1
            perdedor.derrotas += 1
            ganador.save()
            perdedor.save()
            
            combate.estado = 'FINALIZADO'
            combate.fecha_finalizacion = timezone.now()
            
            # Webhook Discord
            if DISCORD_WEBHOOK_URL:
                try:
                    payload = {"content": f"⚔️ **{ganador.nickname_pokemmo}** venció a **{perdedor.nickname_pokemmo}** en la Liga Eclipse Warriors!"}
                    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
                except: pass

            messages.success(request, f"¡Combate finalizado! Ganador: {ganador.nickname_pokemmo}")
        else:
            messages.warning(request, "Ya has reportado tu victoria. Espera la confirmación de tu rival.")

    combate.save()
    return redirect('mis_combates')

def historial_combates(request):
    lista_de_duelos = Combate.objects.filter(estado='FINALIZADO').order_by('-fecha_finalizacion')
    
    return render(request, 'liga/historial.html', {
        'combates': lista_de_duelos  
    })

def public_perfil(request, jugador_id):
    perfil = get_object_or_404(Jugador, id=jugador_id)
    
    # Obtenemos sus últimos 5 combates finalizados
    historial = Combate.objects.filter(
        (Q(retador=perfil) | Q(oponente=perfil)),
        estado='FINALIZADO'
    ).order_by('-fecha_finalizacion')[:5]
    
    # Contamos cuántas veces ha quedado en el podio (opcional para los logros)
    logros = {
        'oro': Temporada.objects.filter(puesto_1=perfil.nickname_pokemmo).count(),
        'plata': Temporada.objects.filter(puesto_2=perfil.nickname_pokemmo).count(),
        'bronce': Temporada.objects.filter(puesto_3=perfil.nickname_pokemmo).count(),
    }

    return render(request, 'liga/public_perfil.html', {
        'perfil': perfil,
        'historial': historial,
        'logros': logros
    })

def salon_fama(request):
    temporadas = Temporada.objects.all().order_by('-numero')
    return render(request, 'liga/salon_fama.html', {'temporadas': temporadas})

@login_required
def editar_perfil(request):
    # BUSCA el jugador; si no existe, lo CREA automáticamente para evitar el error
    jugador, created = Jugador.objects.get_or_create(
        usuario=request.user,
        defaults={'nickname_pokemmo': request.user.username}
    )

    if request.method == 'POST':
        form = JugadorPerfilForm(request.POST, request.FILES, instance=jugador)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Perfil actualizado con éxito!")
            return redirect('ranking')
    else:
        form = JugadorPerfilForm(instance=jugador)
    
    return render(request, 'liga/editar_perfil.html', {'form': form})


# Asegúrate de que tu vista de registro siga creando el jugador automáticamente:
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            # Esto crea el Jugador vinculado al Usuario recién creado
            Jugador.objects.create(usuario=usuario, nickname_pokemmo=usuario.username)
            login(request, usuario)
            return redirect('ranking')
    else:
        form = UserCreationForm()
    return render(request, 'liga/registro.html', {'form': form})