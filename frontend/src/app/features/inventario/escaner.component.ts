import { Component, ElementRef, EventEmitter, OnDestroy, Output, ViewChild, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, mensajeError } from '../../core/api.service';

export interface ResultadoEscaneo {
  producto: any;
  lote: string | null;
  serie: string | null;
  vencimiento: string | null;
}

/**
 * Lector de códigos (RF #33): cámara, lector USB (modo teclado) o texto escrito.
 * El backend interpreta el código (barras, SKU o GS1-128) y este componente
 * entrega el producto, el lote y el vencimiento a la pantalla que lo usa.
 */
@Component({
  selector: 'app-escaner',
  imports: [FormsModule],
  template: `
    @if (error) { <div class="error">{{ error }}</div> }
    <div class="fila">
      <label>Escanear o escribir código
        <input [(ngModel)]="codigo" [ngModelOptions]="{ standalone: true }"
               (keydown.enter)="$event.preventDefault(); buscar()" placeholder="Código de barras, SKU o GS1-128" />
      </label>
      <button type="button" (click)="buscar()">Buscar</button>
      <button type="button" (click)="camaraActiva ? detener() : iniciar()">
        {{ camaraActiva ? 'Cerrar cámara' : 'Usar cámara' }}
      </button>
    </div>
    <video #video muted playsinline [hidden]="!camaraActiva"
           style="width:100%;max-width:420px;margin-top:10px;border-radius:8px"></video>
  `,
})
export class EscanerComponent implements OnDestroy {
  private api = inject(ApiService);

  @ViewChild('video', { static: true }) video!: ElementRef<HTMLVideoElement>;
  @Output() escaneado = new EventEmitter<ResultadoEscaneo>();

  codigo = '';
  error = '';
  camaraActiva = false;
  private controles: { stop: () => void } | null = null;

  buscar() {
    const codigo = this.codigo.trim();
    if (!codigo) return;
    this.error = '';
    this.api.post<ResultadoEscaneo>('productos/escaneo/', { codigo }).subscribe({
      next: (r) => { this.codigo = ''; this.escaneado.emit(r); },
      error: (e) => (this.error = mensajeError(e)),
    });
  }

  async iniciar() {
    this.error = '';
    if (!navigator.mediaDevices?.getUserMedia) {
      this.error = 'Este navegador no permite usar la cámara. Escriba el código o use un lector.';
      return;
    }
    this.camaraActiva = true;
    try {
      // se carga solo cuando se usa la cámara, para no agrandar la aplicación
      const [{ BrowserMultiFormatReader }, { DecodeHintType }] = await Promise.all([
        import('@zxing/browser'),
        import('@zxing/library'),
      ]);
      // ASSUME_GS1 conserva el separador FNC1 de los códigos GS1-128
      const lector = new BrowserMultiFormatReader(new Map([[DecodeHintType.ASSUME_GS1, true]]));
      const controles = await lector.decodeFromConstraints(
        { video: { facingMode: 'environment' } },
        this.video.nativeElement,
        (resultado, _error, ctrl) => {
          if (!resultado) return;               // todavía no hay un código en la imagen
          ctrl.stop();
          this.camaraActiva = false;
          this.controles = null;
          this.codigo = resultado.getText();
          this.buscar();
        },
      );
      if (this.camaraActiva) this.controles = controles;
      else controles.stop();                    // se cerró mientras arrancaba
    } catch {
      this.camaraActiva = false;
      this.error = 'No se pudo abrir la cámara. Revise el permiso del navegador o escriba el código.';
    }
  }

  detener() {
    this.controles?.stop();
    this.controles = null;
    this.camaraActiva = false;
  }

  ngOnDestroy() {
    this.detener();
  }
}
