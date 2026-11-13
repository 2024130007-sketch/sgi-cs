import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, mensajeError } from '../../core/api.service';
import { AuthService } from '../../core/auth.service';

/** Vista GestionProveedores (CU-03, RF-10). */
@Component({
  selector: 'app-proveedores',
  imports: [FormsModule],
  template: `
    <h1>Proveedores</h1>
    @if (error) { <div class="error">{{ error }}</div> }
    @if (ok) { <div class="ok">{{ ok }}</div> }
    @if (puedeEditar) {
      <div class="tarjeta">
        <h3>{{ editandoId ? 'Modificar proveedor' : 'Nuevo proveedor' }}</h3>
        <form (ngSubmit)="guardar()" class="fila">
          <label>RUC (11 dígitos)<input name="ruc" maxlength="11" [(ngModel)]="form.ruc" /></label>
          <label>Razón social<input name="razon" [(ngModel)]="form.razon_social" /></label>
          <label>Correo<input name="correo" type="email" [(ngModel)]="form.correo" /></label>
          <label class="chico">Entrega (días)<input name="dias" type="number" min="1" [(ngModel)]="form.tiempo_entrega_dias" /></label>
          <button type="submit">{{ editandoId ? 'Actualizar' : 'Registrar' }}</button>
          @if (editandoId) { <button type="button" class="btn-sec" (click)="limpiar()">Cancelar</button> }
        </form>
      </div>
    }
    <div class="tarjeta fila">
      <label>Buscar por RUC o razón social<input [(ngModel)]="busqueda" (ngModelChange)="cargar()" /></label>
    </div>
    <table>
      <thead><tr><th>RUC</th><th>Razón social</th><th>Correo</th><th>Entrega</th><th>Estado</th><th></th></tr></thead>
      <tbody>
        @for (p of proveedores; track p.id) {
          <tr>
            <td>{{ p.ruc }}</td><td>{{ p.razon_social }}</td><td>{{ p.correo }}</td><td>{{ p.tiempo_entrega_dias }} d</td>
            <td><span class="etiqueta" [class.verde]="p.activo" [class.rojo]="!p.activo">{{ p.activo ? 'Activo' : 'Inactivo' }}</span></td>
            <td>
              @if (puedeEditar) {
                <button class="btn-chico btn-sec" (click)="editar(p)">Editar</button>
                @if (p.activo) { <button class="btn-chico btn-peligro" (click)="desactivar(p)">Desactivar</button> }
              }
            </td>
          </tr>
        } @empty { <tr><td colspan="6" class="vacio">No hay proveedores.</td></tr> }
      </tbody>
    </table>
  `
})
export class ProveedoresComponent implements OnInit {
  private api = inject(ApiService);
  puedeEditar = inject(AuthService).tieneRol('ADMINISTRADOR', 'COMPRADOR');
  proveedores: any[] = [];
  form: any = this.vacio();
  busqueda = '';
  editandoId: number | null = null;
  error = '';
  ok = '';

  vacio() { return { ruc: '', razon_social: '', correo: '', tiempo_entrega_dias: 1 }; }
  ngOnInit() { this.cargar(); }
  cargar() { this.api.get<any[]>('proveedores/', { search: this.busqueda }).subscribe((d) => (this.proveedores = d)); }

  guardar() {
    this.error = this.ok = '';
    const f = this.form;
    if (!/^\d{11}$/.test(f.ruc.trim())) { this.error = 'El RUC debe tener exactamente 11 dígitos.'; return; }
    if (!f.razon_social.trim()) { this.error = 'La razón social es obligatoria.'; return; }
    if (!f.correo.trim()) { this.error = 'El correo es obligatorio.'; return; }
    const peticion = this.editandoId ? this.api.put(`proveedores/${this.editandoId}/`, f) : this.api.post('proveedores/', f);
    peticion.subscribe({
      next: () => { this.ok = this.editandoId ? 'Proveedor actualizado.' : 'Proveedor registrado.'; this.limpiar(); this.cargar(); },
      error: (e) => (this.error = mensajeError(e)),
    });
  }

  editar(p: any) {
    this.editandoId = p.id;
    this.form = { ruc: p.ruc, razon_social: p.razon_social, correo: p.correo, tiempo_entrega_dias: p.tiempo_entrega_dias, activo: p.activo };
    this.ok = this.error = '';
  }

  limpiar() { this.editandoId = null; this.form = this.vacio(); }

  desactivar(p: any) {
    this.api.delete(`proveedores/${p.id}/`).subscribe({
      next: () => { this.ok = 'Proveedor desactivado.'; this.cargar(); },
      error: (e) => (this.error = mensajeError(e)),
    });
  }
}
