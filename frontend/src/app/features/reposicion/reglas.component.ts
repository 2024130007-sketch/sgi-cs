import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, mensajeError } from '../../core/api.service';

/** Vista ReglasReposicion (CU-13, RF-40): punto de reorden = demanda diaria x entrega + seguridad. */
@Component({
  selector: 'app-reglas',
  imports: [FormsModule],
  template: `
    <h1>Reglas de reposición</h1>
    @if (error) { <div class="error">{{ error }}</div> }
    @if (ok) { <div class="ok">{{ ok }}</div> }

    <div class="tarjeta">
      <form (ngSubmit)="guardar()">
        <div class="fila">
          <label>Producto
            <select name="producto" [(ngModel)]="form.producto">
              <option [ngValue]="null">Seleccione...</option>
              @for (p of productos; track p.id) { <option [ngValue]="p.id">{{ p.sku }} - {{ p.nombre }}</option> }
            </select>
          </label>
          <label>Almacén
            <select name="almacen" [(ngModel)]="form.almacen">
              <option [ngValue]="null">Seleccione...</option>
              @for (a of almacenes; track a.id) { <option [ngValue]="a.id">{{ a.nombre }}</option> }
            </select>
          </label>
        </div>
        <div class="fila" style="margin-top:10px">
          <label class="chico">Mínimo<input name="min" type="number" min="0" [(ngModel)]="form.stock_minimo" /></label>
          <label class="chico">Seguridad<input name="seg" type="number" min="0" [(ngModel)]="form.stock_seguridad" /></label>
          <label class="chico">Máximo<input name="max" type="number" min="0" [(ngModel)]="form.stock_maximo" /></label>
          <label class="chico">Demanda diaria<input name="dem" type="number" min="0" [(ngModel)]="form.demanda_diaria" /></label>
          <label class="chico">Entrega (días)<input name="ent" type="number" min="1" [(ngModel)]="form.tiempo_entrega_dias" /></label>
          <label class="chico">Punto de reorden<input disabled [value]="puntoReorden()" /></label>
          <button type="submit">{{ editandoId ? 'Actualizar' : 'Guardar regla' }}</button>
          @if (editandoId) { <button type="button" class="btn-sec" (click)="limpiar()">Cancelar</button> }
        </div>
      </form>
    </div>

    <table>
      <thead><tr><th>Producto</th><th>Almacén</th><th>Mín.</th><th>Seg.</th><th>Máx.</th><th>Punto reorden</th><th></th></tr></thead>
      <tbody>
        @for (r of reglas; track r.id) {
          <tr>
            <td>{{ r.producto_nombre }}</td>
            <td>{{ r.almacen_nombre }}</td>
            <td>{{ r.stock_minimo }}</td>
            <td>{{ r.stock_seguridad }}</td>
            <td>{{ r.stock_maximo }}</td>
            <td>{{ r.punto_reorden }}</td>
            <td>
              <button class="btn-chico btn-sec" (click)="editar(r)">Editar</button>
              <button class="btn-chico btn-peligro" (click)="eliminar(r)">Eliminar</button>
            </td>
          </tr>
        } @empty { <tr><td colspan="7" class="vacio">No hay reglas configuradas.</td></tr> }
      </tbody>
    </table>
  `,
})
export class ReglasComponent implements OnInit {
  private api = inject(ApiService);
  productos: any[] = [];
  almacenes: any[] = [];
  reglas: any[] = [];
  form: any = this.vacio();
  editandoId: number | null = null;
  error = '';
  ok = '';

  vacio() { return { producto: null, almacen: null, stock_minimo: 0, stock_seguridad: 0, stock_maximo: 0, demanda_diaria: 0, tiempo_entrega_dias: 1 }; }
  puntoReorden() { return (this.form.demanda_diaria || 0) * (this.form.tiempo_entrega_dias || 0) + (this.form.stock_seguridad || 0); }

  ngOnInit() {
    this.api.get<any[]>('productos').subscribe((d) => (this.productos = d.filter((p) => p.activo)));
    this.api.get<any[]>('almacenes').subscribe((d) => (this.almacenes = d.filter((a) => a.activo)));
    this.cargar();
  }

  cargar() { this.api.get<any[]>('reglas-reposicion').subscribe((d) => (this.reglas = d)); }

  guardar() {
    this.error = this.ok = '';
    const f = this.form;
    if (!f.producto || !f.almacen) { this.error = 'Seleccione el producto y el almacén.'; return; }
    if (f.stock_maximo < f.stock_minimo) { this.error = 'El stock máximo no puede ser menor al minimo.'; return; }
    
    const existente = this.reglas.find((r) => r.producto === f.producto && r.almacen === f.almacen);
    const id = this.editandoId ?? existente?.id;
    const peticion = id ? this.api.put(`reglas-reposicion/${id}/`, f) : this.api.post('reglas-reposicion', f);
    
    peticion.subscribe({
      next: () => { this.ok = 'Regla guardada.'; this.limpiar(); this.cargar(); },
      error: (e) => (this.error = mensajeError(e)),
    });
  }

  editar(r: any) {
    this.editandoId = r.id;
    this.form = { producto: r.producto, almacen: r.almacen, stock_minimo: r.stock_minimo, stock_seguridad: r.stock_seguridad, stock_maximo: r.stock_maximo, demanda_diaria: r.demanda_diaria, tiempo_entrega_dias: r.tiempo_entrega_dias };
  }

  limpiar() { this.editandoId = null; this.form = this.vacio(); }

  eliminar(r: any) {
    this.api.delete(`reglas-reposicion/${r.id}/`).subscribe({ next: () => this.cargar(), error: (e) => (this.error = mensajeError(e)) });
  }
}