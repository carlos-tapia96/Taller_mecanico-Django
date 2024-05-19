import csv
import smtplib
import datetime
import os, os.path
from threading import Thread

import docx
import pandas
import docx2pdf
#import rut_chile
from .models import *
from django.apps import apps
from django.http import HttpResponse
from django.http import FileResponse
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.template.defaultfilters import date
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import get_language, activate
from django.contrib.auth import login as iniciarSesion, logout, authenticate

from Taller.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

# Función anónima para validar que sólo se ingresen números.
only_numbers = lambda texto: ''.join([numero if numero in ['0','1','2','3','4','5','6','7','8','9'] else '' for numero in texto])

def to_index(request):
    """Redirección hacia index"""
    return redirect('index')

def login(request):
    """Módulo que permite al usuario registrarse e/o iniciar sesión."""    

    # Si el usuario ya está loggeado,
    # Se redirecciona al index.
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        # Se rescatan los campos de usuario y contraseña.
        only_numbers = lambda texto: ''.join([numero if numero in ['0','1','2','3','4','5','6','7','8','9'] else '' for numero in texto])
        usuario = only_numbers(request.POST['username'])
        contra = request.POST['password']

        # Se verifica que las crenciales sean válidas.
        usuarioLogeado = authenticate(username = usuario, password = contra)

        # Debiera devolver una instancia de sesión.
        # De lo contrario, devuelve 'None'.
        if usuarioLogeado is not None:

            # La función login() iniciará la sesión.
            iniciarSesion(request, usuarioLogeado)

            # Si la autenticación es correcta, 
            # entonces la plantilla se renderizará
            # como un usuario válidamente autenticado.
            return redirect('index')
        
        # Si la autenticación falla, 
        # la sesión NO existirá.
        else:
            # Se verifica que exista el nombre de usuario en la base de datos.
            if len(User.objects.filter(username=usuario)):
                # Si existe, se le informa al usuario que la contraseña es incorrecta.
                return render(request, 'mantenedor/login.html', {'errores':'CONTRASEÑA_INCORRECTA'})
            else:
                # Si no existe, se le informa al usuario que el nombre de usuario no existe.
                return render(request, 'mantenedor/login.html', {'errores':'NO_EXISTE_NOMBRE_USUARIO'})

    # Página de inicio de sesión.
    return render(request, 'mantenedor/login.html')

def registro (request):
    formulario = None
    if request.method == 'POST':
        formulario = FormularioRegistro(data = request.POST)
        # try:
        #     if not rut_chile.is_valid_rut(formulario['username']):
        #         return render(request, 'Mantenedor/registro.html', {formulario:formulario, 'errores':'rut mal ingresado'})
        # except ValueError:
        #     return render(request, 'Mantenedor/registro.html', {formulario:formulario, 'errores':'rut mal ingresado'})
        if formulario.is_valid():
            usuario_guardado = formulario.save()
            if usuario_guardado is not None:
                iniciarSesion(request,usuario_guardado)
                context = {'perfil':
                            {'nivel':'admin'},
                            'level':'admin'
                            }
                return render(request, 'TEMPORAL/perfil.html', context)                
    else:
        formulario = FormularioRegistro()

    context = {'formulario': formulario}
    return render(request, 'TEMPORAL/registro.html', context)

def perfil(request):
    return render(
        request,
        'TEMPORAL/perfil.html'
    )

def salir(request):
    logout(request)
    return redirect('index')

def obtener_usuario(request):
    nivel = None
    if request.user.is_authenticated:
        try:
            nivel = Perfil.objects.filter(id_auth_user = request.user.id)[0].nivel
        except IndexError:
            logout(request)
            nivel = 'ERROR'
    return {'perfil':{'nivel':nivel}}

def index (request):
    context = obtener_usuario(request)
    return render (request, 'mantenedor/index.html',context)


