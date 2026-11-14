import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, mensajeError } from '../../core/api.service';

/** Vista RegistroSalida (CU-05, RF-16/17/19): descuenta lotes por FEFO. */
@Component({
  selector: 'app-salida',
  imports: [FormsModule],
  template: `
    <h1>Registrar salida de mercadería (FEFO)</h1>
    @if (error) { <div class="error">{{ error }}</div> }

    <div class="tarjeta">
      <form (ngSubmit)="registrar()" class="fila">
        <label>Almacén de origen
          <select name="almacen" [(ngModel)]="form.almacen">
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
        <label>Documento (pedido/guía)<input name="doc" [(ngModel)]="form.documento" /></label>
        <button type="submit">Registrar salida</button>
      </form>
    </div>

    @if (resultado) {
      <div class="ok">Salida registrada. Lotes asignados por FEFO (primero en vencer, primero en salir):</div>
      <table>
        <thead><tr><th>Producto</th><th>Lote</th><th>Vence</th><th>Cantidad</th></tr></thead>
        <tbody>
          @for (d of resultado.detalles; track $index) {
            <tr><td>{{ d.producto }}</td><td>{{ d.lote_numero }}</td><td>{{ d.vencimiento || '—' }}</td><td>{{ d.cantidad }}</td></tr>
          }
        </tbody>
      </table>
    }
  `,
})
export class SalidaComponent implements OnInit {
  private api = inject(ApiService);
  almacenes: any[] = [];
  productos: any[] = [];
  form: any = { almacen: null, producto: null, cantidad: 1, documento: '' };
  resultado: any = null;
  error = '';

  ngOnInit() {
    this.api.get<any[]>('almacenes/').subscribe((d) => (this.almacenes = d.filter((a) => a.activo)));
    this.api.get<any[]>('productos/').subscribe((d) => (this.productos = d.filter((p) => p.activo)));
  }

  registrar() {
    this.error = '';
    this.resultado = null;
    const f = this.form;
    if (!f.almacen || !f.producto) { this.error = 'Seleccione el almacén y el producto.'; return; }
    if (!f.cantidad || f.cantidad <= 0) { this.error = 'La cantidad debe ser mayor a cero.'; return; }
    this.api.post<any>('inventario/salidas/', f).subscribe({
      next: (r) => (this.resultado = r),
      error: (e) => (this.error = mensajeError(e)),
    });
  }
}
