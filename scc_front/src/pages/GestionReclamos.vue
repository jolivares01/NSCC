<template>
  <div class="content">
    <div class="row">
      <div v-if="role === 'ROL_0002'" class="col-md-12">
        <card>
          <template slot="header">
            <h4 class="title">Generar Nuevo Reclamo</h4>
          </template>
          <div class="row">
            <div class="col-md-12">
              <base-input label="Descripción detallada"
                          v-model="newClaim.desc_claims"
                          type="text"
                          placeholder="Indique el motivo de su reclamo...">
              </base-input>
              <button class="btn btn-primary" @click="crearTicket" :disabled="loading">
                <i class="tim-icons icon-send"></i> Crear Ticket INC
              </button>
            </div>
          </div>
        </card>
      </div>

      <div class="col-md-12">
        <card>
          <template slot="header">
            <h4 class="title">{{ role === 'ROL_0001' ? 'Tickets Pendientes por Atender' : 'Mis Reclamos en Proceso' }}</h4>
          </template>
          <div class="table-responsive">
            <table class="table tablesorter">
              <thead class="text-primary">
                <tr>
                  <th>ID Ticket</th>
                  <th>{{ role === 'ROL_0001' ? 'Agente' : 'Estado' }}</th>
                  <th>Descripción</th>
                  <th>Fecha Creación</th>
                  <th class="text-center">Acción</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ticket in tickets" :key="ticket.id_inc_claims">
                  <td><span class="badge badge-info">{{ ticket.id_inc_claims }}</span></td>
                  <td>{{ role === 'ROL_0001' ? ticket.agente : ticket.status }}</td>
                  <td>{{ ticket.desc_claims }}</td>
                  <td>{{ formatDate(ticket.created_dt) }}</td>
                  <td class="text-center">
                    <button v-if="role === 'ROL_0001'" 
                            class="btn btn-sm btn-success" 
                            @click="prepararRespuesta(ticket)">
                      Responder
                    </button>
                    <span v-else class="text-muted small">Esperando respuesta...</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </card>
      </div>

      <div class="col-md-12 mt-4">
        <card>
          <template slot="header">
            <div class="row">
              <div class="col-md-6">
                <h4 class="title">Historial de Tickets Atendidos</h4>
              </div>
              <div class="col-md-6 d-flex justify-content-end align-items-center">
                <input type="date" v-model="filter.start" class="form-control form-control-sm mr-2" style="max-width: 150px;">
                <span class="mr-2">al</span>
                <input type="date" v-model="filter.end" class="form-control form-control-sm mr-2" style="max-width: 150px;">
                <button class="btn btn-sm btn-info" @click="consultarAtendidos">
                  <i class="tim-icons icon-zoom-split"></i> Filtrar
                </button>
              </div>
            </div>
          </template>

          <div class="table-responsive">
            <table class="table tablesorter">
              <thead class="text-primary">
                <tr>
                  <th>ID</th>
                  <th>Agente</th>
                  <th>Descripción</th>
                  <th v-if="role === 'ROL_0001'">Cerrado por</th>
                  <th>Gestionado</th>
                </tr>
              </thead>
              <tbody>
              <tr v-for="h in history" :key="h.id_inc_claims">
  <td><span class="badge badge-default">{{ h.id_inc_claims }}</span></td>
  <td>{{ h.agente }}</td>
  <td>{{ h.desc_claims }}</td>
  <td><span class="text-info">{{ h.changed_who || 'Admin' }}</span></td>
  <td>{{ formatDate(h.change_dt) }}</td>
  <td>
    <button class="btn btn-simple btn-sm btn-info" @click="verDetalleAtendido(h)">
      Ver Respuesta
    </button>
  </td>
</tr>
              </tbody>
            </table>
          </div>
        </card>
      </div>
    </div>

   <modal :show.sync="showModal" headerClasses="justify-content-center">
  <template slot="header">
    <h4 class="title" style="color: #2b3553;">Responder al Ticket: {{ selectedTicket.id_inc_claims }}</h4>
  </template>
  <div class="row">
    <div class="col-md-12">
      <label class="text-dark">Mensaje para el Agente:</label>
      <textarea class="form-control text-dark" 
                v-model="adminResponse" 
                rows="4" 
                style="border: 1px solid #2b3553; color: #000 !important; background-color: #fff !important;">
      </textarea>
    </div>
  </div>
  <template slot="footer">
    <button class="btn btn-secondary" @click="showModal = false">Cancelar</button>
    <button class="btn btn-primary" @click="enviarRespuesta">Enviar y Finalizar</button>
  </template>