def registro_cliente (request):
    formulario = FormularioRegistro()
    context = dict()
    permitir_sesion = False
    if request.method == 'POST':
        formulario = FormularioRegistro(data = request.POST)
        if formulario.is_valid():
            usuario_guardado = formulario.save()
            if usuario_guardado is not None:
                permitir_sesion = True
        else:
            context['formulario'] = formulario
            return render (request, 'mantenedor/registro_cliente.html',context)

        dato_or_zero = lambda dato_crudo: 0 if not dato_crudo else dato_crudo
        only_numbers = lambda texto: ''.join([numero if numero in ['0','1','2','3','4','5','6','7','8','9'] else '' for numero in texto])

        mi_ci = only_numbers(formulario.cleaned_data['username'])
        mi_nombre = request.POST['first_name']
        mi_apellido = request.POST['last_name']
        mi_direccion = request.POST['direccion']
        mi_telefono = dato_or_zero(request.POST['telefono'])
        mi_email = request.POST['email']

        id_user_auth = User.objects.get(username=only_numbers(formulario.cleaned_data['username'])).id
        id_cliente = Cliente.objects.count()+1
        cliente = Cliente(id_cliente,mi_nombre,mi_apellido,mi_direccion,
                            mi_telefono,mi_email,mi_ci)

        n_perfil = Perfil.objects.all().count()+1
        perfil = Perfil(n_perfil,id_user_auth, id_cliente,'CLIENTE')
        perfil.save()

        cliente.save()
        if permitir_sesion:
            iniciarSesion(request,usuario_guardado)
            nivel = Perfil.objects.filter(id_auth_user = request.user.id)[0].nivel
        return render(request, 'Mantenedor/index.html', {'perfil':{'nivel':nivel}})
    context['formulario'] = formulario
    return render (request, 'mantenedor/registro_cliente.html',context)

def ver_perfil(request):
    id_cliente = Perfil.objects.filter(id_auth_user = request.user.id)[0].id_usuario
    ci = User.objects.filter(id = request.user.id)[0].username

    cliente = Cliente.objects.get(id_cliente=id_cliente)
    context = {'cliente':cliente}

    if request.method =='POST':
        only_numbers = lambda texto: ''.join([numero if numero in ['0','1','2','3','4','5','6','7','8','9'] else '' for numero in texto])

        mi_nombre = request.POST['nombre']
        mi_apellido = request.POST['apellido']
        mi_direccion = request.POST['direccion']
        mi_telefono = request.POST['telefono']
        mi_email = request.POST['email']

        cliente = Cliente

        cliente.id_cliente

        cliente.nombre = mi_nombre
        cliente.apellido = mi_apellido
        cliente.direccion = mi_direccion
        cliente.telefono = mi_telefono
        cliente.email = mi_email

        cliente = Cliente(id_cliente, mi_nombre, mi_apellido,mi_direccion, mi_telefono, mi_email, ci)

        cliente.save()

        a = User.objects.get(username=ci)
        a.first_name = mi_nombre
        a.last_name = mi_apellido
        a.email = mi_email
        a.save()

        context = {'cliente':cliente}

        return render (request, 'contenedor/ver_perfil.html', context)

    return render(request, 'contenedor/ver_perfil.html', context)

def servicios (request):
    servicios = TipoServicio.objects.all()
    context = {'servicios': servicios}

    return render (request, 'contenedor/servicios.html', context)

def reservas (request):
    if not (request.user.is_authenticated):
        return HttpResponse('Debes estar logeado!')
    cliente = dict()
    cliente['nombre'] = f'{request.user.firts_name} {request.user.last_name}'
    cliente['correo'] = f'{request.user.email}'
    vehiculo = dict()
    solicitud = ''
    servicios_disponibles = dict()
    for index,item in enumerate(TipoServicio.objects.all()):
        servicios_disponibles[f'servicio_{index+1}'] = item.nombre

    servicios = TipoServicio.objects.all()
    context = {'servicios':servicios}
    context['years'] = range(2010, 2022)
    if request.method == 'POST':
        context['method'] = 'POST'
        vehiculo['marca'] = request.POST['marca']
        vehiculo['modelo'] = request.POST['modelo']
        vehiculo['year'] = request.POST['year']

        id_cliente = Perfil.objects.filter(id_auth_user = request.user.id)[0].id_usuario
        id_reserva = Reservas.objects.count()+1
        reservas = Reservas(id_reserva,
                            id_cliente,
                            vehiculo['marca'],
                            vehiculo['modelo'],
                            vehiculo['year'],
                            datetime.datetime.now(),
                            0)
        reservas.save()

        services = list()
        for service in request.POST:
            if 'servicio' in service:
                services.append(servicios_disponibles[service])
                id_servicio = service.replace('servicio_','')
                id_detalle = DetalleSer.objects.count()+1
                detalle = DetalleSer(id_detalle, id_reserva, id_servicio)
                detalle.save()
        solicitud = '\n'.join(services)

        tupla_datos = (cliente,vehiculo, solicitud)
        al_recepcionista = Thread(target=enviar_correo, args=(tupla_datos,))
        al_recepcionista.start()
        return render (request, 'contenedor/reservas.html', context)
    return render (request, 'contenedor/reservas.html', context)

