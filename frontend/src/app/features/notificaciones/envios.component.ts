import { DatePipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';

import { ApiService, mensajeError } from '../../core/api.service';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-envios',
  template: `
    <h1>Envío de órdenes y alertas por correo</h1>

    @if (error) {
      <div class="error">{{ error }}</div>
    }
    @if (ok) {
      <div class="ok">{{ ok }}</div>
    }

    <div class="tarjeta">
      <h3>Resumen de alertas</h3>
      <p>Envía un resumen de las alertas abiertas al personal autorizado.</p>
      <button (click)="enviarResumen()" [disabled]="cargandoResumen">
        {{ cargandoResumen ? 'Enviando...' : 'Enviar resumen de alertas' }}
      </button>
    </div>

    <div class="tarjeta">
      <h3>Órdenes de compra</h3>
      <p>Envía las órdenes aprobadas al correo registrado de cada proveedor.</p>

      <table>
        <thead>
          <tr>
            <th>Orden</th>
            <th>Proveedor</th>
            <th>Correo</th>
            <th>Total (S/)</th>
            <th>Estado</th>
            <th>Fecha de envío</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          @for (o of ordenes; track o.id) {
            <tr>
              <td>OC-{{ o.id }}</td>
              <td>{{ o.proveedor_nombre }}</td>
              <td>{{ o.proveedor_correo }}</td>
              <td>{{ o.total }}</td>
              <td>
                <span class="etiqueta"
                  [class.verde]="o.estado === 'ENVIADA'"
                  [class.ambar]="o.estado === 'APROBADA'">
                  {{ o.estado_display }}
                </span>
              </td>
              <td>
                {{ o.fecha_envio ? (o.fecha_envio | date:'short') : 'Sin enviar' }}
              </td>
              <td>
                @if (puedeEnviar && o.estado === 'APROBADA') {
                  <button
                    class="btn-chico"
                    [disabled]="enviandoId === o.id"
                    (click)="enviarOrden(o)">
                    {{ enviandoId === o.id ? 'Enviando...' : 'Enviar al proveedor' }}
                  </button>
                } @else if (o.estado === 'ENVIADA') {
                  <span>Enviada</span>
                } @else {
                  <span>No disponible</span>
                }
              </td>
            </tr>
          } @empty {
            <tr>
              <td colspan="7" class="vacio">No hay órdenes registradas.</td>
            </tr>
          }
        </tbody>
      </table>
    </div>
  `,
  imports: [DatePipe],
})
export class EnviosComponent implements OnInit {
  private api = inject(ApiService);
  private auth = inject(AuthService);

  ordenes: any[] = [];
  error = '';
  ok = '';
  enviandoId: number | null = null;
  cargandoResumen = false;

  get puedeEnviar() {
    return this.auth.tieneRol('ADMINISTRADOR', 'COMPRADOR');
  }

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.api.get<any[]>('compras/ordenes/').subscribe({
      next: (datos) => (this.ordenes = datos),
      error: (e) => (this.error = mensajeError(e)),
    });
  }

  enviarOrden(orden: any) {
    this.error = '';
    this.ok = '';
    this.enviandoId = orden.id;

    this.api.post(
      `notificaciones/ordenes/${orden.id}/enviar/`,
      {},
    ).subscribe({
      next: () => {
        this.ok = `La orden OC-${orden.id} fue enviada al proveedor.`;
        this.enviandoId = null;
        this.cargar();
      },
      error: (e) => {
        this.error = mensajeError(e);
        this.enviandoId = null;
      },
    });
  }

  enviarResumen() {
    this.error = '';
    this.ok = '';
    this.cargandoResumen = true;

    this.api.post('alertas/enviar_resumen/', {}).subscribe({
      next: (resultado: any) => {
        this.ok = `Resumen procesado: ${resultado.enviados} correo(s) enviado(s), ${resultado.alertas} alerta(s).`;
        this.cargandoResumen = false;
      },
      error: (e) => {
        this.error = mensajeError(e);
        this.cargandoResumen = false;
      },
    });
  }
}
