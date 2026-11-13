
import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, mensajeError } from '../../core/api.service';

interface Usuario {
  id: number;
  email: string;
  first_name: string;
  rol: string;
  rol_display: string;
  is_active: boolean;
  bloqueado: boolean;
  intentos_fallidos: number;
}

@Component({
  selector: 'app-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <h1>Gestión de usuarios</h1>

    <div class="tarjeta">
      <h2>{{ editando ? 'Editar usuario' : 'Registrar usuario' }}</h2>

      <form (ngSubmit)="guardar()">
        <div class="fila">
          <label>Nombre
            <input name="nombre" [(ngModel)]="form.first_name" required>
          </label>

          <label>Correo electrónico
            <input type="email" name="correo" [(ngModel)]="form.email" required>
          </label>

          <label>Rol
            <select name="rol" [(ngModel)]="form.rol" required>
              <option value="ADMINISTRADOR">Administrador</option>
              <option value="JEFE_ALMACEN">Jefe de almacén</option>
              <option value="OPERARIO">Operario</option>
              <option value="COMPRADOR">Comprador</option>
            </select>
          </label>

          <label>Contraseña
            <input type="password" name="password"
              [(ngModel)]="form.password"
              [required]="!editando"
              placeholder="Mínimo 8 caracteres">
          </label>
        </div>

        <p class="error" *ngIf="error">{{ error }}</p>
        <p class="ok" *ngIf="mensaje">{{ mensaje }}</p>

        <button type="submit" [disabled]="cargando">
          {{ editando ? 'Guardar cambios' : 'Registrar usuario' }}
        </button>
        <button type="button" class="btn-sec" (click)="limpiar()">
          Cancelar
        </button>
      </form>
    </div>

    <div class="tarjeta">
      <h2>Usuarios registrados</h2>

      <div class="fila">
        <label>Buscar
          <input [(ngModel)]="buscar" name="buscar"
            placeholder="Nombre o correo">
        </label>
        <button type="button" (click)="cargar()">Buscar</button>
      </div>

      <p *ngIf="cargando">Cargando usuarios...</p>

      <div style="overflow-x:auto">
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Bloqueo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let u of usuarios">
              <td>{{ u.first_name }}</td>
              <td>{{ u.email }}</td>
              <td>{{ u.rol_display }}</td>
              <td>{{ u.is_active ? 'Activo' : 'Inactivo' }}</td>
              <td>{{ u.bloqueado ? 'Bloqueado' : 'Normal' }}</td>
              <td>
                <button type="button" class="btn-chico"
                  (click)="editar(u)">Editar</button>
                <button type="button" class="btn-chico btn-sec"
                  *ngIf="u.bloqueado"
                  (click)="desbloquear(u)">Desbloquear</button>
                <button type="button" class="btn-chico btn-peligro"
                  *ngIf="u.is_active"
                  (click)="desactivar(u)">Desactivar</button>
              </td>
            </tr>
            <tr *ngIf="usuarios.length === 0">
              <td colspan="6" class="vacio">No hay usuarios registrados.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
})
export class UsuariosComponent implements OnInit {
  private api = inject(ApiService);

  usuarios: Usuario[] = [];
  buscar = '';
  error = '';
  mensaje = '';
  cargando = false;
  editando = false;
  idEditando: number | null = null;

  form = this.formularioVacio();

  ngOnInit() {
    this.cargar();
  }

  formularioVacio() {
    return {
      first_name: '',
      email: '',
      rol: 'OPERARIO',
      password: ''
    };
  }

  cargar() {
    this.cargando = true;
    this.error = '';

    this.api.get<Usuario[]>('usuarios/', { buscar: this.buscar }).subscribe({
      next: (datos) => {
        this.usuarios = datos;
        this.cargando = false;
      },
      error: (e) => {
        this.error = mensajeError(e);
        this.cargando = false;
      }
    });
  }

  guardar() {
    this.error = '';
    this.mensaje = '';
    this.cargando = true;

    const datos: any = { ...this.form };
    if (!datos.password) delete datos.password;

    const peticion = this.editando
      ? this.api.put(`usuarios/${this.idEditando}/`, datos)
      : this.api.post('usuarios/', datos);

    peticion.subscribe({
      next: () => {
        this.mensaje = this.editando
          ? 'Usuario actualizado correctamente.'
          : 'Usuario registrado correctamente.';
        this.limpiar();
        this.cargar();
      },
      error: (e) => {
        this.error = mensajeError(e);
        this.cargando = false;
      }
    });
  }

  editar(u: Usuario) {
    this.editando = true;
    this.idEditando = u.id;
    this.form = {
      first_name: u.first_name,
      email: u.email,
      rol: u.rol,
      password: ''
    };
    this.error = '';
    this.mensaje = '';
  }

  desactivar(u: Usuario) {
    if (!confirm(`¿Desactivar al usuario ${u.email}?`)) return;

    this.api.delete(`usuarios/${u.id}/`).subscribe({
      next: () => {
        this.mensaje = 'Usuario desactivado correctamente.';
        this.cargar();
      },
      error: (e) => this.error = mensajeError(e)
    });
  }

  desbloquear(u: Usuario) {
    this.api.post(`usuarios/${u.id}/desbloquear/`).subscribe({
      next: () => {
        this.mensaje = 'Usuario desbloqueado correctamente.';
        this.cargar();
      },
      error: (e) => this.error = mensajeError(e)
    });
  }

  limpiar() {
    this.form = this.formularioVacio();
    this.editando = false;
    this.idEditando = null;
    this.cargando = false;
  }
}
