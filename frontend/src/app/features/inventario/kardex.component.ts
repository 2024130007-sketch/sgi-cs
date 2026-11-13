import { Component, OnInit, inject } from '@angular/core';
import { ApiService } from '../../core/api.service';

/** Kardex de movimientos (RF-32): base de la vista TrazabilidadLote. */
@Component({
  selector: 'app-kardex',
  template: `
    <h1>Kardex de movimientos</h1>
    <table>
      <thead><tr><th>Fecha</th><th>Tipo</th><th>Almacén</th><th>Usuario</th><th>Documento</th><th>Detalle (lote x cantidad)</th></tr></thead>
      <tbody>
        @for (m of movimientos; track m.id) {
          <tr>
            <td>{{ m.fecha.slice(0, 16).replace('T', ' ') }}</td>
            <td><span class="etiqueta" [class.verde]="m.tipo==='INGRESO'" [class.ambar]="m.tipo!=='INGRESO'">{{ m.tipo_display }}</span></td>
            <td>{{ m.almacen_nombre }}</td><td>{{ m.usuario_email }}</td><td>{{ m.documento_origen || '-' }}</td>
            <td>@for (d of m.detalles; track $index) { <div>{{ d.producto }} {{ d.lote_numero }} x {{ d.cantidad }}</div> }</td>
          </tr>
        } @empty { <tr><td colspan="6" class="vacio">Aún no hay movimientos.</td></tr> }
      </tbody>
    </table>
  `
})
export class KardexComponent implements OnInit {
  private api = inject(ApiService);
  movimientos: any[] = [];
  ngOnInit() { this.api.get<any[]>('inventario/movimientos/').subscribe((d) => (this.movimientos = d)); }
}
