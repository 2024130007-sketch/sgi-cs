import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, mensajeError } from '../../core/api.service';

/** Vista RegistroIngreso (CU-04, RF-14/15/31). Incluye lectura de código de barras en modo teclado (CU-17). */
@Component({
  selector: 'app-ingreso',
  imports: [FormsModule],
  template: `
    <h1>Registrar ingreso de mercadería</h1>
    @if (error) { <div class="error">{{ error }}</div> }
    @if (ok) { <div class="ok">{{ ok }}</div> }

    <div class="tarjeta">
      <form (ngSubmit)="registrar()">
        <div class="fila">
          <label>Escanear código de barras
            <input name="cb" [(ngModel)]="codigo" (keydown.enter)="$event.preventDefault(); buscarCodigo()" placeholder="Escanee y presione Enter" />
          </label>
          <label>Almacén
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
        </div>
        <div class="fila" style="margin-top:10px">
          <label class="chico">Cantidad<input name="cantidad" type="number" min="1" [(ngModel)]="form.cantidad" /></label>
          <label>N.º de lote<input name="lote" [(ngModel)]="form.numero_lote" /></label>
          <label>Fecha de vencimiento<input name="venc" type="date" [(ngModel)]="form.fecha_vencimiento" /></label>
          <label>Proveedor
            <select name="proveedor" [(ngModel)]="form.proveedor">
              <option [ngValue]="null">(sin proveedor)</option>
              @for (p of proveedores; track p.id) { <option [ngValue]="p.id">{{ p.razon_social }}</option> }
            </select>
          </label>
          <label>Documento (guía/factura)<input name="doc" [(ngModel)]="form.documento" /></label>
          <button type="submit">Registrar ingreso</button>
        </div>
      </form>
    </div>
  `,
})
export class IngresoComponent implements OnInit {
  private api = inject(ApiService);
  almacenes: any[] = [];
  productos: any[] = [];
  proveedores: any[] = [];
  codigo = '';
  form: any = this.vacio();
  error = '';
  ok = '';

  vacio() { return { almacen: null, producto: null, cantidad: 1, numero_lote: '', fecha_vencimiento: '', proveedor: null, documento: '' }; }

  ngOnInit() {
    this.api.get<any[]>('almacenes/').subscribe((d) => (this.almacenes = d.filter((a) => a.activo)));
    this.api.get<any[]>('productos/').subscribe((d) => (this.productos = d.filter((p) => p.activo)));
    this.api.get<any[]>('proveedores/').subscribe((d) => (this.proveedores = d.filter((p) => p.activo)));
  }

  buscarCodigo() {
    this.error = '';
    if (!this.codigo.trim()) return;
    this.api.get<any>(`productos/codigo/${encodeURIComponent(this.codigo.trim())}/`).subscribe({
      next: (p) => { this.form.producto = p.id; this.codigo = ''; },
      error: (e) => (this.error = mensajeError(e)),
    });
  }

  registrar() {
    this.error = this.ok = '';
    const f = this.form;
    if (!f.almacen || !f.producto) { this.error = 'Seleccione el almacén y el producto.'; return; }
    if (!f.cantidad || f.cantidad <= 0) { this.error = 'La cantidad debe ser mayor a cero.'; return; }
    const cuerpo = { ...f, fecha_vencimiento: f.fecha_vencimiento || null };
    this.api.post('inventario/ingresos/', cuerpo).subscribe({
      next: () => { this.ok = 'Ingreso registrado correctamente. El stock fue actualizado.'; this.form = { ...this.vacio(), almacen: f.almacen }; },
      error: (e) => (this.error = mensajeError(e)),
    });
  }
}
