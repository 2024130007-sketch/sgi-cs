import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, mensajeError } from '../../core/api.service';

/** Vista RecepcionOrdenCompra (RF-37 y RF-38). */
@Component({
  selector: 'app-recepcion',
  imports: [FormsModule],
  template: `
    <h1>Recepción de órdenes de compra</h1>
    @if (error) { <div class="error">{{ error }}</div> }
    @if (ok) { <div class="ok">{{ ok }}</div> }

    <div class="tarjeta">
      <form (ngSubmit)="registrar()">
        <div class="fila">
          <label>Orden de compra ID
            <input name="orden" type="number" [(ngModel)]="form.orden_compra" placeholder="Ej: 1" />
          </label>
          <label>Documento / Guía
            <input name="doc" [(ngModel)]="form.documento" placeholder="Guía de remisión" />
          </label>
        </div>
        <div class="fila" style="margin-top:10px">
          <label class="chico">Cantidad recibida
            <input name="cant" type="number" min="1" [(ngModel)]="form.cantidad" />
          </label>
          <button type="submit">Registrar recepción</button>
        </div>
      </form>
    </div>
  `,
})
export class RecepcionComponent implements OnInit {
  private api = inject(ApiService);
  form: any = { orden_compra: null, documento: '', cantidad: 1 };
  error = '';
  ok = '';

  ngOnInit() {
    // Aquí se cargarían las órdenes pendientes en un futuro
  }

  registrar() {
    this.error = this.ok = '';
    if (!this.form.orden_compra || this.form.cantidad <= 0) {
      this.error = 'Complete el ID de la orden y una cantidad mayor a cero.';
      return;
    }

    this.api.post('recepciones/', this.form).subscribe({
      next: () => {
        this.ok = 'Recepción registrada correctamente. El stock ha sido actualizado.';
        this.form = { orden_compra: null, documento: '', cantidad: 1 };
      },
      error: (e) => (this.error = mensajeError(e)),
    });
  }
}