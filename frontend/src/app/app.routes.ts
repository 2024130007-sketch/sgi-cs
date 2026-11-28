import { Routes } from '@angular/router';
import { authGuard, rolGuard } from './core/guards';
import { ShellComponent } from './layout/shell.component';

const MOVER = ['ADMINISTRADOR', 'JEFE_ALMACEN', 'OPERARIO'];

export const routes: Routes = [
  { path: 'login', loadComponent: () => import('./features/auth/login.component').then((m) => m.LoginComponent) },
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'stock' },
      { path: 'stock', loadComponent: () => import('./features/inventario/stock.component').then((m) => m.StockComponent) },
      { path: 'ingresos', canActivate: [rolGuard], data: { roles: MOVER }, loadComponent: () => import('./features/inventario/ingreso.component').then((m) => m.IngresoComponent) },
      { path: 'salidas', canActivate: [rolGuard], data: { roles: MOVER }, loadComponent: () => import('./features/inventario/salida.component').then((m) => m.SalidaComponent) },
      { path: 'transferencias', canActivate: [rolGuard], data: { roles: MOVER }, loadComponent: () => import('./features/transferencias/transferencias.component').then((m) => m.TransferenciasComponent) },
      { path: 'kardex', loadComponent: () => import('./features/inventario/kardex.component').then((m) => m.KardexComponent) },
      { path: 'productos', loadComponent: () => import('./features/productos/productos.component').then((m) => m.ProductosComponent) },
      { path: 'almacenes', loadComponent: () => import('./features/almacenes/almacenes.component').then((m) => m.AlmacenesComponent) },
      { path: 'proveedores', loadComponent: () => import('./features/proveedores/proveedores.component').then((m) => m.ProveedoresComponent) },
      { path: 'reglas', canActivate: [rolGuard], data: { roles: ['ADMINISTRADOR', 'JEFE_ALMACEN'] }, loadComponent: () => import('./features/reposicion/reglas.component').then((m) => m.ReglasComponent) },
      { path: 'alertas', loadComponent: () => import('./features/reposicion/alertas.component').then((m) => m.AlertasComponent) },
      { path: 'usuarios', canActivate: [rolGuard], data: { roles: ['ADMINISTRADOR'] }, loadComponent: () => import('./features/usuarios/usuarios.component').then((m) => m.UsuariosComponent) },
      { path: 'ajustes', canActivate: [rolGuard], data: { roles: ['ADMINISTRADOR', 'JEFE_ALMACEN'] }, loadComponent: () => import('./features/ajustes/ajuste.component').then((m) => m.AjusteComponent) },
      { path: 'bajas', canActivate: [rolGuard], data: { roles: ['ADMINISTRADOR', 'JEFE_ALMACEN'] }, loadComponent: () => import('./features/ajustes/baja.component').then((m) => m.BajaComponent) },
      { path: 'trazabilidad', loadComponent: () => import('./features/inventario/trazabilidad.component').then((m) => m.TrazabilidadComponent) },
      { path: 'ordenes-compra', canActivate: [rolGuard], data: { roles: ['ADMINISTRADOR', 'JEFE_ALMACEN', 'COMPRADOR'] }, loadComponent: () => import('./features/compras/ordenes.component').then((m) => m.OrdenesComponent) },
      { path: 'aprobacion-ordenes', canActivate: [rolGuard], data: { roles: ['ADMINISTRADOR', 'JEFE_ALMACEN'] }, loadComponent: () => import('./features/compras/aprobacion.component').then((m) => m.AprobacionComponent) },
      { path: 'recepcion', canActivate: [rolGuard], data: { roles: MOVER }, loadComponent: () => import('./features/recepciones/recepcion.component').then((m) => m.RecepcionComponent) },
      { path: 'envios', canActivate: [rolGuard], data: { roles: ['ADMINISTRADOR', 'JEFE_ALMACEN', 'COMPRADOR'] }, loadComponent: () => import('./features/notificaciones/envios.component').then((m) => m.EnviosComponent) },
      { path: 'auditoria', canActivate: [rolGuard], data: { roles: ['ADMINISTRADOR'] }, loadComponent: () => import('./features/auditoria/auditoria.component').then((m) => m.AuditoriaComponent) },
      { path: 'respaldos', canActivate: [rolGuard], data: { roles: ['ADMINISTRADOR'] }, loadComponent: () => import('./features/respaldos/respaldos.component').then((m) => m.RespaldosComponent) },
      { path: 'reportes', loadComponent: () => import('./features/reportes/reportes.component').then((m) => m.ReportesComponent) },
      { path: 'erp', canActivate: [rolGuard], data: { roles: ['ADMINISTRADOR', 'JEFE_ALMACEN'] }, loadComponent: () => import('./features/erp/erp.component').then((m) => m.ErpComponent) },
      { path: '**', redirectTo: '' },
    ]
  }
];
