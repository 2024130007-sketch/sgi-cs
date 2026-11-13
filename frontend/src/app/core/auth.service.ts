import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { tap } from 'rxjs';
import { API_URL } from './config';

export type Rol = 'ADMINISTRADOR' | 'JEFE_ALMACEN' | 'OPERARIO' | 'COMPRADOR';

export interface UsuarioSesion {
  id: number;
  email: string;
  first_name: string;
  rol: Rol;
  rol_display: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  get token(): string | null {
    try { return localStorage.getItem('sgi_token'); } catch { return null; }
  }
  get usuario(): UsuarioSesion | null {
    try { return JSON.parse(localStorage.getItem('sgi_usuario') || 'null'); } catch { return null; }
  }
  get autenticado(): boolean {
    return !!this.token;
  }

  tieneRol(...roles: Rol[]): boolean {
    const u = this.usuario;
    return !!u && roles.includes(u.rol);
  }

  login(email: string, password: string) {
    return this.http.post<any>(`${API_URL}/auth/login`, { email, password }).pipe(
      tap((r) => {
        localStorage.setItem('sgi_token', r.access);
        localStorage.setItem('sgi_usuario', JSON.stringify(r.usuario));
      })
    );
  }

  logout() {
    localStorage.removeItem('sgi_token');
    localStorage.removeItem('sgi_usuario');
    this.router.navigate(['/login']);
  }
}