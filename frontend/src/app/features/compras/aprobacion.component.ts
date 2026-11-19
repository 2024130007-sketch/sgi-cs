import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ApiService, mensajeError } from '../../core/api.service';

/** Vista AprobacionOrdenCompra (CU-11, RF-36): aprobar o rechazar órdenes pendientes. */
@Component({
  selector: 'app-aprobacion',
  imports: [FormsModule],
  template: `
    <h1>Aprobación de órdenes de compra</h1>
    @if (error) { <div class="error">{{ error }}</div> }
    @if (ok) { <div class="ok">{{ ok }}</div> }

    @for (o of ordenes; track o.id) {
      <div class="tarjeta">
        <h3>OC-{{ o.id }} — {{ o.proveedor_nombre }}</h3>
        <p>Destino: {{ o.almacen_nombre }} · Solicitada por {{ o.creada_por_email }} · Total: <b>S/ {{ o.total }}</b>
          @if (o.observacion) { · {{ o.observacion }} }</p>
        <table>
          <thead><tr><th>SKU</th><th>Producto</th><th>Cantidad</th><th>Precio unit.</th><th>Subtotal</th></tr></thead>
          <tbody>
            @for (d of o.detalles; track d.id) {
              <tr><td>{{ d.sku }}</td><td>{{ d.producto_nombre }}</td><td>{{ d.cantidad }}</td><td>{{ d.precio_unitario }}</td><td>{{ d.subtotal }}</td></tr>
            }
          </tbody>
        </table>
        <div class="fila" style="margin-top:10px">
          <button (click)="aprobar(o)">Aprobar</button>
          <label>Motivo del rechazo<input [name]="'m' + o.id" [(ngModel)]="motivos[o.id]" /></label>
          <button class="btn-peligro" (click)="rechazar(o)">Rechazar</button>
        </div>
      </div>
    } @empty { <p class="vacio">No hay órdenes pendientes de aprobación.</p> }
  `,
})
export class AprobacionComponent implements OnInit {
  private api = inject(ApiService);
  ordenes: any[] = [];
  motivos: Record<number, string> = {};
  error = '';
  ok = '';

  ngOnInit() { this.cargar(); }
  cargar() { this.api.get<any[]>('compras/ordenes/', { estado: 'PENDIENTE' }).subscribe((d) => (this.ordenes = d)); }

  aprobar(o: any) {
    this.error = this.ok = '';
    this.api.post(`compras/ordenes/${o.id}/aprobar/`).subscribe({
      next: () => { this.ok = `OC-${o.id} aprobada.`; this.cargar(); },
      error: (e) => (this.error = mensajeError(e)),
    });
  }

  rechazar(o: any) {
    this.error = this.ok = '';
    const motivo = (this.motivos[o.id] || '').trim();
    if (!motivo) { this.error = 'Indique el motivo del rechazo.'; return; }
    this.api.post(`compras/ordenes/${o.id}/rechazar/`, { motivo }).subscribe({
      next: () => { this.ok = `OC-${o.id} rechazada.`; this.cargar(); },
      error: (e) => (this.error = mensajeError(e)),
    });
  }
}
