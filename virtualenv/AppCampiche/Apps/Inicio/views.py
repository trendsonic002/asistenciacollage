# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,render_to_response,get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.template import RequestContext,Context
from .models import Establecimiento,Administrador,Alumno,Curso,Persona,Direccion
from .forms import formLog,formCrearUsuario
import hashlib
import base64
import time
import calendar
import datetime
import itertools
import smtplib
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.db import connection
from django.views.generic import View
from django.template.loader import get_template
from .utils import render_to_pdf

def iniciar_sesion(request):
	if request.method == 'POST':
		formulario = formLog(request.POST)
		if formulario.is_valid:
			usuario = request.POST['usuario']
			clave = request.POST['contrasenia']
			establecimiento = request.POST['id_establecimiento']
			claveencryp = hashlib.md5(clave.encode('utf-8')).hexdigest()
			verificacion = Administrador.objects.filter(usuario=usuario,contrasenia=claveencryp,id_establecimiento=establecimiento).exists()
			if verificacion == True:
				request.session["usuario"] = usuario
				request.session["id_estable"] = establecimiento
				return HttpResponseRedirect('/privado')
			else:
				return HttpResponseRedirect('/')

	else:
		formulario = formLog()
	context = {'formulario':formulario}
	return render(request,'Inicio/index.html',context)

def estadisticas(request,id=None):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	id_administrador = id
	usuario = Administrador.objects.filter(usuario=usuario_ses,id_establecimiento=estable)
	cursor = connection.cursor()
	cursor.execute('''SELECT COUNT(id_alumno) FROM alumno INNER JOIN curso ON alumno.id_curso=curso.id_curso WHERE curso.id_administrador=%s AND curso.id_establecimiento=%s''',[id_administrador,estable])
	row = cursor.fetchall()
	cursor.execute('''SELECT COUNT(historial.id_historial) FROM historial INNER JOIN alumno ON historial.id_alumno=alumno.id_alumno INNER JOIN curso ON curso.id_curso=alumno.id_curso WHERE curso.id_administrador=%s AND historial.fecha = CURRENT_DATE AND curso.id_establecimiento=%s AND historial.estado="Presente"''',[id_administrador,estable])
	rowpresente = cursor.fetchall()
	cursor.execute('''SELECT COUNT(historial.id_historial) FROM historial INNER JOIN alumno ON historial.id_alumno=alumno.id_alumno INNER JOIN curso ON curso.id_curso=alumno.id_curso WHERE curso.id_administrador=%s AND historial.fecha = CURRENT_DATE AND curso.id_establecimiento=%s AND historial.estado="Ausente"''',[id_administrador,estable])
	rowausente = cursor.fetchall()
	return render(request,'Contenido/asistencia/estadisticas.html',{'usuario':usuario,'row':row,'rowpresente':rowpresente,'rowausente':rowausente})

def privado(request):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses,id_establecimiento=estable)
	return render(request,'Contenido/privado.html',{'usuario':usuario})

def alumnos(request):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses,id_establecimiento=estable)
	for data in usuario:
		tipo = data.tipo
		if tipo == 1:
			cursor = connection.cursor()
			cursor.execute('''SELECT alumno.estado,persona.nombre,persona.apellido_pat,persona.apellido_mat,persona.rut,curso.curso,curso.seccion,persona.id_persona FROM ALUMNO INNER JOIN PERSONA ON alumno.id_persona=persona.id_persona INNER JOIN curso ON alumno.id_curso=curso.id_curso INNER JOIN establecimiento ON curso.id_establecimiento=establecimiento.id_establecimiento WHERE establecimiento.id_establecimiento = %s''',[estable])
			row = cursor.fetchall()
			return render(request,'Contenido/alumnos/alumnos.html',{'usuario':usuario,'row':row,'tipo':tipo})
		elif tipo == 3:
			cursor = connection.cursor()
			id_admin = data.id_administrador
			cursor.execute('''SELECT alumno.estado,persona.nombre,persona.apellido_pat,persona.apellido_mat,persona.rut,curso.curso,curso.seccion,persona.id_persona,curso.id_curso FROM ALUMNO INNER JOIN PERSONA ON alumno.id_persona=persona.id_persona INNER JOIN curso ON alumno.id_curso=curso.id_curso INNER JOIN establecimiento ON curso.id_establecimiento=establecimiento.id_establecimiento WHERE establecimiento.id_establecimiento = %s AND curso.id_administrador=%s''',[estable,id_admin])
			row = cursor.fetchall()
			for data in row:
				id_curso = data[8]
			return render(request,'Contenido/alumnos/alumnos.html',{'usuario':usuario,'row':row,'tipo':tipo,'id_curso':id_curso})
		else:
			return HttpResponseRedirect('/')
	cursor.close()

