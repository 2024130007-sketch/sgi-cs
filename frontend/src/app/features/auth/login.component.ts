
import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth.service';
import { mensajeError } from '../../core/api.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="tarjeta login-caja">
      <h1>SGI-CS</h1>
      <p style="text-align:center">Sistema de Gestión de Inventarios</p>

      <form (ngSubmit)="ingresar()">
        <label>Correo electrónico
          <input type="email" name="email" [(ngModel)]="email"
            required placeholder="usuario@sgi.com">
        </label>

        <label>Contraseña
          <input type="password" name="password" [(ngModel)]="password"
            required placeholder="Ingrese su contraseña">
        </label>

        <p class="error" *ngIf="error">{{ error }}</p>

        <button type="submit" [disabled]="cargando">
          {{ cargando ? 'Ingresando...' : 'Iniciar sesión' }}
        </button>
      </form>
    </div>
  `
})
export class LoginComponent {
  private auth = inject(AuthService);
  private router = inject(Router);

  email = '';
  password = '';
  error = '';
  cargando = false;

  ingresar() {
    this.error = '';
    this.cargando = true;

    this.auth.login(this.email.trim(), this.password).subscribe({
      next: () => this.router.navigateByUrl('/'),
      error: (e) => {
        this.error = mensajeError(e);
        this.cargando = false;
      }
    });
  }
}