def modificar_reserva(request, id_reserva, id_mecanico, confirmacion):
    if confirmacion not in [0,1]:
        return HttpResponse(status=403)
    try: reserva = Reservas.objects.get(id_reserva = id_reserva)
    except: return HttpResponse('No se encuentra la reserva', status=403)
    reserva.save()
    ot = Ot.objects.filter(reservas_id_reserva_id = id_reserva)
    if ot.count () == 0:
        id_ot = Ot.objects.count() + 1
        ot = Ot(id_ot, id_mecanico, id_reserva, datetime.datetime.now())
        ot.save()
    else:
        ot = Ot.objects.get(reservas_id_reserva = id_reserva)
        ot.delete()
    return HttpResponse(status=200)

def eliminar_reserva(request, id_reserva):
    if not len(Reservas.objects.filter(id_reserva = id_reserva)):
        return HttpResponse('Backend: No existe reserva.', status= 404)
    reserva = Reservas.objects.filter(id_reserva=id_reserva)[0]
    reserva.delete()
    return HttpResponse('BackEnd: !Reserva y sus detalles de servicios borrados!' status=200)

def ver_reservas(request):
    reservas = Reservas.objects.all().order_by('-id_reserva')
    mecanicos = Empleado.objects.filter(cargo_id_tipo_cargo=2)
    context = {'reservas': reservas,
               'mecanicos': mecanicos}
    return render (request, 'mantener/ver_reservas.html',context)

def pago(request):
    context = dict()
    context['pagos'] = Pago.objects.all().order_by('-id_pago')
    return render (request, 'mantenedor/pago.html',context)

def eliminar_pago(request, id_pago):
    # Determinar si existe un pago asociado a la ID en cuestion.
    try: el_pago = Pago.objects.get(id_pago=id_pago)
    except: return HttpResponse('No existe pago asociado.', status=404)

    el_pago.delete()
    return HttpResponse('Pago eliminado', status=200)

def orden_trabajo(request):
    context = dict()

    ot = Ot.objects.all()
    context['ot'] = ot

    detalles = DetalleSer.objects.all()
    context['detalles'] = detalles

    reservas = Reservas.objects.filter(confirmacion='1')
    context['reservas'] = reservas

    servicios = TipoServicio.objects.all()
    context['servicios'] = servicios

    return render(request, 'contenedor/orden_trabajo.html', context)

def consultar_fecha_pedido(request, id_pedido):
    coincidencia = Op.objects.filter(id_pedido=id_pedido)
    if coincidencia:
        return HttpResponse(coincidencia[0].fecha_pedido, status=200)
    return HttpResponse(f'No hay coincidencia para {id_pedido}', status= 404)

def consultar_fecha_entrega(request, id_pedido):
    if Op.objects.filter(id_pedido=id_pedido):
        return HttpResponse(Op.objects.filter(id_pedido=id_pedido)[0].fecha_entrega, status=200)
    return HttpResponse(f'ERROR, NO SE ENCUENTRA FECHA ENTREGA DE {id_pedido}', status=404)

def agregar_det_prod(request, id_pedido, cant, id_product):
    if not len(Op.objects.filter(id_pedido=id_pedido)):
        return HttpResponse('No existe ID PEDIDO.', status=404)

    if not len(Producto.objects.filter(id_product=id_product)):
        return HttpResponse('No existe producto!', status=404)

    try:
        DetalleOp.objects.last().id_detalle_op
        id_detalle = DetalleOp.objects.last().id_detalle_op + 1
    except AttributeError:
        id_detalle = 1

    id_proveedor, familia, fecha_vencimiento, tipo = ['001', '005', '000000000', '008']
    cod_prod = f'{id_proveedor}{familia}{fecha_vencimiento}{tipo}'

    nuevo_detalle = DetalleOp(id_detalle,cod_prod,cant,id_pedido, id_product)
    nuevo_detalle.save()

    return HttpResponse(f'{id_detalle}', status=200)