def cursos(request):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses,id_establecimiento=estable)
	cursor = connection.cursor()
	cursor.execute('''SELECT curso,seccion,administrador.nombre,administrador.apellido_pat ,id_curso FROM curso INNER JOIN administrador ON curso.id_administrador=administrador.id_administrador WHERE curso.id_establecimiento =%s''',[estable])
	row = cursor.fetchall()
	return render(request,'Contenido/alumnos/cursos.html',{'usuario':usuario,'row':row})
	cursor.close()

def alumnos_curso(request, id = None):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	id_curs = id
	cursor = connection.cursor()
	cursor.execute('''SELECT persona.rut,persona.nombre,persona.apellido_pat,persona.apellido_mat,persona.id_persona FROM alumno INNER JOIN persona ON alumno.id_persona=persona.id_persona INNER JOIN curso ON alumno.id_curso=curso.id_curso INNER JOIN establecimiento ON curso.id_establecimiento=establecimiento.id_establecimiento WHERE curso.id_curso = %s AND establecimiento.id_establecimiento = %s''',[id_curs,estable])
	row1 = cursor.fetchall()
	return render(request,'Contenido/alumnos/alumnos_curso.html',{'usuario':usuario,'row1':row1})
	cursor.close()

def perfil_alumno(request,id=None):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	id_pers = id
	cursor = connection.cursor()
	cursor.execute('''SELECT persona.id_persona,persona.nombre,persona.apellido_pat,persona.apellido_mat,persona.rut,persona.dverificador,persona.sexo,persona.telefono_f,persona.telefono_m,persona.fecha_nac,persona.correo,direccion.region,direccion.ciudad,direccion.comuna,direccion.calle,direccion.numero FROM persona INNER JOIN alumno ON alumno.id_persona=persona.id_persona INNER JOIN curso ON curso.id_curso=alumno.id_curso INNER JOIN establecimiento ON establecimiento.id_establecimiento = curso.id_establecimiento INNER JOIN direccion ON direccion.id_persona=persona.id_persona WHERE establecimiento.id_establecimiento=%s AND persona.id_persona=%s''',[estable,id_pers])
	row2 = cursor.fetchall()
	return render(request,'Contenido/alumnos/perfil_alumno.html',{'usuario':usuario,'row2':row2})
	cursor.close()

def eliminar_alumno(request,id=None):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	id_pers = id
	cursor = connection.cursor()
	cursor.execute('''DELETE FROM direccion WHERE id_persona=%s''',[id_pers])
	cursor.execute('''SELECT alumno.id_alumno FROM alumno INNER JOIN persona ON alumno.id_persona=persona.id_persona WHERE persona.id_persona=%s ''',[id_pers])
	row = cursor.fetchall()
	for data in row:
		id_alum = data[0]
		cursor.execute('''DELETE FROM historial WHERE id_alumno=%s''',[id_alum])
		cursor.execute('''DELETE FROM alumno WHERE id_alumno=%s''',[id_alum])
		cursor.execute('''DELETE FROM alumno WHERE id_persona =%s''',[id_pers])
		cursor.execute('''DELETE FROM persona WHERE id_persona =%s''',[id_pers])
	return HttpResponseRedirect('/alumnos')


def editar_alumno(request,id=None):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	id_pers = id
	cursor = connection.cursor()
	cursor.execute('''SELECT persona.rut,persona.dverificador,persona.nombre,persona.apellido_pat,persona.apellido_mat,persona.sexo,persona.telefono_f,persona.telefono_m,persona.fecha_nac,
	direccion.region,direccion.comuna,direccion.ciudad,direccion.calle,direccion.numero,curso.curso,curso.seccion,persona.id_persona,persona.correo FROM persona INNER JOIN direccion 
	ON direccion.id_persona=persona.id_persona INNER JOIN alumno ON alumno.id_persona=persona.id_persona INNER JOIN curso ON curso.id_curso=alumno.id_curso inner JOIN establecimiento
	 on establecimiento.id_establecimiento=curso.id_establecimiento WHERE persona.id_persona=%s AND establecimiento.id_establecimiento=%s''',[id_pers,estable])
	row = cursor.fetchall()
	return render(request,'Contenido/alumnos/editar_alumno.html',{'usuario':usuario,'row':row})

