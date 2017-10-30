from django.conf.urls import url,include
from django.contrib import admin
from Apps.Inicio.views import iniciar_sesion,GeneratePDF_curso,insertar_usuario_profesor,insertar_usuario,GeneratePDF_asistencia,ingresar_usuario,GeneratePDF,usuarios_docentes,estadisticas,edicion_asistencia,editar_asistencia,asistencia_micurso,edicion_alumno,enviar_correos,asistencia_curso,editar_alumno,eliminar_alumno,privado,perfil_alumno,alumnos_curso,nuevo_administrador,logout,alumnos,usuarios,gestionalumnos,cursos,asistencia

urlpatterns = [
    url(r'^$',iniciar_sesion,name='iniciar_sesion'),
    url(r'^privado$',privado,name='privado'),
    url(r'^usuario/nuevo$',nuevo_administrador,name='nuevo_administrador'),
    url(r'^logout$',logout,name='logout'),
    url(r'^alumnos$',alumnos,name='alumnos'),
    url(r'^asistencia$',asistencia,name='asistencia'),
    url(r'^gestionalumnos$',gestionalumnos,name='gestionalumnos'),
    url(r'^cursos$',cursos,name='cursos'),
    url(r'^alumnos_curso/(?P<id>\d+)/$',alumnos_curso,name='alumnos_curso'),
    url(r'^perfil_alumno/(?P<id>\d+)/$',perfil_alumno,name='perfil_alumno'),
    url(r'^asistencia_curso/(?P<id>\d+)/$',asistencia_curso,name='asistencia_curso'),
    url(r'^eliminar_alumno/(?P<id>\d+)/$',eliminar_alumno,name='eliminar_alumno'),
    url(r'^editar_alumno/(?P<id>\d+)/$',editar_alumno,name='editar_alumno'),
    url(r'^edicion_alumno$',edicion_alumno,name='edicion_alumno'),
    url(r'^enviar_correos$',enviar_correos,name='enviar_correos'),
    url(r'^asistencia_micurso$',asistencia_micurso,name='asistencia_micurso'),
    url(r'^editar_asistencia',editar_asistencia,name='editar_asistencia'),
    url(r'^edicion_asistencia/(?P<id>\d+)/$',edicion_asistencia,name='edicion_asistencia'),
    url(r'^usuarios_docentes$',usuarios_docentes,name='usuarios_docentes'),
    url(r'^estadisticas/(?P<id>\d+)/$',estadisticas,name='estadisticas'),
    url(r'^ingresar_usuario$',ingresar_usuario,name='ingresar_usuario'),
    url(r'^GeneratePDF/(?P<id>\d+)/$',GeneratePDF.as_view()),
    url(r'^GeneratePDF_asistencia/(?P<id>\d+)/$',GeneratePDF_asistencia.as_view()),
    url(r'^insertar_usuario$',insertar_usuario,name='insertar_usuario'),
    url(r'^insertar_usuario_profesor$',insertar_usuario_profesor,name='insertar_usuario_profesor'),
    url(r'^GeneratePDF_curso/(?P<id>\d+)/$',GeneratePDF_curso.as_view()),
    
    
]