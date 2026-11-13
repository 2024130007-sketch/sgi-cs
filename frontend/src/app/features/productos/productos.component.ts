
import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, mensajeError } from '../../core/api.service';

interface CodigoBarras {
  id: number;
  codigo: string;
  fecha_registro: string;
}

interface Producto {
  id: number;
  sku: string;
  nombre: string;
  descripcion: string;
  marca: string;
  unidad_medida: string;
  precio: string;
  activo: boolean;
  fecha_creacion: string;
  codigos_barras: CodigoBarras[];
}

@Component({
  selector: 'app-productos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <h1>Gestión de productos</h1>

    <div class="tarjeta">
      <h2>{{ editando ? 'Editar producto' : 'Registrar producto' }}</h2>

      <form (ngSubmit)="guardar()">
        <div class="fila">
          <label>SKU
            <input name="sku" [(ngModel)]="form.sku" required>
          </label>

          <label>Nombre
            <input name="nombre" [(ngModel)]="form.nombre" required>
          </label>

          <label>Marca
            <input name="marca" [(ngModel)]="form.marca">
          </label>

          <label>Unidad de medida
            <select name="unidad_medida"
              [(ngModel)]="form.unidad_medida">
              <option value="UNIDAD">Unidad</option>
              <option value="CAJA">Caja</option>
              <option value="PAQUETE">Paquete</option>
              <option value="KILOGRAMO">Kilogramo</option>
              <option value="LITRO">Litro</option>
            </select>
          </label>

          <label>Precio
            <input type="number" name="precio"
              [(ngModel)]="form.precio"
              min="0" step="0.01" required>
          </label>
        </div>

        <label>Descripción
          <textarea name="descripcion"
            [(ngModel)]="form.descripcion"
            rows="3"></textarea>
        </label>

        <label *ngIf="editando">
          <input type="checkbox" name="activo"
            [(ngModel)]="form.activo">
          Producto activo
        </label>

        <p class="error" *ngIf="error">{{ error }}</p>
        <p class="ok" *ngIf="mensaje">{{ mensaje }}</p>

        <button type="submit" [disabled]="cargando">
          {{ editando ? 'Guardar cambios' : 'Registrar producto' }}
        </button>

        <button type="button" class="btn-sec" (click)="limpiar()">
          Cancelar
        </button>
      </form>
    </div>

    <div class="tarjeta">
      <h2>Productos registrados</h2>

      <div class="fila">
        <label>Buscar producto
          <input [(ngModel)]="buscar" name="buscar"
            placeholder="SKU, nombre o marca">
        </label>

        <button type="button" (click)="cargar()">Buscar</button>
      </div>

      <p *ngIf="cargando">Cargando productos...</p>

      <div style="overflow-x:auto">
        <table>
          <thead>
            <tr>
              <th>SKU</th>
              <th>Producto</th>
              <th>Marca</th>
              <th>Unidad</th>
              <th>Precio</th>
              <th>Estado</th>
              <th>Códigos de barras</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr *ngFor="let p of productos">
              <td>{{ p.sku }}</td>
              <td>{{ p.nombre }}</td>
              <td>{{ p.marca || '-' }}</td>
              <td>{{ p.unidad_medida }}</td>
              <td>S/ {{ p.precio }}</td>
              <td>{{ p.activo ? 'Activo' : 'Inactivo' }}</td>

              <td>
                <div *ngFor="let c of p.codigos_barras">
                  {{ c.codigo }}
                </div>
                <span *ngIf="p.codigos_barras.length === 0">
                  Sin códigos
                </span>
                <button type="button" class="btn-chico"
                  (click)="agregarCodigo(p)">
                  + Código
                </button>
              </td>

              <td>
                <button type="button" class="btn-chico"
                  (click)="editar(p)">
                  Editar
                </button>

                <button type="button"
                  class="btn-chico btn-peligro"
                  (click)="eliminar(p)">
                  Eliminar
                </button>
              </td>
            </tr>

            <tr *ngIf="productos.length === 0">
              <td colspan="8" class="vacio">
                No hay productos registrados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
})
export class ProductosComponent implements OnInit {
  private api = inject(ApiService);

  productos: Producto[] = [];
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
      sku: '',
      nombre: '',
      descripcion: '',
      marca: '',
      unidad_medida: 'UNIDAD',
      precio: '0.00',
      activo: true
    };
  }

  cargar() {
    this.cargando = true;
    this.error = '';

    this.api.get<Producto[]>('productos/', {
      buscar: this.buscar
    }).subscribe({
      next: (datos) => {
        this.productos = datos;
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

    const datos = { ...this.form };

    const peticion = this.editando
      ? this.api.put(`productos/${this.idEditando}/`, datos)
      : this.api.post('productos/', datos);

    peticion.subscribe({
      next: () => {
        this.mensaje = this.editando
          ? 'Producto actualizado correctamente.'
          : 'Producto registrado correctamente.';

        this.limpiar();
        this.cargar();
      },
      error: (e) => {
        this.error = mensajeError(e);
        this.cargando = false;
      }
    });
  }

  editar(p: Producto) {
    this.editando = true;
    this.idEditando = p.id;

    this.form = {
      sku: p.sku,
      nombre: p.nombre,
      descripcion: p.descripcion,
      marca: p.marca,
      unidad_medida: p.unidad_medida,
      precio: p.precio,
      activo: p.activo
    };

    this.error = '';
    this.mensaje = '';
  }

  eliminar(p: Producto) {
    if (!confirm(`¿Eliminar el producto ${p.nombre}?`)) return;

    this.api.delete(`productos/${p.id}/`).subscribe({
      next: () => {
        this.mensaje = 'Producto eliminado correctamente.';
        this.cargar();
      },
      error: (e) => {
        this.error = mensajeError(e);
      }
    });
  }

  agregarCodigo(p: Producto) {
    const codigo = prompt(
      `Ingrese el código de barras para ${p.nombre}:`
    );

    if (!codigo?.trim()) return;

    this.api.post('codigos-barras/', {
      producto: p.id,
      codigo: codigo.trim()
    }).subscribe({
      next: () => {
        this.mensaje = 'Código de barras registrado correctamente.';
        this.cargar();
      },
      error: (e) => {
        this.error = mensajeError(e);
      }
    });
  }

  limpiar() {
    this.form = this.formularioVacio();
    this.editando = false;
    this.idEditando = null;
    this.cargando = false;
  }
}
