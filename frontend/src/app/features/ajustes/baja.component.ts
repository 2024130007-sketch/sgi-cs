import { Component, OnInit, inject } from '@angular/core'; 
import { FormsModule } from '@angular/forms'; 
import { ApiService, mensajeError } from '../../core/api.service';

@Component({ 
  selector: 'app-baja', 
  imports: [FormsModule], 
  template: ` 
    <h1>Bajas y devoluciones a proveedor</h1> 
    @if (error) { <div class="error">{{ error }}</div> } 
    @if (ok) { <div class="ok">{{ ok }}</div> } 
  
    <div class="tarjeta"> 
      <form (ngSubmit)="registrar()"> 
        <div class="fila"> 
          <label>Almacén 
            <select name="almacen" [(ngModel)]="almacen" (ngModelChange)="cargarStock()"> 
              <option [ngValue]="null">Seleccione...</option> 
              @for (a of almacenes; track a.id) { <option [ngValue]="a.id">{{ a.nombre }}</option> } 
            </select> 
          </label> 
          <label>Producto / lote 
            <select name="existencia" [(ngModel)]="form.existencia"> 
              <option [ngValue]="null">Seleccione...</option> 
              @for (e of existencias; track e.id) { 
                <option [ngValue]="e.id">{{ e.sku }} {{ e.producto }} · lote {{ e.lote_numero }} · vence {{ 
e.vencimiento || '—' }} · disp. {{ e.disponible }}</option> 
              } 
            </select> 
          </label> 
        </div> 
        <div class="fila" style="margin-top:10px"> 
          <label>Tipo 
            <select name="tipo" [(ngModel)]="form.tipo"> 
              <option value="DANO">Producto dañado</option> 
              <option value="VENCIMIENTO">Vencimiento</option> 
              <option value="DEVOLUCION">Devolución a proveedor</option> 
            </select> 
          </label> 
          <label class="chico">Cantidad<input name="cantidad" type="number" min="1" [(ngModel)]="form.cantidad" 
/></label> 
          <label>Motivo<input name="motivo" [(ngModel)]="form.motivo" /></label> 
          @if (form.tipo === 'DEVOLUCION') { 
            <label>Proveedor 
              <select name="proveedor" [(ngModel)]="form.proveedor"> 
                <option [ngValue]="null">Seleccione...</option> 
                @for (p of proveedores; track p.id) { <option [ngValue]="p.id">{{ p.razon_social }}</option> } 
              </select> 
            </label> 
          } 
          <button type="submit" class="btn-peligro">Registrar baja</button> 
        </div> 
      </form> 
    </div> 
  
    <table> 
      
<thead><tr><th>Fecha</th><th>Tipo</th><th>Almacén</th><th>Producto</th><th>Lote</th><th>Cant.</th><th>Motivo</th><th
>Proveedor</th></tr></thead> 
      <tbody> 
        @for (b of bajas; track b.id) { 
          <tr><td>{{ b.fecha.substring(0, 16).replace('T', ' ') }}</td><td>{{ b.tipo_display }}</td><td>{{ 
b.almacen_nombre }}</td> 
            <td>{{ b.sku }} {{ b.producto }}</td><td>{{ b.lote_numero }}</td><td>{{ b.cantidad }}</td><td>{{ 
b.motivo }}</td><td>{{ b.proveedor_nombre || '—' }}</td></tr> 
        } @empty { <tr><td colspan="8" class="vacio">Aún no hay bajas registradas.</td></tr> } 
      </tbody> 
    </table> 
  `, 
}) 
export class BajaComponent implements OnInit { 
  private api = inject(ApiService); 
  almacenes: any[] = []; 
  proveedores: any[] = []; 
  existencias: any[] = []; 
  bajas: any[] = []; 
  almacen: number | null = null; 
  form: any = this.vacio(); 
  error = ''; 
  ok = ''; 
  
  vacio() { return { existencia: null, tipo: 'DANO', cantidad: 1, motivo: '', proveedor: null }; } 
  
  ngOnInit() { 
    this.api.get<any[]>('almacenes/').subscribe((d) => (this.almacenes = d.filter((a) => a.activo))); 
    this.api.get<any[]>('proveedores/').subscribe((d) => (this.proveedores = d.filter((p) => p.activo))); 
    this.cargar(); 
  } 
  cargar() { this.api.get<any[]>('bajas/').subscribe((d) => (this.bajas = d)); } 
  
  cargarStock() { 
    this.form.existencia = null; 
    this.existencias = []; 
    if (this.almacen) this.api.get<any[]>('inventario/stock/', { almacen: this.almacen }).subscribe((d) => 
(this.existencias = d)); 
  } 
  
  registrar() { 
    this.error = this.ok = ''; 
    const f = this.form; 
    if (!f.existencia) { this.error = 'Seleccione el producto y lote.'; return; } 
    if (!f.cantidad || f.cantidad < 1) { this.error = 'La cantidad debe ser mayor a cero.'; return; } 
    if (!f.motivo.trim()) { this.error = 'Indique el motivo de la baja.'; return; } 
    if (f.tipo === 'DEVOLUCION' && !f.proveedor) { this.error = 'Seleccione el proveedor de la devolución.'; return; 
} 
    this.api.post('bajas/', f).subscribe({ 
      next: () => { this.ok = 'Baja registrada y descontada del stock.'; this.form = this.vacio(); 
this.cargarStock(); this.cargar(); }, 
      error: (e) => (this.error = mensajeError(e)), 
    }); 
  } 
} 