
import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ApiService, mensajeError } from '../../core/api.service';

interface RegistroRespaldo {
  id: number;
  archivo: string;
  tamano: number;
  fecha: string;
  ok: boolean;
  error: string;
  usuario: number | null;
}

@Component({
  selector: 'app-respaldos',
  standalone: true,
  imports: [CommonModule],
  template: `
    <h1>Respaldos de base de datos</h1>

    <div class="tarjeta">
      <div class="fila">
        <div>
          <h2>Administración de respaldos</h2>
          <p>Consulta y genera copias de seguridad de la base de datos.</p>
        </div>

        <button
          type="button"
          (click)="crear()"
          [disabled]="creando || cargando">
          {{ creando ? 'Generando...' : 'Generar respaldo' }}
        </button>

        <button
          type="button"
          class="btn-sec"
          (click)="cargar()"
          [disabled]="cargando || creando">
          Actualizar
        </button>
      </div>

      <p *ngIf="cargando">Cargando respaldos...</p>
      <p class="ok" *ngIf="mensaje">{{ mensaje }}</p>
      <p class="error" *ngIf="error">{{ error }}</p>
    </div>

    <div class="tarjeta">
      <div class="fila">
        <h2>Historial de respaldos</h2>
        <span class="etiqueta">{{ registros.length }} registros</span>
      </div>

      <div style="overflow-x: auto">
        <table>
          <thead>
            <tr>
              <th>Archivo</th>
              <th>Fecha</th>
              <th>Tamaño</th>
              <th>Estado</th>
              <th>Error</th>
            </tr>
          </thead>

          <tbody>
            <tr *ngFor="let r of registros">
              <td>{{ r.archivo }}</td>
              <td>{{ r.fecha | date:'dd/MM/yyyy HH:mm:ss' }}</td>
              <td>{{ r.tamano | number }} bytes</td>
              <td>
                <span class="etiqueta"
                  [class.verde]="r.ok"
                  [class.rojo]="!r.ok">
                  {{ r.ok ? 'Correcto' : 'Fallido' }}
                </span>
              </td>
              <td>{{ r.error || '-' }}</td>
            </tr>

            <tr *ngIf="!cargando && registros.length === 0">
              <td colspan="5" class="vacio">
                No hay respaldos registrados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
})
export class RespaldosComponent implements OnInit {
  private api = inject(ApiService);

  registros: RegistroRespaldo[] = [];
  cargando = false;
  creando = false;
  mensaje = '';
  error = '';

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.cargando = true;
    this.error = '';
    this.mensaje = '';

    this.api.get<RegistroRespaldo[]>('respaldos/').subscribe({
      next: (datos) => {
        this.registros = datos;
        this.cargando = false;
      },
      error: (e) => {
        this.error = mensajeError(e);
        this.cargando = false;
      }
    });
  }

  crear() {
    this.creando = true;
    this.error = '';
    this.mensaje = '';

    this.api.post<RegistroRespaldo>('respaldos/').subscribe({
      next: (registro) => {
        this.mensaje = 'Respaldo generado correctamente.';
        this.registros = [registro, ...this.registros];
        this.creando = false;
      },
      error: (e) => {
        this.error = mensajeError(e);
        this.creando = false;
      }
    });
  }
}
