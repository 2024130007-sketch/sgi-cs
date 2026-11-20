import { Component, OnInit, inject } from '@angular/core'; 
import { FormsModule } from '@angular/forms'; 
import { ApiService, mensajeError } from '../../core/api.service'; 
  

@Component({ 
  selector: 'app-ajuste', 
  imports: [FormsModule], 
  template: ` 
    <h1>Ajuste de inventario por conteo físico</h1> 
    @if (error) { <div class="error">{{ error }}</div> } 
    @if (ok) { <div class="ok">{{ ok }}</div> } 
  
    <div class="tarjeta"> 
      <form (ngSubmit)="iniciar()" class="fila"> 
        <label>Almacén a contar 
          <select name="almacen" [(ngModel)]="almacen"> 
            <option [ngValue]="null">Seleccione...</option> 
            @for (a of almacenes; track a.id) { <option [ngValue]="a.id">{{ a.nombre }}{{ a.en_conteo ? ' (en 
conteo)' : '' }}</option> } 
          </select> 
        </label> 
        <label>Observación<input name="obs" [(ngModel)]="observacion" /></label> 
        <button type="submit">Iniciar conteo</button> 
      </form> 
      <small>Mientras dura el conteo el almacén no admite ingresos, salidas ni transferencias.</small> 
    </div> 
  
    @if (actual) { 
      <div class="tarjeta"> 
        <h3>AJ-{{ actual.id }} — {{ actual.almacen_nombre }} <span class="etiqueta ambar">{{ actual.estado_display 
}}</span></h3> 
        <table> 
          
<thead><tr><th>SKU</th><th>Producto</th><th>Lote</th><th>Sistema</th><th>Contado</th><th>Diferencia</th></tr></thead
> 
          <tbody> 
            @for (d of actual.detalles; track d.id) { 
              <tr> 
                <td>{{ d.sku }}</td><td>{{ d.producto }}</td><td>{{ d.lote_numero }}</td><td>{{ d.cantidad_sistema 
}}</td> 
                <td> 
                  @if (actual.estado === 'EN_CONTEO') { 
                    <input type="number" min="0" style="width:90px" [name]="'c' + d.id" [(ngModel)]="conteos[d.id]" 
/> 
                  } @else { {{ d.cantidad_contada ?? '—' }} } 
                </td> 
                <td [style.color]="d.diferencia < 0 ? '#991b1b' : d.diferencia > 0 ? '#166534' : ''">{{ d.diferencia 
?? '—' }}</td> 
              </tr> 
            } 
          </tbody> 
        </table> 
        @if (actual.estado === 'EN_CONTEO') { 
          <div class="fila" style="margin-top:10px"> 
            <button class="btn-sec" (click)="guardarConteo()">Guardar conteo</button> 
            <button (click)="cerrar()">Cerrar y aplicar diferencias</button> 
            <button class="btn-peligro" (click)="cancelar()">Cancelar conteo</button> 
          </div> 
        } 
      </div> 
    } 
  
    <h3>Historial de ajustes</h3> 
    <table> 
      
<thead><tr><th>N.º</th><th>Almacén</th><th>Responsable</th><th>Inicio</th><th>Estado</th><th></th></tr></thead> 
      <tbody> 
        @for (a of ajustes; track a.id) { 
          <tr><td>AJ-{{ a.id }}</td><td>{{ a.almacen_nombre }}</td><td>{{ a.usuario_email }}</td> 
            <td>{{ a.fecha_inicio.substring(0, 16).replace('T', ' ') }}</td><td>{{ a.estado_display }}</td> 
            <td><button class="btn-chico btn-sec" (click)="abrir(a)">Ver</button></td></tr> 
        } @empty { <tr><td colspan="6" class="vacio">Aún no hay ajustes.</td></tr> } 
      </tbody> 
    </table> 
  `, 
}) 
export class AjusteComponent implements OnInit { 
  private api = inject(ApiService); 
  almacenes: any[] = []; 
  ajustes: any[] = []; 
  actual: any = null; 
  conteos: Record<number, any> = {}; 
  almacen: number | null = null; 
  observacion = ''; 
  error = ''; 
  ok = ''; 
  
  ngOnInit() { this.cargar(); } 
  
  cargar() { 
    this.api.get<any[]>('almacenes/').subscribe((d) => (this.almacenes = d.filter((a) => a.activo))); 
    this.api.get<any[]>('ajustes/').subscribe((d) => (this.ajustes = d)); 
  } 
  
  abrir(a: any) { 
    this.actual = a; 
    this.conteos = {}; 
    for (const d of a.detalles) this.conteos[d.id] = d.cantidad_contada; 
  } 
  
  iniciar() { 
    this.error = this.ok = ''; 
    if (!this.almacen) { this.error = 'Seleccione el almacén a contar.'; return; } 
    this.api.post<any>('ajustes/', { almacen: this.almacen, observacion: this.observacion }).subscribe({ 
      next: (a) => { this.ok = 'Conteo iniciado. Registre las cantidades contadas.'; this.abrir(a); this.cargar(); 
}, 
      error: (e) => (this.error = mensajeError(e)), 
    }); 
  } 
  
  guardarConteo(despues?: () => void) { 
    this.error = this.ok = ''; 
    const enviar: Record<string, any> = {}; 
    for (const [id, v] of Object.entries(this.conteos)) if (v !== null && v !== undefined && v !== '') enviar[id] = 
String(v); 
    if (!Object.keys(enviar).length) { this.error = 'Indique al menos una cantidad contada.'; return; } 
    this.api.post<any>(`ajustes/${this.actual.id}/conteo/`, { conteos: enviar }).subscribe({ 
      next: (a) => { this.abrir(a); if (despues) despues(); else this.ok = 'Conteo guardado.'; }, 
      error: (e) => (this.error = mensajeError(e)), 
    }); 
  } 
  
  cerrar() { 
    this.guardarConteo(() => { 
      this.api.post<any>(`ajustes/${this.actual.id}/cerrar/`).subscribe({ 
        next: (a) => { this.ok = 'Ajuste cerrado: el stock se corrigió y quedó en el kardex.'; this.abrir(a); 
this.cargar(); }, 
        error: (e) => (this.error = mensajeError(e)), 
      }); 
    }); 
  } 
  
  cancelar() { 
    this.error = this.ok = ''; 
    this.api.post<any>(`ajustes/${this.actual.id}/cancelar/`).subscribe({ 
      next: (a) => { this.ok = 'Conteo cancelado; el almacén vuelve a operar.'; this.abrir(a); this.cargar(); }, 
      error: (e) => (this.error = mensajeError(e)), 
    }); 
  } 
} 