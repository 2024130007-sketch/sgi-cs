import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, mensajeError } from '../../core/api.service';

/** Vista RecepcionOrdenCompra (CU-12, RF-37 y RF-38): recibe mercadería contra una orden, total o parcial. */
@Component({
  selector: 'app-recepcion',
  imports: [FormsModule],
  template: `
    <h1>Recepción de órdenes de compra</h1>
    @if (error) { <div class="error">{{ error }}</div> }
    @if (ok) { <div class="ok">{{ ok }}</div> }

    <div class="tarjeta">
      <label>Orden por recibir
        <select [(ngModel)]="ordenId" (ngModelChange)="elegir()">
          <option [ngValue]="null">Seleccione...</option>
          @for (o of ordenes; track o.id) { <option [ngValue]="o.id">OC-{{ o.id }} · {{ o.proveedor_nombre }} · {{ o.estado_display }}</option> }
        </select>
      </label>
    </div>

    @if (orden) {
      <div class="tarjeta">
        <h3>OC-{{ orden.id }} — {{ orden.proveedor_nombre }} → {{ orden.almacen_nombre }}</h3>
        <table>
          <thead><tr><th>Producto</th><th>Pedido</th><th>Recibido</th><th>Pendiente</th><th>Recibir ahora</th><th>N.º de lote</th><th>Vencimiento</th></tr></thead>
          <tbody>
            @for (d of orden.detalles; track d.id) {
              <tr>
                <td>{{ d.sku }} {{ d.producto_nombre }}</td><td>{{ d.cantidad }}</td><td>{{ d.cantidad_recibida }}</td><td><b>{{ d.pendiente }}</b></td>
                <td><input type="number" min="0" [max]="d.pendiente" style="width:80px" [(ngModel)]="lineas[d.id].cantidad" [name]="'c' + d.id" [disabled]="d.pendiente === 0" /></td>
                <td><input [(ngModel)]="lineas[d.id].numero_lote" [name]="'l' + d.id" [disabled]="d.pendiente === 0" /></td>
                <td><input type="date" [(ngModel)]="lineas[d.id].fecha_vencimiento" [name]="'v' + d.id" [disabled]="d.pendiente === 0" /></td>
              </tr>
            }
          </tbody>
        </table>
        <div class="fila" style="margin-top:10px">
          <label>Documento (guía de remisión)<input [(ngModel)]="observacion" name="obs" /></label>
          <button (click)="registrar()">Registrar recepción</button>
        </div>
      </div>
    }

    <h3>Recepciones registradas</h3>
    <table>
      <thead><tr><th>Fecha</th><th>Orden</th><th>Documento</th><th>Detalle</th><th>Estado</th></tr></thead>
      <tbody>
        @for (r of recepciones; track r.id) {
          <tr><td>{{ r.fecha.substring(0, 16).replace('T', ' ') }}</td><td>OC-{{ r.orden_compra }}</td><td>{{ r.documento }}</td>
            <td>@for (d of r.detalles; track d.id) { {{ d.cantidad }} × {{ d.producto }}{{ d.numero_lote ? ' (lote ' + d.numero_lote + ')' : '' }}; }</td>
            <td>{{ r.estado }}</td></tr>
        } @empty { <tr><td colspan="5" class="vacio">Aún no hay recepciones.</td></tr> }
      </tbody>
    </table>
  `,
})
export class RecepcionComponent implements OnInit {
  private api = inject(ApiService);
  ordenes: any[] = [];
  recepciones: any[] = [];
  ordenId: number | null = null;
  orden: any = null;
  lineas: Record<number, any> = {};
  observacion = '';
  error = '';
  ok = '';

  ngOnInit() { this.cargar(); }

  cargar() {
    this.api.get<any[]>('compras/ordenes/', { estado: 'APROBADA,ENVIADA,RECIBIDA_PARCIAL' }).subscribe((d) => (this.ordenes = d));
    this.api.get<any[]>('recepciones/').subscribe((d) => (this.recepciones = d));
  }

  elegir() {
    this.orden = this.ordenes.find((o) => o.id === this.ordenId) ?? null;
    this.lineas = {};
    for (const d of this.orden?.detalles ?? []) this.lineas[d.id] = { cantidad: d.pendiente, numero_lote: '', fecha_vencimiento: '' };
  }

  registrar() {
    this.error = this.ok = '';
    const lineas = Object.entries(this.lineas)
      .filter(([, l]) => Number(l.cantidad) > 0)
      .map(([id, l]) => ({ detalle_orden: Number(id), cantidad: Number(l.cantidad), numero_lote: l.numero_lote, fecha_vencimiento: l.fecha_vencimiento || null }));
    if (!lineas.length) { this.error = 'Indique la cantidad recibida de al menos un producto.'; return; }
    this.api.post('recepciones/', { orden_compra: this.orden.id, documento: this.observacion, detalles: lineas }).subscribe({
      next: () => {
        this.ok = 'Recepción registrada. La mercadería ya figura en el stock del almacén.';
        this.ordenId = null; this.orden = null; this.observacion = '';
        this.cargar();
      },
      error: (e) => (this.error = mensajeError(e)),
    });
  }
}