</modal>

    <modal :show.sync="showDetailModal">
  <template slot="header">
    <h4 class="title" style="color: #2b3553;">Detalle Ticket: {{ detailTicket.id_inc_claims }}</h4>
  </template>
  <div class="row">
    <div class="col-md-12">
      <p class="text-dark"><strong>Descripción:</strong> {{ detailTicket.desc_claims }}</p>
      <hr>
      <p class="text-dark">
        <strong>Respuesta del Admin:</strong> 
        {{ detailTicket.user_response_message || 'Sin respuesta detallada' }}
      </p>
    </div>
  </div>
  <template slot="footer">
    <button class="btn btn-primary" @click="showDetailModal = false">Cerrar</button>
  </template>
</modal>
  </div>
</template>

<script>
import axios from 'axios';
import Modal from '@/components/Modal';

export default {
  components: { Modal },
  data() {
    return {
      role: localStorage.getItem('user_role'),
      username: localStorage.getItem('user_name'),
      tickets: [],
      history: [],
      loading: false,
      showModal: false,
      showDetailModal: false,
      adminResponse: '',
      selectedTicket: {},
      detailTicket: {},
      newClaim: { desc_claims: '' },
      filter: {
        start: new Date().toISOString().split('T')[0],
        end: new Date().toISOString().split('T')[0]
      }
    };
  },
  methods: {
    async cargarTickets() {
      try {
        const res = await axios.get('http://localhost:8000/api/v1/claims/list-open', {
          params: { username: this.username, id_rol: this.role }
        });
        this.tickets = res.data;
      } catch (err) {
        this.$notify({ type: 'danger', message: 'Error al cargar tickets abiertos' });
      }
    },
    async consultarAtendidos() {
      try {
        const res = await axios.get('http://localhost:8000/api/v1/claims/list-attended', {
          params: {
            id_rol: this.role,
            username: this.role === 'ROL_0002' ? this.username : null,
            start_date: this.filter.start,
            end_date: this.filter.end
          }
        });
        this.history = res.data;
      } catch (err) {
        this.$notify({ type: 'danger', message: 'Error al consultar historial' });
      }
    },
    async crearTicket() {
      if (!this.newClaim.desc_claims) return;
      this.loading = true;
      try {
        await axios.post('http://localhost:8000/api/v1/claims/create-claim', {
          agente: this.username,
          desc_claims: this.newClaim.desc_claims
        });
        this.newClaim.desc_claims = '';
        this.cargarTickets();
        this.$notify({ type: 'success', message: 'Ticket INC generado correctamente' });
      } catch (err) {
        this.$notify({ type: 'danger', message: 'Error al crear el ticket' });
      } finally {
        this.loading = false;
      }
    },
    prepararRespuesta(ticket) {
      this.selectedTicket = ticket;
      this.adminResponse = '';
      this.showModal = true;
    },
    verDetalleAtendido(ticket) {
      this.detailTicket = ticket;
      this.showDetailModal = true;
    },
    async enviarRespuesta() {
  try {
    await axios.post('http://localhost:8000/api/v1/claims/respond-claim', {
      id_inc_claims: this.selectedTicket.id_inc_claims,
      user_response_message: this.adminResponse,
      admin_user: this.username // Enviamos el usuario logueado (localStorage)
    });
    this.showModal = false;
    this.cargarTickets();
    this.consultarAtendidos();
    this.$notify({ type: 'success', message: 'Respuesta enviada y auditoría registrada' });
  } catch (err) {
    this.$notify({ type: 'danger', message: 'Error al procesar la respuesta' });
  }
},
    formatDate(date) {
      if (!date) return 'N/A';
      return new Date(date).toLocaleString('es-VE');
    }
  },
  mounted() {
    this.cargarTickets();
    this.consultarAtendidos();
  }
}
</script>