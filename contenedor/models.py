from django import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class FormularioRegistro(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')

    def save(self, commit=True):
        # Función anónima para validar que sólo se ingresen números.
        only_numbers = lambda texto: ''.join([numero if numero in ['0','1','2','3','4','5','6','7','8','9'] else '' for numero in texto])
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.username = only_numbers(self.cleaned_data['username'])
        if commit:
            user.save()
        return user

class Cargo(models.Model):
    id_tipo_cargo = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

    class Meta:
        managed = True
        db_table = 'cargo'


class Cliente(models.Model):
    id_cliente = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    direccion = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.IntegerField(blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    ci = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.nombre + ' ' + self.apellido + ', ' + str(self.rut)

    class Meta:
        managed = True
        db_table = 'cliente'


class DetalleOp(models.Model):
    id_detalle_op = models.FloatField(primary_key=True)
    cod_producto = models.FloatField()
    cantidad = models.FloatField()
    op_id_pedido = models.ForeignKey('Op', on_delete=models.CASCADE, db_column='op_id_pedido')
    producto_id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE, db_column='producto_id_producto')

    class Meta:
        managed = True
        db_table = 'detalle_op'


class DetallePedido(models.Model):
    id_proucto_op = models.FloatField(primary_key=True)
    op_id_pedido = models.FloatField()
    proveedor_id_proveedor = models.FloatField()
    class Meta:
        managed = True
        db_table = 'detalle_pedido'

class DetalleSer(models.Model):
    id_detalle_ser = models.FloatField(primary_key=True)
    reservas_id_reserva = models.ForeignKey('Reservas', db_column='reservas_id_reserva', on_delete=models.CASCADE)
    tipo_servicio_id_servicio = models.ForeignKey('TipoServicio', models.DO_NOTHING, db_column='tipo_servicio_id_servicio')

    class Meta:
        managed = True
        db_table = 'detalle_ser'

class Empleado(models.Model):
    id_empleado = models.IntegerField(primary_key=True)
    ci = models.FloatField()
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    contacto = models.CharField(max_length=50)
    cargo_id_tipo_cargo = models.ForeignKey(Cargo, models.DO_NOTHING, db_column='cargo_id_tipo_cargo')
    
    def __str__(self):
        return f'{self.id_empleado}) {self.rut}, {self.nombre} {self.apellido}, {self.contacto}, {self.cargo_id_tipo_cargo.nombre}'

    class Meta:
        managed = True
        db_table = 'empleado'

class EstadoVehiculo(models.Model):
    id_estado = models.FloatField(primary_key=True)
    cliente = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50, blank=True, null=True)
    contacto = models.FloatField()
    fecha = models.DateField()
    modelo = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    patente = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    year = models.CharField(max_length=50)
    kilometraje = models.CharField(max_length=50)
    combustible = models.CharField(max_length=10)
    a_motor = models.CharField(max_length=10)
    refrigerante = models.CharField(max_length=10)
    liq_frenos = models.CharField(max_length=50)
    intermitente = models.CharField(max_length=30)
    observaciones = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'estado_vehiculo'


class InfoAuto(models.Model):
    id_informe = models.FloatField(primary_key=True)
    cliente = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50, blank=True, null=True)
    contacto = models.FloatField()
    fecha = models.DateField()
    modelo = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    patente = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    year = models.CharField(max_length=50)
    kilometraje = models.CharField(max_length=50)
    combustible = models.CharField(max_length=10)
    a_motor = models.CharField(max_length=10)
    refrigerante = models.CharField(max_length=10)
    liq_frenos = models.CharField(max_length=50)
    intermitente = models.CharField(max_length=30)
    observaciones = models.CharField(max_length=200, blank=True, null=True)
    empleado_id_empleado = models.ForeignKey(Empleado, models.DO_NOTHING, db_column='empleado_id_empleado')

    class Meta:
        managed = True
        db_table = 'info_auto'

class Op(models.Model):
    id_pedido = models.FloatField(primary_key=True)
    fecha_pedido = models.DateField()
    fecha_entrega = models.DateField(blank=True, null=True)
    info_auto_id_informe = models.ForeignKey(InfoAuto, models.DO_NOTHING, db_column='info_auto_id_informe')

    class Meta:
        managed = True
        db_table = 'op'


class Ot(models.Model):
    id_orden = models.FloatField(primary_key=True)
    empleado_id_empleado = models.ForeignKey(Empleado, models.DO_NOTHING, db_column='empleado_id_empleado')
    reservas_id_reserva = models.ForeignKey('Reservas', models.DO_NOTHING, db_column='reservas_id_reserva')
    fecha_termino = models.DateField()
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ot'


class Pago(models.Model):
    id_pago = models.FloatField(primary_key=True)
    id_orden = models.FloatField()
    fecha_emision = models.DateField()
    tipo_recibo = models.CharField(max_length=10)
    monto = models.FloatField()

    def __str__(self):
        return f'{self.id_pago}) id orden: {self.id_orden} - {self.fecha_emision} - {self.tipo_recibo} - Monto: {self.monto}'
    class Meta:
        managed = True
        db_table = 'pago'

class Perfil(models.Model):
    id_perfil = models.FloatField(primary_key=True)
    id_auth_user = models.FloatField()
    id_usuario = models.FloatField()
    nivel = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.id_perfil}) FK_AUTH_username: {User.objects.get(id=self.id_auth_user).username}, nivel: {self.nivel}, id_auth_user: {self.id_auth_user}, id_usuario: {self.id_usuario}'

    class Meta:
        managed = True
        db_table = 'perfil'
        verbose_name_plural = "Perfiles"
        
class Producto(models.Model):
    id_producto = models.FloatField(primary_key=True)
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=18)
    valor = models.FloatField()
    descripcion = models.CharField(max_length=100)
    proveedor_id_proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE, db_column='proveedor_id_proveedor')

    class Meta:
        managed = True
        db_table = 'producto'

class Proveedor(models.Model):
    id_proveedor = models.FloatField(primary_key=True)
    ci = models.FloatField()
    nombre = models.CharField(max_length=50)
    telefono = models.FloatField()
    email = models.CharField(max_length=50)
    rubro = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.id_proveedor}, {self.nombre}, {self.rubro}, {self.telefono}, {self.email}, {self.rut}'

    class Meta:
        managed = True
        db_table = 'proveedor'
        verbose_name_plural = "Proveedores"


class Reservas(models.Model):
    id_reserva = models.FloatField(primary_key=True)
    cliente_id_cliente = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='cliente_id_cliente')
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    year = models.CharField(max_length=50)
    fecha_reserva = models.DateField()
    confirmacion = models.CharField(max_length=50)
        
    def __str__(self):
        estado = 'confirmado' if self.confirmacion == 1 else 'Sin confirmar'
        return f'{self.id_reserva}, {self.marca}, {self.modelo}, {self.year}, {estado}.'

    class Meta:
        managed = True
        db_table = 'reservas'

class TipoServicio(models.Model):
    id_servicio = models.FloatField(primary_key=True)
    nombre = models.CharField(max_length=50)
    monto = models.FloatField()
    tiempo_serv = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'tipo_servicio'
    
    def __str__(self):
        return f'{self.nombre}'