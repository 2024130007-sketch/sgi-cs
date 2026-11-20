import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, mensajeError } from '../../core/api.service';

interface RegistroBitacora {
  id: number;
  fecha: string;
  usuario: number | null;
  usuario_email: string | null;
  accion: string;
  accion_display: string;
  entidad: string;
  entidad_id: number | null;
  detalle: string;
}

@Component({
  selector: 'app-auditoria',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <h1>Bitácora de auditoría</h1>

    <div class="tarjeta">
      <h2>Filtros de búsqueda</h2>

      <div class="fila">
        <label>Usuario
          <input
            name="usuario"
            type="number"
            min="1"
            [(ngModel)]="filtros.usuario"
            placeholder="ID del usuario">
        </label>

        <label>Acción
          <select name="accion" [(ngModel)]="filtros.accion">
            <option value="">Todas</option>
            <option value="CREAR">Crear</option>
            <option value="MODIFICAR">Modificar</option>
          </select>
        </label>

        <label>Entidad
          <input
            name="entidad"
            [(ngModel)]="filtros.entidad"
            placeholder="Ej. Lote, Movimiento">
        </label>
      </div>

      <div class="fila" style="margin-top: 12px">
        <label>Desde
          <input
            type="date"
            name="fecha_desde"
            [(ngModel)]="filtros.fecha_desde">
        </label>

        <label>Hasta
          <input
            type="date"
            name="fecha_hasta"
            [(ngModel)]="filtros.fecha_hasta">
        </label>

        <button type="button" (click)="cargar()" [disabled]="cargando">
          Buscar
        </button>

        <button type="button" class="btn-sec" (click)="limpiar()">
          Limpiar filtros
        </button>
      </div>
    </div>

    <div class="tarjeta">
      <div class="fila">
        <h2>Registros de actividad</h2>
        <span class="etiqueta">{{ registros.length }} registros</span>
      </div>

      <p *ngIf="cargando">Cargando registros de auditoría...</p>
      <p class="error" *ngIf="error">{{ error }}</p>

      <div style="overflow-x: auto">
        <table>
          <thead>
            <tr>
              <th>Fecha y hora</th>
              <th>Usuario</th>
              <th>Acción</th>
              <th>Entidad</th>
              <th>ID entidad</th>
              <th>Detalle</th>
            </tr>
          </thead>

          <tbody>
            <tr *ngFor="let r of registros">
              <td>{{ r.fecha | date:'dd/MM/yyyy HH:mm:ss' }}</td>
              <td>{{ r.usuario_email || 'Sistema' }}</td>
              <td>
                <span class="etiqueta"
                  [class.verde]="r.accion === 'CREAR'"
                  [class.ambar]="r.accion === 'MODIFICAR'">
                  {{ r.accion_display }}
                </span>
              </td>
              <td>{{ r.entidad }}</td>
              <td>{{ r.entidad_id ?? '-' }}</td>
              <td>{{ r.detalle || '-' }}</td>
            </tr>

            <tr *ngIf="!cargando && registros.length === 0">
              <td colspan="6" class="vacio">
                No se encontraron registros de auditoría.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
})
export class AuditoriaComponent implements OnInit {
  private api = inject(ApiService);

  registros: RegistroBitacora[] = [];
  error = '';
  cargando = false;

  filtros = {
    usuario: '',
    accion: '',
    entidad: '',
    fecha_desde: '',
    fecha_hasta: ''
  };

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.cargando = true;
    this.error = '';

    this.api.get<RegistroBitacora[] | { results: RegistroBitacora[] }>(
      'auditoria/',
      this.filtros
    ).subscribe({
      next: (datos) => {
        this.registros = Array.isArray(datos) ? datos : datos.results;
        this.cargando = false;
      },
      error: (e) => {
        this.error = mensajeError(e);
        this.cargando = false;
      }
    });
  }

  limpiar() {
    this.filtros = {
      usuario: '',
      accion: '',
      entidad: '',
      fecha_desde: '',
      fecha_hasta: ''
    };

    this.cargar();
  }
}
