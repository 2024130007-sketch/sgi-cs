import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService, Rol } from '../core/auth.service';

interface Opcion { ruta: string; texto: string; roles?: Rol[]; grupo: string; }

@Component({
  selector: 'app-shell',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="layout">
      <aside class="menu">
        <h2>SGI-CS</h2>
        <p class="usuario">{{ auth.usuario?.email }}</p>
        @for (g of grupos; track g) {
          <h4>{{ g }}</h4>
          @for (o of visibles(g); track o.ruta) {
            <a [routerLink]="o.ruta" routerLinkActive="activo">{{ o.texto }}</a>
          }
        }
        <button class="btn-sec salir" (click)="auth.logout()">Cerrar sesión</button>
      </aside>
      <main class="contenido"><router-outlet /></main>
    </div>
  `,
})
export class ShellComponent {
  auth = inject(AuthService);
  grupos = ['Inventario', 'Datos maestros', 'Reposición', 'Administración'];
  
  private opciones: Opcion[] = [
    { grupo: 'Inventario', ruta: '/stock', texto: 'Consulta de stock' },
    { grupo: 'Inventario', ruta: '/ingresos', texto: 'Registrar ingreso', roles: ['ADMINISTRADOR', 'JEFE_ALMACEN', 'OPERARIO'] },
    { grupo: 'Inventario', ruta: '/salidas', texto: 'Registrar salida', roles: ['ADMINISTRADOR', 'JEFE_ALMACEN', 'OPERARIO'] },
    { grupo: 'Inventario', ruta: '/transferencias', texto: 'Transferencias', roles: ['ADMINISTRADOR', 'JEFE_ALMACEN', 'OPERARIO'] },
    { grupo: 'Inventario', ruta: '/kardex', texto: 'Kardex (movimientos)' },
    { grupo: 'Datos maestros', ruta: '/productos', texto: 'Productos' },
    { grupo: 'Datos maestros', ruta: '/almacenes', texto: 'Almacenes' },
    { grupo: 'Datos maestros', ruta: '/proveedores', texto: 'Proveedores' },
    { grupo: 'Reposición', ruta: '/reglas', texto: 'Reglas de reposición', roles: ['ADMINISTRADOR', 'JEFE_ALMACEN'] },
    { grupo: 'Reposición', ruta: '/alertas', texto: 'Bandeja de alertas' },
    { grupo: 'Administración', ruta: '/usuarios', texto: 'Usuarios y roles', roles: ['ADMINISTRADOR'] },
  ];

  visibles(grupo: string) {
    return this.opciones.filter((o) => o.grupo === grupo && (!o.roles || this.auth.tieneRol(...o.roles)));
  }
}