def eliminar_pedido(request, id_pedido):
    coincidencia = Op.objects.filter(id_pedido=id_pedido)
    if len(coincidencia):
        eliminado = coincidencia[0]
        eliminado.delete()
        return HttpResponse(status =200)
    return HttpResponse ('ERROR, no coincide el id con ningun registro', status=404)

def get_new_id_pedido(request):
    try:
        Op.objects.last().id_pedido
    except AttributeError:
        return HttpResponse(1)
    
    if Op.objects.last().id_pedido:
        return HttpResponse(Op.objects.last().id_pedido+1)
    return HttpResponse(status=404)

def agregar_pedido(request, id_auto):
    try:
        Op.objects.last().id_pedido
    except AttributeError:
        return HttpResponse(1)
    id_pedido = Op.objects.last().id_pedido+1
    fecha_pedido = datetime.datetime.now()
    fecha_entrega = datetime.datetime.now() + datetime.timedelta(days=2)
    nuevo_pedido = Op(id_pedido, fecha_pedido, fecha_entrega, id_auto)
    nuevo_pedido.save()
    return HttpResponse('Backend: !Registro creado!', status=200)

def orden_pedido (request):
    proveedores = Proveedor.objects.all()
    pedidos = Op.objects.all().order_by('-id_pedido')
    detalles = DetalleOp.objects.all()
    productos = Producto.objects.all()
    autos = InfoAuto.objects.all().order_by('-id_informe')

    context = {'proveedores': proveedores,
               'pedidos': pedidos,
               'detalles': detalles,
               'productos': productos,
               'autos':autos,}
    if request.method =='POST':
        #=request.POST['']
        ''' auto = request.POST['auto']
         
        producto = request.POST['producto']
        cantidad = request.POST['cantidad']
        fecha_pedido = datetime.datetime.now()
        hora_pedido = datetime.datetime.now().strftime('%H_%M')
        fecha_entrega = datetime.datetime.now() + datetime.timedelta(days=2)
        proveedor = request.POST['proveedor']
        
        id_pedido = Op.objects.count()+1
        op = Op(id_pedido, producto, cantidad, fecha_pedido, hora_pedido, fecha_entrega, proveedor)
        op.save()
        
        id_detalle = DetallePedido.objects.count()+1
        dp = DetallePedido(id_detalle, id_pedido, proveedor)
        dp.save() '''

    return render (request, 'mantenedor/orden_pedido.html', context)

def registrar_pago(request, id_orden, tipo_recibo):
    if tipo_recibo not in ['boleta', 'factura']:
        return HttpResponse('Error del tipo recibo. (boleta/factura)')

    # Se obtiene la ultima ID de pago.
    try: id_pago = Pago.objects.last().id_pago + 1
    except AttributeError: id_pago = 1

    fecha_emision = datetime.datetime.now()

    monto = 0
    if tipo_recibo == 'botela':
        # se valida que exista la orden de trabajo
        try: orden_trabajo = Ot.objects.get(id_orden=id_orden)
        except: return HttpResponse('no existe orden de trabajo asociado')

        id_reserva = orden_trabajo.reservas_id_reserva.id_reserva
        for servicio in DetalleOp.objects.filter(reservas_id_reservas = id_reserva):
            monto += int (servicio.tipo_servicio_id_servicio.monto)

    else: # --> factura
        # se valida que exista la orden de pedido
        try: orden_pedido = Op.objects.get(id_pedido=id_orden)
        except: return HttpResponse('No existe orden de pedido asociado')

        for producto in DetalleOp.objects.filter(op_id_pedido=orden_pedido.id_pedido):
            monto += producto.cantidad * producto.producto_id_producto.valor

    if Pago.objects.filter(id_orden=id_orden).filter(tipo_recibo=tipo_recibo):
        return HttpResponse(f'ya existe un pago registrado para esta orden', status = 404)
    else:
        nuevo_pago = Pago (id_pago, id_orden,fecha_emision,tipo_recibo,monto)
        nuevo_pago.save()
        return HttpResponse('pago registrado!', status=200)
    
    return HttpResponse ('pago registrado', status= 404)







































