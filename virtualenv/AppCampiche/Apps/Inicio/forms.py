# -*- coding: utf-8 -*-
from django import forms
from .models import Establecimiento,Administrador

class formLog(forms.ModelForm):
	contrasenia = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Contraseña','required':'required'}))
	usuario = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Usuario','required':'required'}))
	id_establecimiento = forms.ModelChoiceField(widget=forms.Select(attrs={'class':"form-control",'required':'required'}),queryset=Establecimiento.objects.all())
	class Meta:
		model = Administrador
		fields = ['usuario','contrasenia','id_establecimiento']

class formCrearUsuario(forms.ModelForm):
	class Meta:
		model = Administrador
		fields = ['usuario','contrasenia','tipo']