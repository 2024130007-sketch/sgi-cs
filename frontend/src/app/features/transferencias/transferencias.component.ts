import { Component, OnInit, inject } from '@angular/core'; 
import { FormsModule } from '@angular/forms'; 
import { ApiService, mensajeError } from '../../core/api.service'; 
 
/** Vista TransferenciaStock (CU-06, RF-21): Pendiente -> En tránsito -> Completada. */ 
@Component({ 
  selector: 'app-transferencias', 
  imports: [FormsModule], 
  template: ` 
    <h1>Transferencias entre almacenes</h1> 
    @if (error) { <div class="error">{{ error }}</div> } 
    @if (ok) { <div class="ok">{{ ok }}</div> } 
 
    <div class="tarjeta"> 
      <h3>Nueva transferencia</h3> 
      <form (ngSubmit)="crear()" class="fila"> 
        <label>Origen 
          <select name="origen" [(ngModel)]="form.origen"> 
            <option [ngValue]="null">Seleccione...</option> 
            @for (a of almacenes; track a.id) { <option [ngValue]="a.id">{{ a.nombre }}</option> } 
          </select> 
        </label> 
        <label>Destino 
          <select name="destino" [(ngModel)]="form.destino"> 
            <option [ngValue]="null">Seleccione...</option> 
            @for (a of almacenes; track a.id) { <option [ngValue]="a.id">{{ a.nombre }}</option> } 
          </select> 
        </label> 
        <label>Producto 
          <select name="producto" [(ngModel)]="form.producto"> 
            <option [ngValue]="null">Seleccione...</option> 
            @for (p of productos; track p.id) { <option [ngValue]="p.id">{{ p.sku }} - {{ p.nombre }}</option> } 
          </select> 
        </label> 
        <label class="chico">Cantidad<input name="cantidad" type="number" min="1" [(ngModel)]="form.cantidad" /></label> 
        <button type="submit">Crear y reservar</button> 
      </form> 
    </div> 
 
    <table> 
      <thead><tr><th>#</th><th>Origen → Destino</th><th>Detalle</th><th>Estado</th><th></th></tr></thead> 
      <tbody> 
        @for (t of transferencias; track t.id) { 
          <tr> 
            <td>{{ t.id }}</td> 
            <td>{{ t.origen_nombre }} → {{ t.destino_nombre }}</td> 
            <td> 
              @for (d of t.detalles; track d.id) { 
                <div>{{ d.producto }} (lote {{ d.lote_numero }}): {{ d.cantidad }} 
                  @if (d.cantidad_recibida !== null) { · recibido {{ d.cantidad_recibida }} }</div> 
              } 
            </td> 
            <td><span class="etiqueta" [class.ambar]="t.estado==='PENDIENTE'||t.estado==='EN_TRANSITO'" 
[class.verde]="t.estado==='COMPLETADA'" [class.rojo]="t.estado==='CANCELADA'">{{ t.estado_display }}</span></td> 
            <td> 
              @if (t.estado === 'PENDIENTE') { 
                <button class="btn-chico" (click)="accion(t, 'confirmar-salida', 'Salida confirmada: la mercadería está 
en tránsito.')">Confirmar salida</button> 
                <button class="btn-chico btn-peligro" (click)="accion(t, 'cancelar', 'Transferencia cancelada y reserva 
liberada.')">Cancelar</button> 
              } 
              @if (t.estado === 'EN_TRANSITO') { 
                <button class="btn-chico" (click)="accion(t, 'confirmar-ingreso', 'Ingreso confirmado en el almacén 
destino.')">Confirmar ingreso</button> 
              } 
            </td> 
          </tr> 
        } @empty { <tr><td colspan="5" class="vacio">No hay transferencias.</td></tr> } 
      </tbody> 
    </table> 
  `, 
}) 
export class TransferenciasComponent implements OnInit { 
  private api = inject(ApiService); 
  almacenes: any[] = []; 
  productos: any[] = []; 
  transferencias: any[] = []; 
  form: any = { origen: null, destino: null, producto: null, cantidad: 1 }; 
  error = ''; 
  ok = ''; 
 
  ngOnInit() { 
    this.api.get<any[]>('almacenes/').subscribe((d) => (this.almacenes = d.filter((a) => a.activo))); 
    this.api.get<any[]>('productos/').subscribe((d) => (this.productos = d.filter((p) => p.activo))); 
    this.cargar(); 
  } 
  cargar() { this.api.get<any[]>('transferencias/').subscribe((d) => (this.transferencias = d)); } 
 
  crear() { 
    this.error = this.ok = ''; 
    const f = this.form; 
    if (!f.origen || !f.destino || !f.producto || !f.cantidad || f.cantidad < 1) { 
      this.error = 'Complete origen, destino, producto y una cantidad mayor a cero.'; 
      return; 
    } 
    this.api.post('transferencias/', f).subscribe({ 
      next: () => { this.ok = 'Transferencia creada; el stock quedó reservado.'; this.cargar(); }, 
      error: (e) => (this.error = mensajeError(e)), 
    }); 
  } 
  accion(t: any, nombre: string, mensaje: string) { 
    this.error = this.ok = ''; 
    this.api.post(`transferencias/${t.id}/${nombre}/`).subscribe({ 
      next: () => { this.ok = mensaje; this.cargar(); }, 
      error: (e) => (this.error = mensajeError(e)), 
    }); 
  } 
} 