def ingresar_usuario(request):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	return render(request,'Contenido/usuarios/ingresar_usuario.html',{'usuario':usuario})

def insertar_usuario(request):
	if request.method == 'POST':
		usuario_ses = request.session["usuario"]
		estable = request.session["id_estable"]
		usuario = Administrador.objects.filter(usuario=usuario_ses)
		nom_usuario = request.POST.get("usuario")
		nombre = request.POST.get("nombre")
		apellidos = request.POST.get("apellidos")
		contrasenia = request.POST.get("contrasenia")
		cargo = request.POST.get("cargo")
		claveencryp = hashlib.md5(contrasenia.encode('utf-8')).hexdigest()
		cursor = connection.cursor()
		row_count = cursor.execute('''SELECT usuario FROM administrador WHERE usuario=%s''',[nom_usuario])
		if row_count == 0:
			if cargo == "3":
				cursor.execute('''SELECT curso.curso,curso.seccion FROM curso WHERE curso.id_establecimiento=%s''',[estable])
				row = cursor.fetchall()
				return render(request,'Contenido/usuarios/usuario_profesor.html',{'row':row,'usuario':usuario,'nombre':nombre,'nom_usuario':nom_usuario,'apellidos':apellidos,'contrasenia':claveencryp,'cargo':cargo})
			else:
				cursor.execute('''INSERT INTO administrador(id_establecimiento,usuario,contrasenia,tipo,nombre,apellido_pat) VALUES(%s,%s,%s,%s,%s,%s)''',[estable,nom_usuario,claveencryp,cargo,nombre,apellidos])
				return render(request,'Contenido/usuarios/ingresar_usuario.html',{'usuario':usuario})
		else:
			return HttpResponseRedirect('/ingresar_usuario')
	else:
		return HttpResponseRedirect('/privado')

def insertar_usuario_profesor(request):
	if request.method == 'POST':
		usuario_ses = request.session["usuario"]
		estable = request.session["id_estable"]
		usuario = Administrador.objects.filter(usuario=usuario_ses)
		nombre = request.POST.get("nombre")
		apellidos = request.POST.get("apellidos")
		nom_usuario = request.POST.get("nom_usuario")
		contrasenia = request.POST.get("contrasenia")
		cargo = request.POST.get("cargo")
		claveencryp = hashlib.md5(contrasenia.encode('utf-8')).hexdigest()
		curso = request.POST.get("curso")
		var = curso.split(" ")
		curso = var[0]
		seccion = var[1]
		cursor = connection.cursor()
		cursor.execute('''INSERT INTO administrador(id_establecimiento,usuario,contrasenia,tipo,nombre,apellido_pat) VALUES(%s,%s,%s,%s,%s,%s)''',[estable,nom_usuario,claveencryp,cargo,nombre,apellidos])
		id_new = cursor.lastrowid
		cursor.execute('''UPDATE curso SET id_administrador = %s WHERE curso=%s AND seccion =%s ''',[id_new,curso,seccion])
		return render(request,'Contenido/usuarios/ingresar_usuario.html',{'usuario':usuario})
	else:
		return HttpResponseRedirect("/privado")

def editar_asistencia(request):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	cursor = connection.cursor()
	cursor.execute('''SELECT persona.nombre,persona.apellido_pat,persona.apellido_mat,historial.fecha,historial.hora,historial.estado,historial.id_historial FROM persona INNER JOIN alumno ON persona.id_persona=alumno.id_alumno INNER JOIN historial ON historial.id_alumno=alumno.id_alumno INNER JOIN curso ON curso.id_curso=alumno.id_curso INNER JOIN establecimiento ON curso.id_establecimiento=establecimiento.id_establecimiento  WHERE establecimiento.id_establecimiento =%s AND historial.fecha=CURRENT_DATE ''',[estable])
	row = cursor.fetchall()
	return render(request,'Contenido/asistencia/editar_asistencia.html',{'usuario':usuario,'row':row})
	cursor.close()

