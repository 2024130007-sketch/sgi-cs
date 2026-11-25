import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../../core/api.service';

/** Pantalla de reportes (#31): descarga de stock, kardex y órdenes en PDF o Excel. */
@Component({
  selector: 'app-reportes',
  imports: [FormsModule],
  template: `
    <h1>Reportes</h1>
    @if (error) { <div class="error">{{ error }}</div> }
    @if (ok) { <div class="ok">{{ ok }}</div> }

    <div class="tarjeta">
      <h3>Stock actual</h3>
      <p>Disponible por producto, lote y almacén.</p>
      <button (click)="descargar('stock', 'pdf')">PDF</button>
      <button class="btn-sec" (click)="descargar('stock', 'xlsx')">Excel</button>
    </div>

    <div class="tarjeta">
      <h3>Kardex</h3>
      <p>Últimos 200 movimientos.</p>
      <label>Almacén
        <select name="almacen" [(ngModel)]="almacen">
          <option [ngValue]="null">Todos</option>
          @for (a of almacenes; track a.id) { <option [ngValue]="a.id">{{ a.nombre }}</option> }
        </select>
      </label>
      <button (click)="descargar('kardex', 'pdf', { almacen })">PDF</button>
      <button class="btn-sec" (click)="descargar('kardex', 'xlsx', { almacen })">Excel</button>
    </div>

    <div class="tarjeta">
      <h3>Órdenes de compra</h3>
      <p>Todas las órdenes, o filtradas por estado.</p>
      <label>Estado<input name="estado" [(ngModel)]="estado" placeholder="Opcional" /></label>
      <button (click)="descargar('ordenes', 'pdf', { estado })">PDF</button>
      <button class="btn-sec" (click)="descargar('ordenes', 'xlsx', { estado })">Excel</button>
    </div>
  `,
})
export class ReportesComponent implements OnInit {
  private http = inject(HttpClient);
  private api = inject(ApiService);
  private base = '/api'; // cámbiala por la URL base que use api.service.ts
  almacenes: any[] = [];
  almacen: number | null = null;
  estado = '';
  error = '';
  ok = '';

  ngOnInit() {
    this.api.get<any[]>('almacenes/').subscribe((d) => (this.almacenes = d));
  }

  descargar(reporte: string, formato: 'pdf' | 'xlsx', filtros: Record<string, any> = {}) {
    this.error = this.ok = '';
    const params: Record<string, string> = { formato };
    for (const [k, v] of Object.entries(filtros)) if (v !== null && v !== undefined && v !== '') params[k] = String(v);

    this.http.get(`${this.base}/reportes/${reporte}/`, { params, responseType: 'blob' }).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const enlace = document.createElement('a');
        enlace.href = url;
        enlace.download = `${reporte}.${formato}`;
        enlace.click();
        URL.revokeObjectURL(url);
        this.ok = `Reporte de ${reporte} descargado en ${formato.toUpperCase()}.`;
      },
      error: () => (this.error = 'No se pudo descargar el reporte. Verifique su sesión y que el servidor esté activo.'),
    });
  }
}