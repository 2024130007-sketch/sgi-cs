import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/api.service';

/** Vista ConsultaStock (CU-08, RF-27 y RF-28): físico, reservado, disponible y en tránsito por lote. */
@Component({
  selector: 'app-stock',
  imports: [FormsModule],
  template: `
    <h1>Consulta de stock</h1>
    <div class="tarjeta fila">
      <label>Buscar (producto, SKU, lote o código de barras)
        <input [(ngModel)]="busqueda" (ngModelChange)="cargar()" placeholder="Ej: leche" />
      </label>
      <label>Almacén
        <select [(ngModel)]="almacen" (ngModelChange)="cargar()">
          <option value="">Todos</option>
          @for (a of almacenes; track a.id) { <option [value]="a.id">{{ a.nombre }}</option> }
        </select>
      </label>
      <button class="btn-sec" (click)="cargar()">Actualizar</button>
    </div>

    <table>
      <thead>
        <tr><th>SKU</th><th>Producto</th><th>Almacén</th><th>Lote</th><th>Vence</th><th>Físico</th><th>Reservado</th><th>Disponible</th></tr>
      </thead>
      <tbody>
        @for (e of stock; track e.id) {
          <tr>
            <td>{{ e.sku }}</td><td>{{ e.producto }}</td><td>{{ e.almacen_nombre }}</td>
            <td>{{ e.lote_numero }} @if (e.estado_lote === 'CUARENTENA') { <span class="etiqueta rojo">Cuarentena</span> }</td>
            <td>{{ e.vencimiento || '—' }}</td>
            <td>{{ e.cantidad }}</td><td>{{ e.reservada }}</td><td><b>{{ e.disponible }}</b></td>
          </tr>
        } @empty { <tr><td colspan="8" class="vacio">No hay stock para mostrar.</td></tr> }
      </tbody>
    </table>
  `,
})
export class StockComponent implements OnInit {
  private api = inject(ApiService);
  stock: any[] = [];
  almacenes: any[] = [];
  busqueda = '';
  almacen = '';

  ngOnInit() {
    this.api.get<any[]>('almacenes/').subscribe((d) => (this.almacenes = d));
    this.cargar();
  }
  cargar() {
    this.api.get<any[]>('inventario/stock/', { search: this.busqueda, almacen: this.almacen }).subscribe((d) => (this.stock = d));
  }
}
