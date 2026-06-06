<template>
  <div class="content">
    <div class="row">
      <div class="col-12">
        <card class="card-shadow">
          <template slot="header">
            <h4 class="card-title text-digitel-purple title-bold">
              <i class="tim-icons icon-upload text-primary mr-2"></i> 
              Carga Masiva de Comisiones Especiales
            </h4>
          </template>

          <div 
            class="upload-area" 
            :class="{ 'dragging': isDragging }"
            @dragover.prevent="isDragging = true" 
            @dragleave.prevent="isDragging = false" 
            @drop.prevent="handleDrop"
            @click="$refs.fileInput.click()"
          >
            <input 
              type="file" 
              ref="fileInput" 
              class="d-none" 
              accept=".txt" 
              @change="handleFileSelect"
            >
            
            <div v-if="!file" class="py-4 text-center">
              <i class="tim-icons icon-paper display-1 text-muted"></i>
              <p class="mt-3 text-dark">Arrastre su archivo <b>.txt</b> aquí o haga clic para seleccionar</p>
              <span class="badge badge-default">DELIMITADOR: { | CAMPOS: 7</span>
            </div>

            <div v-else class="py-4 text-center animated fadeIn">
              <i class="tim-icons icon-check-2 display-1 text-success"></i>
              <h4 class="mt-2 text-dark font-weight-bold">{{ file.name }}</h4>
              <p class="text-muted small">{{ (file.size / 1024).toFixed(2) }} KB</p>
              <button class="btn btn-link text-danger" @click.stop="file = null">Cambiar archivo</button>
            </div>
          </div>

          <div class="text-center mt-4" v-if="file">
            <button 
              class="btn btn-primary btn-lg btn-round px-5 shadow" 
              @click="uploadFile" 
              :disabled="loading"
            >
              <span v-if="!loading">SUBIR A BASE DE DATOS</span>
              <span v-else><i class="fa fa-spinner fa-spin mr-2"></i> PROCESANDO...</span>
            </button>
          </div>
        </card>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ComisionesEspeciales',
  data() {
    return {
      file: null,
      isDragging: false,
      loading: false
    };
  },
  methods: {
    handleDrop(e) {
      this.isDragging = false;
      const file = e.dataTransfer.files[0];
      if (file && file.name.endsWith('.txt')) {
        this.file = file;
      } else {
        alert("Por favor, seleccione un archivo .txt válido");
      }
    },
    handleFileSelect(e) {
      if (e.target.files.length > 0) {
        this.file = e.target.files[0];
      }
    },
    async uploadFile() {
      if (!this.file) return;

      this.loading = true;
      const formData = new FormData();
      formData.append('file', this.file);

      // FORZAMOS LA URL AL GATEWAY (127.0.0.1 suele ser más estable para CORS que 'localhost')
      const urlGateway = 'http://localhost:8000/api/v1/calculation/special-commissions/upload';

      try {
        console.log("Iniciando petición de carga masiva...");
        
        // Usamos una configuración de Axios que ignore la baseURL global
        const res = await axios({
          method: 'post',
          url: urlGateway,
          data: formData,
          headers: { 
            'Content-Type': 'multipart/form-data'
          },
          // Importante: esto asegura que no se use prefijos extraños de la instancia global
          baseURL: '' 
        });

        alert("¡Éxito! " + (res.data.message || "Archivo procesado."));
        this.file = null;
        
      } catch (e) {
        console.error("DETALLE ERROR AXIOS:", e);
        
        if (e.code === 'ERR_NETWORK' || !e.response) {
          alert("Error de Red: No se pudo conectar con el Gateway (127.0.0.1:8080).\n\nVerifique:\n1. Que el Gateway esté encendido.\n2. Que el Firewall no bloquee el puerto 8080.\n3. Que python-multipart esté instalado.");
        } else {
          // El servidor sí respondió, pero con error (404, 500, etc.)
          const errorDetail = e.response.data?.detail || "Error interno";
          alert(`Error ${e.response.status}: ${JSON.stringify(errorDetail)}`);
        }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.text-digitel-purple { color: #5C068C !important; }
.title-bold { font-weight: 800; }

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8f9fe;
  min-height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.upload-area:hover, .upload-area.dragging {
  border-color: #5C068C;
  background: rgba(92, 6, 140, 0.05);
  transform: scale(1.005);
}

.display-1 { 
  font-size: 4rem; 
  opacity: 0.5;
}

.card-shadow { 
  box-shadow: 0 10px 30px rgba(0,0,0,0.08); 
  border-radius: 15px; 
  border: none;
}

.fadeIn {
  animation: fadeIn 0.4s both;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>