def asistencia_micurso(request):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	for data in usuario:
		tipo = data.tipo
		if tipo == 3:
			id_admin = data.id_administrador
			cursor = connection.cursor()
			cursor.execute('''SELECT persona.rut,persona.nombre,persona.apellido_pat,persona.apellido_mat,historial.fecha,historial.hora,historial.estado FROM historial INNER JOIN alumno ON historial.id_alumno=alumno.id_alumno INNER JOIN persona ON alumno.id_persona=persona.id_persona INNER JOIN curso ON curso.id_curso=alumno.id_curso INNER JOIN establecimiento ON establecimiento.id_establecimiento=curso.id_establecimiento WHERE establecimiento.id_establecimiento=%s AND curso.id_administrador=%s AND historial.fecha=CURRENT_DATE''',[estable,id_admin])
			row = cursor.fetchall()
			return render(request,'Contenido/asistencia/asistencia_micurso.html',{'usuario':usuario,'row':row})
		else:
			return HttpResponseRedirect('/')	
	cursor.close()

def edicion_asistencia(request,id):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	id_asistencia = id
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	cursor = connection.cursor()
	cursor.execute('''SELECT estado FROM historial WHERE id_historial=%s''',[id_asistencia])
	row = cursor.fetchall()
	for data in row:
		estado = data[0]
		if estado == 'Presente':
			cursor.execute('''UPDATE historial SET estado='Ausente' WHERE id_historial=%s''',[id_asistencia])
			return HttpResponseRedirect('/editar_asistencia')
		else:
			cursor.execute('''UPDATE historial SET estado='Presente' WHERE id_historial=%s''',[id_asistencia])
			return HttpResponseRedirect('/editar_asistencia')
	cursor.close()

def usuarios_docentes(request):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	cursor = connection.cursor()
	cursor.execute('''SELECT administrador.nombre,administrador.apellido_pat,administrador.tipo,administrador.id_administrador FROM administrador WHERE administrador.id_establecimiento=%s''',[estable])
	row = cursor.fetchall()
	return render(request,'Contenido/usuarios/usuarios_docentes.html',{'usuario':usuario,'row':row})
	cursor.close()

def edicion_alumno(request):
	if request.method == 'POST':
		usuario_ses = request.session["usuario"]
		estable = request.session["id_estable"]
		rut = request.POST.get("rut")
		dv = request.POST.get("dv")
		telefono_f = request.POST.get("telefono_f")
		nombres = request.POST.get("nombres")
		telefono_m = request.POST.get("telefono_m")
		apellido_pat= request.POST.get("apellido_pat")
		region = request.POST.get("region")
		apellido_mat = request.POST.get("apellido_mat")
		comuna = request.POST.get("comuna")
		sexo= request.POST.get("sexo")
		ciudad= request.POST.get("ciudad")
		fecha_nac = request.POST.get("fecha_nac")
		calle = request.POST.get("calle")
		curso = request.POST.get("curso")
		num_calle = request.POST.get("numero_calle")
		seccion = request.POST.get("seccion")
		correo = request.POST.get("correo")
		id_person = request.POST.get("id_perso")
		usuario = Administrador.objects.filter(usuario=usuario_ses)
		cursor = connection.cursor()
		cursor.execute('''SELECT alumno.id_alumno,curso.id_curso,direccion.id_direccion FROM alumno INNER JOIN persona ON alumno.id_persona=persona.id_persona INNER JOIN curso ON curso.id_curso=alumno.id_curso INNER JOIN establecimiento ON curso.id_establecimiento=establecimiento.id_establecimiento INNER JOIN direccion ON direccion.id_persona=persona.id_persona WHERE persona.id_persona=%s AND establecimiento.id_establecimiento=%s''',[id_person,estable])
		row = cursor.fetchall()
		for data in row:
			id_alum = data[0]
			id_curs = data[1]
			id_dire = data[2]
			cursor.execute('''UPDATE persona SET nombre=%s,apellido_pat=%s,apellido_mat=%s,sexo=%s,telefono_f=%s,telefono_m=%s  WHERE id_persona=%s''',[nombres,apellido_pat,apellido_mat,sexo,telefono_f,telefono_m,id_person])
			cursor.execute('''UPDATE curso SET curso=%s,seccion=%s WHERE id_curso=%s''',[curso,seccion,id_curs])
			cursor.execute('''UPDATE direccion SET region=%s,comuna=%s,ciudad=%s,calle=%s,numero=%s WHERE id_direccion=%s''',[region,comuna,ciudad,calle,num_calle,id_dire])
		return HttpResponseRedirect('/alumnos')
	else:
		return HttpResponseRedirect('/google.cl')
		cursor.close()


