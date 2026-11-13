import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { API_URL } from './config';

export function mensajeError(e: any): string {
  if (e?.status === 0) return 'No se pudo conectar con el servidor. Verifique que el backend esté en ejecución.';
  if (e?.status === 403) return e?.error?.detail || 'No tiene permiso para realizar esta acción.';
  const err = e?.error;
  if (!err) return 'Ocurrió un error inesperado.';
  if (typeof err === 'string') return 'Error del servidor. Intente nuevamente.';
  if (Array.isArray(err)) return err.join(' ');
  if (err.detail) return String(err.detail);
  const partes: string[] = [];
  for (const [campo, valor] of Object.entries(err)) {
    const txt = Array.isArray(valor) ? valor.join(' ') : typeof valor === 'object' ? JSON.stringify(valor) : String(valor);
    partes.push(campo === 'non_field_errors' ? txt : `${campo}: ${txt}`);
  }
  return partes.join(' | ');
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);

  get<T>(ruta: string, params?: Record<string, any>): Observable<T> {
    let p = new HttpParams();
    for (const [k, v] of Object.entries(params ?? {})) {
      if (v != null && v != undefined && v != '') p = p.set(k, String(v));
    }
    return this.http.get<T>(`${API_URL}/${ruta}`, { params: p });
  }

  post<T>(ruta: string, cuerpo: any = {}): Observable<T> {
    return this.http.post<T>(`${API_URL}/${ruta}`, cuerpo);
  }

  put<T>(ruta: string, cuerpo: any): Observable<T> {
    return this.http.put<T>(`${API_URL}/${ruta}`, cuerpo);
  }

  delete<T>(ruta: string): Observable<T> {
    return this.http.delete<T>(`${API_URL}/${ruta}`);
  }
}