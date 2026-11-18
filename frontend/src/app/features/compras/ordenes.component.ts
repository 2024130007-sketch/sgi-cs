import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ApiService, mensajeError } from '../../core/api.service';
import { AuthService } from '../../core/auth.service';

/** Vista GestionOrdenCompra (CU-10, RF-35): crear, modificar y seguir órdenes de compra. */
@Component({
  selector: 'app-ordenes',
  imports: [FormsModule],
  template: `
    <h1>Órdenes de compra</h1>
    @if (error) { <div class="error">{{ error }}</div> }
    @if (ok) { <div class="ok">{{ ok }}</div> }

    @if (puedeEditar) {
      <div class="tarjeta">
        <h3>{{ editandoId ? 'Modificar orden OC-' + editandoId : 'Nueva orden de compra' }}</h3>
        <form (ngSubmit)="guardar()">
          <div class="fila">
            <label>Proveedor
              <select name="proveedor" [(ngModel)]="form.proveedor">
                <option [ngValue]="null">Seleccione...</option>
                @for (p of proveedores; track p.id) { <option [ngValue]="p.id">{{ p.razon_social }}</option> }
              </select>
            </label>
            <label>Almacén de destino
              <select name="almacen" [(ngModel)]="form.almacen_destino">
                <option [ngValue]="null">Seleccione...</option>
                @for (a of almacenes; track a.id) { <option [ngValue]="a.id">{{ a.nombre }}</option> }
              </select>
            </label>
            <label>Observación<input name="obs" [(ngModel)]="form.observacion" /></label>
          </div>
          <h4>Productos</h4>
          @for (it of form.items; track $index; let i = $index) {
            <div class="fila" style="margin-bottom:6px">
              <label>Producto
                <select [name]="'prod' + i" [(ngModel)]="it.producto">
                  <option [ngValue]="null">Seleccione...</option>
                  @for (p of productos; track p.id) { <option [ngValue]="p.id">{{ p.sku }} - {{ p.nombre }}</option> }
                </select>
              </label>
              <label class="chico">Cantidad<input [name]="'cant' + i" type="number" min="1" [(ngModel)]="it.cantidad" /></label>
              <label class="chico">Precio unit.<input [name]="'prec' + i" type="number" min="0" step="0.01" [(ngModel)]="it.precio_unitario" /></label>
              <button type="button" class="btn-chico btn-peligro" (click)="quitar(i)">Quitar</button>
            </div>
          }
          <div class="fila" style="margin-top:8px">
            <button type="button" class="btn-sec" (click)="agregar()">+ Agregar producto</button>
            <button type="submit">{{ editandoId ? 'Guardar cambios' : 'Crear orden' }}</button>
            @if (editandoId) { <button type="button" class="btn-sec" (click)="cancelarEdicion()">Cancelar edición</button> }
          </div>
        </form>
      </div>
    }

    <table>
      <thead><tr><th>N.º</th><th>Proveedor</th><th>Destino</th><th>Total (S/)</th><th>Estado</th><th>Acciones</th></tr></thead>
      <tbody>
        @for (o of ordenes; track o.id) {
          <tr>
            <td>OC-{{ o.id }}</td><td>{{ o.proveedor_nombre }}</td><td>{{ o.almacen_nombre }}</td><td>{{ o.total }}</td>
            <td><span class="etiqueta" [class.verde]="o.estado === 'APROBADA' || o.estado === 'RECIBIDA'"
                  [class.rojo]="o.estado === 'RECHAZADA' || o.estado === 'CANCELADA'"
                  [class.ambar]="o.estado === 'PENDIENTE'">{{ o.estado_display }}</span>
              @if (o.motivo_rechazo) { <br><small>{{ o.motivo_rechazo }}</small> }</td>
            <td>
              @if (puedeEditar && o.estado === 'BORRADOR') {
                <button class="btn-chico btn-sec" (click)="editar(o)">Modificar</button>
                <button class="btn-chico" (click)="accion(o, 'enviar-aprobacion', 'Orden enviada a aprobación.')">Enviar a aprobación</button>
              }
              @if (puedeEditar && (o.estado === 'BORRADOR' || o.estado === 'PENDIENTE' || o.estado === 'APROBADA')) {
                <button class="btn-chico btn-peligro" (click)="accion(o, 'cancelar', 'Orden cancelada.')">Cancelar</button>
              }
            </td>
          </tr>
        } @empty { <tr><td colspan="6" class="vacio">No hay órdenes de compra.</td></tr> }
      </tbody>
    </table>
  `,
})
export class OrdenesComponent implements OnInit {
  private api = inject(ApiService);
  private auth = inject(AuthService);
  proveedores: any[] = [];
  almacenes: any[] = [];
  productos: any[] = [];
  ordenes: any[] = [];
  form: any = this.vacio();
  editandoId: number | null = null;
  error = '';
  ok = '';

  get puedeEditar() { return this.auth.tieneRol('ADMINISTRADOR', 'COMPRADOR'); }

  vacio() { return { proveedor: null, almacen_destino: null, observacion: '', items: [{ producto: null, cantidad: 1, precio_unitario: 0 }] }; }

  ngOnInit() {
    this.api.get<any[]>('proveedores/').subscribe((d) => (this.proveedores = d.filter((p) => p.activo)));
    this.api.get<any[]>('almacenes/').subscribe((d) => (this.almacenes = d.filter((a) => a.activo)));
    this.api.get<any[]>('productos/').subscribe((d) => (this.productos = d.filter((p) => p.activo)));
    this.cargar();
  }
  cargar() { this.api.get<any[]>('compras/ordenes/').subscribe((d) => (this.ordenes = d)); }

  agregar() { this.form.items.push({ producto: null, cantidad: 1, precio_unitario: 0 }); }
  quitar(i: number) { this.form.items.splice(i, 1); }

  guardar() {
    this.error = this.ok = '';
    const f = this.form;
    if (!f.proveedor || !f.almacen_destino) { this.error = 'Seleccione el proveedor y el almacén de destino.'; return; }
    if (!f.items.length || f.items.some((i: any) => !i.producto || !i.cantidad || i.cantidad < 1)) {
      this.error = 'Cada línea necesita un producto y una cantidad mayor a cero.';
      return;
    }
    const peticion = this.editandoId
      ? this.api.put(`compras/ordenes/${this.editandoId}/`, f)
      : this.api.post('compras/ordenes/', f);
    peticion.subscribe({
      next: () => {
        this.ok = this.editandoId ? 'Orden modificada.' : 'Orden creada en borrador.';
        this.cancelarEdicion();
        this.cargar();
      },
      error: (e) => (this.error = mensajeError(e)),
    });
  }

  editar(o: any) {
    this.error = this.ok = '';
    this.editandoId = o.id;
    this.form = {
      proveedor: o.proveedor, almacen_destino: o.almacen_destino, observacion: o.observacion,
      items: o.detalles.map((d: any) => ({ producto: d.producto, cantidad: d.cantidad, precio_unitario: d.precio_unitario })),
    };
  }
  cancelarEdicion() { this.editandoId = null; this.form = this.vacio(); }

  accion(o: any, nombre: string, mensaje: string) {
    this.error = this.ok = '';
    this.api.post(`compras/ordenes/${o.id}/${nombre}/`).subscribe({
      next: () => { this.ok = mensaje; this.cargar(); },
      error: (e) => (this.error = mensajeError(e)),
    });
  }
}