def asistencia_curso(request,id):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	id_curs = id
	cursor = connection.cursor()
	cursor.execute('''SELECT persona.rut,persona.nombre,persona.apellido_pat,persona.apellido_mat,historial.fecha,historial.hora,historial.estado,persona.dverificador FROM historial INNER JOIN alumno ON historial.id_alumno=alumno.id_alumno INNER JOIN persona ON alumno.id_persona=persona.id_persona INNER JOIN curso ON curso.id_curso=alumno.id_curso INNER JOIN establecimiento ON establecimiento.id_establecimiento=curso.id_establecimiento WHERE establecimiento.id_establecimiento=%s AND curso.id_curso=%s AND historial.fecha=CURRENT_DATE''',[estable,id_curs])
	row = cursor.fetchall()
	return render(request,'Contenido/asistencia/asistencia_curso.html',{'usuario':usuario,'row':row})
	cursor.close()

def asistencia(request):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	cursor = connection.cursor()
	cursor.execute('''SELECT curso.curso,curso.seccion,curso.id_curso,administrador.nombre,administrador.apellido_pat FROM curso INNER JOIN establecimiento ON curso.id_establecimiento=establecimiento.id_establecimiento INNER JOIN administrador ON administrador.id_administrador=curso.id_administrador  WHERE establecimiento.id_establecimiento=%s''',[estable])
	row3 = cursor.fetchall()
	return render(request,'Contenido/asistencia/asistencia.html',{'usuario':usuario,'row3':row3})
	cursor.close()

