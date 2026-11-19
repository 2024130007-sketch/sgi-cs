import { SlicePipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, mensajeError } from '../../core/api.service';
import { AuthService } from '../../core/auth.service';

/** Vista TrazabilidadLote (CU-09, RF-33 y RF-34): historial del lote y cuarentena. */
@Component({
  selector: 'app-trazabilidad',
  imports: [FormsModule, SlicePipe],
  template: `
    <h1>Trazabilidad por lote</h1>
    @if (error) { <div class="error">{{ error }}</div> }
    @if (ok) { <div class="ok">{{ ok }}</div> }

    <div class="tarjeta fila">
      <label>Buscar lote (número, producto o SKU)
        <input [(ngModel)]="busqueda" (ngModelChange)="cargar()" placeholder="Ej: leche o L-2026" />
      </label>
      <label>Estado
        <select [(ngModel)]="estado" (ngModelChange)="cargar()">
          <option value="">Todos</option>
          <option value="ACTIVO">Activo</option>
          <option value="CUARENTENA">En cuarentena</option>
        </select>
      </label>
    </div>

    <table>
      <thead><tr><th>SKU</th><th>Producto</th><th>Lote</th><th>Vence</th><th>Stock</th><th>Estado</th><th></th></tr></thead>
      <tbody>
        @for (l of lotes; track l.id) {
          <tr>
            <td>{{ l.sku }}</td><td>{{ l.producto }}</td><td>{{ l.numero }}</td>
            <td>{{ l.fecha_vencimiento || '—' }}</td><td>{{ l.stock_total }}</td>
            <td><span class="etiqueta" [class.rojo]="l.estado === 'CUARENTENA'" [class.verde]="l.estado === 'ACTIVO'">{{ l.estado_display }}</span></td>
            <td><button class="btn-chico" (click)="ver(l)">Ver trazabilidad</button></td>
          </tr>
        } @empty { <tr><td colspan="7" class="vacio">No hay lotes para mostrar.</td></tr> }
      </tbody>
    </table>

    @if (detalle) {
      <div class="tarjeta" style="margin-top:16px">
        <h3>Lote {{ detalle.lote.numero }} — {{ detalle.lote.producto }}</h3>
        <p>Estado: <b>{{ detalle.lote.estado_display }}</b>
          @if (detalle.lote.motivo_estado) { · Motivo: {{ detalle.lote.motivo_estado }} }
          · Proveedor: {{ detalle.lote.proveedor_nombre || '—' }}
          · Stock total: <b>{{ detalle.lote.stock_total }}</b></p>

        @if (puedeGestionar) {
          <form (ngSubmit)="cambiarEstado()" class="fila">
            @if (detalle.lote.estado === 'ACTIVO') {
              <label>Motivo de la cuarentena<input name="motivo" [(ngModel)]="motivo" /></label>
              <button type="submit" class="btn-peligro">Poner en cuarentena</button>
            } @else {
              <button type="submit">Liberar lote</button>
            }
          </form>
        }

        <h4>Dónde está hoy</h4>
        <table>
          <thead><tr><th>Almacén</th><th>Físico</th><th>Reservado</th><th>Disponible</th></tr></thead>
          <tbody>
            @for (e of detalle.existencias; track e.almacen) {
              <tr><td>{{ e.almacen }}</td><td>{{ e.cantidad }}</td><td>{{ e.reservada }}</td><td>{{ e.disponible }}</td></tr>
            } @empty { <tr><td colspan="4" class="vacio">Sin existencias.</td></tr> }
          </tbody>
        </table>

        <h4>Historial de movimientos</h4>
        <table>
          <thead><tr><th>Fecha</th><th>Tipo</th><th>Almacén</th><th>Cantidad</th><th>Documento</th><th>Usuario</th></tr></thead>
          <tbody>
            @for (m of detalle.movimientos; track $index) {
              <tr><td>{{ m.fecha | slice:0:16 }}</td><td>{{ m.tipo_display }}</td><td>{{ m.almacen }}</td>
                <td>{{ m.cantidad }}</td><td>{{ m.documento || '—' }}</td><td>{{ m.usuario }}</td></tr>
            } @empty { <tr><td colspan="6" class="vacio">Sin movimientos.</td></tr> }
          </tbody>
        </table>
      </div>
    }
  `,
})
export class TrazabilidadComponent implements OnInit {
  private api = inject(ApiService);
  private auth = inject(AuthService);
  lotes: any[] = [];
  detalle: any = null;
  busqueda = '';
  estado = '';
  motivo = '';
  error = '';
  ok = '';

  get puedeGestionar() { return this.auth.tieneRol('ADMINISTRADOR', 'JEFE_ALMACEN'); }

  ngOnInit() { this.cargar(); }

  cargar() {
    this.api.get<any[]>('inventario/lotes/', { search: this.busqueda, estado: this.estado }).subscribe({
      next: (d) => (this.lotes = d),
      error: (e) => (this.error = mensajeError(e)),
    });
  }

  ver(l: any) {
    this.error = this.ok = this.motivo = '';
    this.api.get<any>(`inventario/lotes/${l.id}/trazabilidad/`).subscribe({
      next: (d) => (this.detalle = d),
      error: (e) => (this.error = mensajeError(e)),
    });
  }

  cambiarEstado() {
    this.error = this.ok = '';
    const nuevo = this.detalle.lote.estado === 'ACTIVO' ? 'CUARENTENA' : 'ACTIVO';
    if (nuevo === 'CUARENTENA' && !this.motivo.trim()) { this.error = 'Indique el motivo de la cuarentena.'; return; }
    this.api.post(`inventario/lotes/${this.detalle.lote.id}/estado/`, { estado: nuevo, motivo: this.motivo }).subscribe({
      next: () => {
        this.ok = nuevo === 'CUARENTENA' ? 'Lote puesto en cuarentena: no saldrá por FEFO.' : 'Lote liberado.';
        this.ver(this.detalle.lote);
        this.cargar();
      },
      error: (e) => (this.error = mensajeError(e)),
    });
  }
}
