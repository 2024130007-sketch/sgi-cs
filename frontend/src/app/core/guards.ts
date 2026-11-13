import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService, Rol } from './auth.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.autenticado ? true : inject(Router).createUrlTree(['/login']);
};

export const rolGuard: CanActivateFn = (route) => {
  const auth = inject(AuthService);
  const roles = (route.data['roles'] ?? []) as Rol[];
  return roles.length === 0 || auth.tieneRol(...roles) ? true : inject(Router).createUrlTree(['/stock']);
};