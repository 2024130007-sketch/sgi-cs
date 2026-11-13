import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const esLogin = req.url.includes('/auth/login');
  const token = auth.token;
  const peticion = token && !esLogin ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : req;
  return next(peticion).pipe(
    catchError((e) => {
      if (e.status === 401 && !esLogin) auth.logout();
      return throwError(() => e);
    })
  );
};