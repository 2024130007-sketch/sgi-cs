import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, mensajeError } from '../../core/api.service';

@Component({
  selector: 'app-erp',
  standalone: true,
  imports: [CommonModule],
  template: `
    <h1>Sincronización con el ERP</h1>
    @if (error) { <div class="error">{{ error }}</div> }
    @if (ok) { <div class="ok">{{ ok }}</div> }

    <div class="tarjeta">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h3>Cola de Eventos</h3>
        <button class="btn btn-primary" (click)="procesar()">Procesar Ahora</button>
      </div>
      
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Tipo</th>
            <th>Estado</th>
            <th>Intentos</th>
            <th>Último Error</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          @for (item of cola; track item.id) {
            <tr>
              <td>{{ item.id }}</td>
              <td>{{ item.tipo }}</td>
              <td>
                <span class="badge" 
                  [ngClass]="{
                    'bg-success': item.estado === 'ENVIADO',
                    'bg-warning': item.estado === 'PENDIENTE',
                    'bg-danger': item.estado === 'ERROR'
                  }">
                  {{ item.estado }}
                </span>
              </td>
              <td>{{ item.intentos }}</td>
              <td>{{ item.ultimo_error || '-' }}</td>
              <td>{{ item.creado | date:'short' }}</td>
            </tr>
          } @empty {
            <tr><td colspan="6" class="text-center">No hay eventos en la cola.</td></tr>
          }
        </tbody>
      </table>
    </div>
  `
})
export class ErpComponent implements OnInit {
  private api = inject(ApiService);
  cola: any[] = [];
  error = '';
  ok = '';

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.api.get<any[]>('erp/cola/').subscribe({
      next: (data) => this.cola = data,
      error: (e) => this.error = mensajeError(e)
    });
  }

  procesar() {
    this.error = this.ok = '';
    this.api.post('erp/cola/procesar/').subscribe({
      next: () => {
        this.ok = 'Cola procesada correctamente.';
        this.cargar(); // Recargamos la tabla para ver los cambios
      },
      error: (e) => this.error = mensajeError(e)
    });
  }
}