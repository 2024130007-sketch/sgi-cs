import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, mensajeError } from '../../core/api.service';

/** Vista BandejaAlertas (CU-14 y CU-15, RF-41 a RF-47). */
@Component({
  selector: 'app-alertas',
  imports: [FormsModule],
  template: `
    <h1>Bandeja de alertas</h1>
    @if (error) { <div class="error">{{ error }}</div> }
    @if (ok) { <div class="ok">{{ ok }}</div> }

    <div class="tarjeta fila">
      <label>Estado
        <select [(ngModel)]="estado" (ngModelChange)="cargar()">
          <option value="ABIERTA">Abiertas</option>
          <option value="ATENDIDA">Atendidas</option>
          <option value="DESCARTADA">Descartadas</option>
          <option value="">Todas</option>
        </select>
      </label>
      <button (click)="generar()">Verificar alertas ahora</button>
    </div>

    <table>
      <thead><tr><th>Tipo</th><th>Producto</th><th>Almacén</th><th>Mensaje</th><th>Sugerido</th><th>Estado</th><th></th></tr></thead>
      <tbody>
        @for (a of alertas; track a.id) {
          <tr>
            <td><span class="etiqueta" [class.ambar]="a.tipo=='REPOSICION'" [class.rojo]="a.tipo=='VENCIMIENTO'">{{ a.tipo_display }}</span></td>
            <td>{{ a.producto_nombre }}</td>
            <td>{{ a.almacen_nombre }}</td>
            <td>{{ a.mensaje }}</td>
            <td>{{ a.tipo=='REPOSICION' ? a.cantidad_sugerida : '—' }}</td>
            <td>{{ a.estado }}</td>
            <td>
              @if (a.estado == 'ABIERTA') {
                <input class="mini" placeholder="Motivo" [(ngModel)]="motivos[a.id]" style="width:130px" />
                <button class="btn-chico" (click)="cerrar(a, 'atender')">Atender</button>
                <button class="btn-chico btn-sec" (click)="cerrar(a, 'descartar')">Descartar</button>
              } @else {
                {{ a.motivo }}
              }
            </td>
          </tr>
        } @empty { <tr><td colspan="7" class="vacio">No hay alertas.</td></tr> }
      </tbody>
    </table>
  `,
})
export class AlertasComponent implements OnInit {
  private api = inject(ApiService);
  alertas: any[] = [];
  estado = 'ABIERTA';
  motivos: Record<number, string> = {};
  error = '';
  ok = '';

  ngOnInit() { this.cargar(); }

  cargar() {
    this.api.get<any[]>('alertas', { estado: this.estado }).subscribe((d) => (this.alertas = d));
  }

  generar() {
    this.error = this.ok = '';
    this.api.post<any>('alertas/generar').subscribe({
      next: (r) => { this.ok = `Verificación terminada: ${r.nuevas} alerta(s) nueva(s).`; this.cargar(); },
      error: (e) => { this.error = mensajeError(e); },
    });
  }

  cerrar(a: any, accion: 'atender' | 'descartar') {
    this.error = this.ok = '';
    this.api.post<any>(`alertas/${a.id}/${accion}`, { motivo: this.motivos[a.id] || '' }).subscribe({
      next: () => { this.ok = 'Alerta actualizada.'; this.cargar(); },
      error: (e) => { this.error = mensajeError(e); },
    });
  }
}