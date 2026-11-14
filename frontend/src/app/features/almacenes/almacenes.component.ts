import { Component, OnInit, inject } from '@angular/core'; 
import { FormsModule } from '@angular/forms'; 
import { ApiService, mensajeError } from '../../core/api.service'; 
import { AuthService } from '../../core/auth.service';

/** Vista GestionAlmacenes (CU-03, RF-09). */ 
@Component({ 
  selector: 'app-almacenes', 
  imports: [FormsModule], 
  template: ` 
    <h1>Almacenes</h1> 
    @if (error) { <div class="error">{{ error }}</div> } 
    @if (ok) { <div class="ok">{{ ok }}</div> } 
 
    @if (puedeEditar) { 
      <div class="tarjeta"> 
        <h3>{{ editandoId ? 'Modificar almacén' : 'Nuevo almacén' }}</h3> 
        <form (ngSubmit)="guardar()" class="fila"> 
          <label>Nombre<input name="nombre" [(ngModel)]="form.nombre" /></label> 
          <label>Dirección<input name="direccion" [(ngModel)]="form.direccion" /></label> 
          @if (editandoId) { <label class="check"><input type="checkbox" name="activo" [(ngModel)]="form.activo" /> 
Activo</label> } 
          <button type="submit">{{ editandoId ? 'Actualizar' : 'Registrar' }}</button> 
          @if (editandoId) { <button type="button" class="btn-sec" (click)="limpiar()">Cancelar</button> } 
        </form> 
      </div> 
    } 
 
    <table> 
      <thead><tr><th>Nombre</th><th>Dirección</th><th>Estado</th><th></th></tr></thead> 
      <tbody> 
        @for (a of almacenes; track a.id) { 
          <tr> 
            <td>{{ a.nombre }}</td><td>{{ a.direccion }}</td> 
            <td><span class="etiqueta" [class.verde]="a.activo" [class.rojo]="!a.activo">{{ a.activo ? 'Activo' : 
'Inactivo' }}</span></td> 
            <td> 
              @if (puedeEditar) { 
                <button class="btn-chico btn-sec" (click)="editar(a)">Editar</button> 
                @if (a.activo) { <button class="btn-chico btn-peligro" (click)="desactivar(a)">Desactivar</button> } 
              } 
            </td> 
          </tr> 
        } @empty { <tr><td colspan="4" class="vacio">No hay almacenes.</td></tr> } 
      </tbody> 
    </table> 
  `, 
}) 
export class AlmacenesComponent implements OnInit { 
  private api = inject(ApiService); 
  puedeEditar = inject(AuthService).tieneRol('ADMINISTRADOR'); 
  almacenes: any[] = []; 
  form: any = { nombre: '', direccion: '', activo: true }; 
  editandoId: number | null = null; 
  error = ''; 
  ok = ''; 
 
  ngOnInit() { this.cargar(); } 
  cargar() { this.api.get<any[]>('almacenes/').subscribe((d) => (this.almacenes = d)); } 
 
  guardar() { 
    this.error = this.ok = ''; 
    if (!this.form.nombre.trim() || !this.form.direccion.trim()) { 
      this.error = 'El nombre y la dirección son obligatorios.'; 
      return; 
    } 
    const peticion = this.editandoId ? this.api.put(`almacenes/${this.editandoId}/`, this.form) : 
this.api.post('almacenes/', this.form); 
    peticion.subscribe({ 
      next: () => { this.ok = this.editandoId ? 'Almacén actualizado.' : 'Almacén registrado.'; this.limpiar(); 
this.cargar(); }, 
      error: (e) => (this.error = mensajeError(e)), 
    }); 
  } 
  editar(a: any) { this.editandoId = a.id; this.form = { nombre: a.nombre, direccion: a.direccion, activo: a.activo }; 
this.ok = this.error = ''; } 
  limpiar() { this.editandoId = null; this.form = { nombre: '', direccion: '', activo: true }; } 
  desactivar(a: any) { 
    this.api.delete(`almacenes/${a.id}/`).subscribe({ 
      next: () => { this.ok = 'Almacén desactivado.'; this.cargar(); }, 
      error: (e) => (this.error = mensajeError(e)), 
    }); 
  } 
} 