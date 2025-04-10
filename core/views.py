from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseForbidden
from django.db import IntegrityError
from uuid import UUID
from django.contrib.auth import login as auth_login
from django.db.models import Q

from .models import Pelada, Presenca, Jogador
from .forms import PeladaForm

def home(request):
    return render(request, 'core/home.html')

def get_user_pelada_or_403(request, pk):
    jogador = get_object_or_404(Jogador, usuario=request.user)
    pelada = get_object_or_404(Pelada, pk=pk)
    if not pelada.jogadores.filter(id=jogador.id).exists():
        return HttpResponseForbidden("Você não participa desta pelada.")
    return pelada

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                Jogador.objects.create(nome=user.username, email=user.email, usuario=user)
                login(request, user)
                messages.success(request, 'Conta criada com sucesso.')
                return redirect('home')
            except IntegrityError:
                messages.error(request, 'Já existe um jogador com esse e-mail.')
        else:
            messages.error(request, 'Por favor, verifique os dados fornecidos.')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def lista_peladas(request):
    try:
        jogador = Jogador.objects.get(usuario=request.user)
    except Jogador.DoesNotExist:
        jogador_existente = Jogador.objects.filter(email=request.user.email).first()
        if jogador_existente:
            jogador_existente.usuario = request.user
            jogador_existente.save()
            jogador = jogador_existente
        else:
            jogador = Jogador.objects.create(
                usuario=request.user,
                nome=request.user.username,
                email=request.user.email
            )

    peladas = Pelada.objects.filter(jogadores=jogador).distinct()
    return render(request, 'core/lista_peladas.html', {'peladas': peladas})

@login_required
def criar_pelada(request):
    if request.method == 'POST':
        form = PeladaForm(request.POST)
        if form.is_valid():
            pelada = form.save(commit=False)
            pelada.organizador = request.user
            pelada.save()

            jogador = Jogador.objects.get(usuario=request.user)

            # Cria a relação manualmente via Presenca
            Presenca.objects.create(pelada=pelada, jogador=jogador, confirmado=False)

            return redirect('detalhes_pelada', pk=pelada.pk)
    else:
        form = PeladaForm()
    return render(request, 'core/pelada_form.html', {'form': form})


@login_required
def editar_pelada(request, pk):
    pelada = get_object_or_404(Pelada, pk=pk)
    if pelada.organizador != request.user:
        return HttpResponseForbidden("Você não tem permissão para editar essa pelada.")
    if request.method == 'POST':
        form = PeladaForm(request.POST, instance=pelada)
        if form.is_valid():
            form.save()
            return redirect('detalhes_pelada', pk=pelada.pk)
    else:
        form = PeladaForm(instance=pelada)
    return render(request, 'core/pelada_form.html', {'form': form})

@login_required
def deletar_pelada(request, pk):
    pelada = get_object_or_404(Pelada, pk=pk)
    if pelada.organizador != request.user:
        return HttpResponseForbidden("Você não tem permissão para deletar essa pelada.")
    if request.method == 'POST':
        pelada.delete()
        return redirect('lista_peladas')
    return redirect('detalhes_pelada', pk=pk)

@login_required
def detalhes_pelada(request, pk):
    jogador = get_object_or_404(Jogador, usuario=request.user)
    pelada = get_object_or_404(Pelada, pk=pk)
    if not pelada.jogadores.filter(id=jogador.id).exists():
        return HttpResponseForbidden("Você não participa desta pelada.")
    return render(request, 'core/detalhes_pelada.html', {'pelada': pelada})

@login_required
def confirmar_presenca(request, pk):
    pelada = get_object_or_404(Pelada, pk=pk)
    jogador = get_object_or_404(Jogador, usuario=request.user)
    if not pelada.jogadores.filter(id=jogador.id).exists():
        return HttpResponseForbidden("Você não participa desta pelada.")
    Presenca.objects.update_or_create(
        pelada=pelada,
        jogador=jogador,
        defaults={'confirmado': True}
    )
    messages.success(request, "Presença confirmada!")
    return redirect('detalhes_pelada', pk=pk)

@login_required
def entrar_com_codigo(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        try:
            uuid_codigo = UUID(codigo.strip())
            pelada = get_object_or_404(Pelada, codigo_acesso=uuid_codigo)
            jogador = get_object_or_404(Jogador, usuario=request.user)

            pelada.jogadores.add(jogador)
            messages.success(request, f"Você entrou na pelada '{pelada.nome}'!")
            return redirect('detalhes_pelada', pk=pelada.pk)
        except (ValueError, Pelada.DoesNotExist):
            messages.error(request, "Código inválido ou pelada não encontrada.")
    return render(request, 'core/entrar_com_codigo.html')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email ou senha inválidos.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