def gestionalumnos(request):
	usuario_ses = request.session["usuario"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	return render(request,'Contenido/gestionalumnos/gestionalumnos.html',{'usuario':usuario})

def usuarios(request):
	usuario_ses = request.session["usuario"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	return render(request,'Contenido/usuarios/usuarios.html',{'usuario':usuario})

def logout(request):
	del request.session["usuario"]
	del request.session['id_estable']
	return HttpResponseRedirect('/')

def nuevo_administrador(request):
	if request.method=='POST':
		formulario = formCrearUsuario(request.POST)
		if formulario.is_valid:
			id_estable = request.session['id_estable']
			usuario = request.POST['usuario']
			clave = request.POST['contrasenia']
			tipo = request.POST['tipo']
			claveencryp = hashlib.md5(clave.encode('utf-8')).hexdigest()
			cs = Administrador()
			cs.id_establecimiento = Establecimiento.objects.get(id_establecimiento=id_estable)
			cs.usuario = usuario
			cs.contrasenia = claveencryp
			cs.tipo = tipo
			cs.save()
			return HttpResponseRedirect('www.youtube.com')
		else:
			formulario = HttpResponseRedirect('/usuario/nuevo')
	else:
		formulario = formCrearUsuario()
	context = {'formulario':formulario}
	return render(request,'Usuario/nuevo_admin.html',context)

def enviar_correos(request):
	usuario_ses = request.session["usuario"]
	estable = request.session["id_estable"]
	usuario = Administrador.objects.filter(usuario=usuario_ses)
	cursor = connection.cursor()
	cursor.execute('''SELECT persona.correo FROM persona INNER JOIN alumno ON persona.id_persona=alumno.id_persona INNER JOIN curso ON curso.id_curso=alumno.id_curso INNER JOIN establecimiento ON curso.id_establecimiento=establecimiento.id_establecimiento INNER JOIN historial ON historial.id_alumno=alumno.id_alumno WHERE establecimiento.id_establecimiento=%s AND historial.estado='Ausente' AND historial.fecha=CURRENT_DATE''',[estable])
	row = cursor.fetchall()
	for correo in row:
		content = 'Su hijo no asistio a clases, si usted no es conciente de la inasistencia, porfavor comunicarse con la institución'
		mail = smtplib.SMTP('smtp.gmail.com',587)
		mail.starttls()
		mail.login('hiimRaest.22@gmail.com','hiimRaestyn123')
		mail.sendmail(correo[0],correo,content)
		mail.close
	return HttpResponseRedirect('/asistencia')

class GeneratePDF_curso(View):
	def get(self,request,*args,**kwargs):
		template = get_template('Contenido/alumnos/generarpdf_curso.html')
		estable = request.session["id_estable"]
		id_curso = self.kwargs['id']
		cursor = connection.cursor()
		cursor.execute('''SELECT curso.curso,curso.seccion,persona.rut,persona.dverificador,persona.nombre,persona.apellido_pat,persona.apellido_mat,persona.id_persona,administrador.nombre,administrador.apellido_pat FROM alumno INNER JOIN persona ON alumno.id_persona=persona.id_persona INNER JOIN curso ON alumno.id_curso=curso.id_curso INNER JOIN establecimiento ON curso.id_establecimiento=establecimiento.id_establecimiento INNER JOIN administrador ON curso.id_administrador=administrador.id_administrador WHERE curso.id_curso = %s AND establecimiento.id_establecimiento = %s''',[id_curso,estable])
		row = cursor.fetchall()
		for datos in row:
			curso = datos[0].capitalize()
			seccion = datos[1].capitalize()
			nombre = datos[8].capitalize()
			apellido = datos[9].capitalize()
			curso_total = curso+" "+seccion
			nom_total = nombre+" "+apellido
			context = {'row':row, 'curso_total':curso_total,'nom_total':nom_total}
			html = template.render(context)
			pdf = render_to_pdf('Contenido/alumnos/generarpdf_curso.html',context)
			return HttpResponse(pdf,content_type="application/pdf")

class GeneratePDF(View):
	def get(self,request,*args,**kwargs):
		template = get_template('Contenido/alumnos/generarpdf.html')
		estable = request.session["id_estable"]
		id_curso = self.kwargs['id']
		cursor = connection.cursor()
		cursor.execute('''SELECT curso.curso,curso.seccion,persona.rut,persona.dverificador,persona.nombre,persona.apellido_pat,persona.apellido_mat,persona.id_persona,administrador.nombre,administrador.apellido_pat FROM alumno INNER JOIN persona ON alumno.id_persona=persona.id_persona INNER JOIN curso ON alumno.id_curso=curso.id_curso INNER JOIN establecimiento ON curso.id_establecimiento=establecimiento.id_establecimiento INNER JOIN administrador ON curso.id_administrador=administrador.id_administrador WHERE curso.id_curso = %s AND establecimiento.id_establecimiento = %s''',[id_curso,estable])
		row = cursor.fetchall()
		for datos in row:
			curso = datos[0].capitalize()
			seccion = datos[1].capitalize()
			nombre = datos[8].capitalize()
			apellido = datos[9].capitalize()
			curso_total = curso+" "+seccion
			nom_total = nombre+" "+apellido
			context = {'row':row, 'curso_total':curso_total,'nom_total':nom_total}
			html = template.render(context)
			pdf = render_to_pdf('Contenido/alumnos/generarpdf.html',context)
			return HttpResponse(pdf,content_type="application/pdf")

class GeneratePDF_asistencia(View):
	def get(self,request,*args,**kwargs):
		template = get_template('Contenido/asistencia/generarpdf.html')
		estable = request.session["id_estable"]
		id_curso = self.kwargs['id']
		mes =  time.strftime("%m")
		mes_nom =  time.strftime("%B")
		now = datetime.datetime.now()
		dias_mes = calendar.monthrange(now.year, now.month)[1]
		loop_times = range(1, dias_mes)
		alum_array = []
		cursor = connection.cursor()
		cursor.execute('''SELECT administrador.nombre,administrador.apellido_pat,curso.curso,curso.seccion FROM curso INNER JOIN administrador ON curso.id_administrador=administrador.id_administrador  WHERE curso.id_establecimiento=%s AND curso.id_curso=%s''',[estable,id_curso])
		row_profesor = cursor.fetchall()
		for profesor in row_profesor:
			nombre_adm = profesor[0].capitalize()
			apellido_adm = profesor[1].capitalize()
			curso_adm = profesor[2].capitalize()
			seccion_adm = profesor[3].capitalize()
			nom_total = nombre_adm+" "+apellido_adm
			curso_total = curso_adm+" "+seccion_adm
		cursor.execute('''SELECT DISTINCT persona.nombre,persona.apellido_pat,persona.apellido_mat,historial.id_alumno FROM persona INNER JOIN alumno ON alumno.id_persona=persona.id_persona INNER JOIN historial ON historial.id_alumno=alumno.id_alumno INNER JOIN curso ON curso.id_curso=alumno.id_curso WHERE curso.id_establecimiento=%s''',[estable])
		row_ids = cursor.fetchall()
		for ides in row_ids:
			id_alum = ides[3]
			cursor.execute('''SELECT historial.fecha FROM historial WHERE historial.id_alumno =%s AND EXTRACT(MONTH FROM historial.fecha)=%s''',[id_alum,mes])
			row_fechas = cursor.fetchall()
		context = {'row_fechas':row_fechas,'loop_times':loop_times,'mes_nom':mes_nom,'nom_total':nom_total,'curso_total':curso_total}
		html = template.render(context)
		pdf = render_to_pdf('Contenido/asistencia/generarpdf.html',context)
		return HttpResponse(pdf,content_type='application/pdf')
