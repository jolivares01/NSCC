<template>
  <div class="content">
    <div class="row">
      <div class="col-12">
        <card>
          <template slot="header">
            <h4 class="card-title text-purple-digitel">
              <i class="tim-icons icon-settings-gear-63 mr-2"></i>
              Configuración de Reglas de Negocio
            </h4>
            <p class="category text-muted">Gestión Paramétrica De Comisiones Por Plan, Servicio Y Operaciones</p>
          </template>
          
          <div v-if="tabActive !== 'catalog'" class="row mb-3">
            <div class="col-md-4 ml-auto">
              <input
                type="text"
                class="form-control"
                placeholder="Buscar en tablas..."
                v-model="searchQuery"
                style="border: 1px solid #5C068C; border-radius: 20px; padding: 0 15px;"
              >
            </div>
          </div>

          <div class="nav-tabs-navigation">
            <div class="nav-tabs-wrapper">
              <ul class="nav nav-tabs custom-nav-tabs">
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: tabActive === 'plans' }" @click.prevent="tabActive = 'plans'" href="#">
                    <i class="tim-icons icon-notes"></i> Planes
                  </a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: tabActive === 'services' }" @click.prevent="tabActive = 'services'" href="#">
                    <i class="tim-icons icon-bullet-list-67"></i> Servicios
                  </a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: tabActive === 'general' }" @click.prevent="tabActive = 'general'" href="#">
                    <i class="tim-icons icon-paper"></i> Reglas Generales (OT)
                  </a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: tabActive === 'catalog' }" @click.prevent="tabActive = 'catalog'" href="#">
                    <i class="tim-icons icon-simple-add"></i> Gestión de Catálogo
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div class="tab-content mt-4">
            
            <div v-if="tabActive === 'plans'">
              <div class="table-responsive">
                <table class="table table-sm custom-table">
                  <thead>
                    <tr>
                      <th class="text-left">PLAN / INSTANCIA</th>
                      <th class="text-center">MONTO / %</th>
                      <th class="text-center">CANAL</th>
                      <th class="text-center">ESTADO</th>
                      <th class="text-right">ACCIONES</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(plan, index) in filteredPlanes" :key="'p-'+index">
                      <td class="text-left">
                        <span class="d-block font-weight-bold plan-name">{{ plan.plan_name }}</span>
                        <small class="text-muted">{{ plan.instance_name }} ({{ plan.id_instance_type }})</small>
                      </td>
                      <td class="text-center">
                        <div class="d-flex flex-column align-items-center">
                          <input type="text" v-model="plan.amount_to_pay" class="form-control editable-input mb-1">
                          <input type="text" v-model="plan.amount_percentage" class="form-control editable-input">
                        </div>
                      </td>
                      <td class="text-center"><badge type="primary" class="channel-badge">{{ plan.channel }}</badge></td>
                      <td class="text-center">
                        <badge :type="!plan.inactive_dt ? 'success' : 'danger'">{{ !plan.inactive_dt ? 'ACTIVO' : 'INACTIVO' }}</badge>
                        <div class="mt-2"><button class="btn btn-xs btn-link p-0 text-status-toggle" @click="toggleStatus(plan)"><u>Cambiar</u></button></div>
                      </td>
                      <td class="text-right">
                        <button class="btn btn-link btn-icon btn-sm action-btn" :class="hasPlanChanged(plan) ? 'btn-warning-pulse' : 'btn-success-static'" @click="confirmSavePlan(plan)" :disabled="loading">
                          <i class="tim-icons icon-check-2"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-if="tabActive === 'services'">
              <div class="table-responsive">
                <table class="table table-sm custom-table">
                  <thead>
                    <tr>
                      <th class="text-left">SERVICIO / ID</th>
                      <th class="text-center">MONTO / %</th>
                      <th class="text-center">CANAL</th>
                      <th class="text-center">ESTADO</th>
                      <th class="text-right">ACCIONES</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(svc, index) in filteredServicios" :key="'s-'+index">
                      <td class="text-left">
                        <span class="font-weight-bold plan-name d-block">{{ svc.display_value }}</span>
                        <small class="text-muted font-weight-bold">{{ svc.id_service }}</small>
                      </td>
                      <td class="text-center">
                        <div class="d-flex flex-column align-items-center">
                          <input type="text" v-model="svc.amount_to_pay" class="form-control editable-input mb-1">
                          <input type="text" v-model="svc.amount_percentage" class="form-control editable-input">
                        </div>
                      </td>
                      <td class="text-center"><badge type="primary" class="channel-badge">{{ svc.channel }}</badge></td>
                      <td class="text-center">
                        <badge :type="!svc.inactive_dt ? 'success' : 'danger'">{{ !svc.inactive_dt ? 'ACTIVO' : 'INACTIVO' }}</badge>
                        <div class="mt-2"><button class="btn btn-xs btn-link p-0 text-status-toggle" @click="toggleStatus(svc)"><u>Cambiar</u></button></div>
                      </td>
                      <td class="text-right">
                        <button class="btn btn-link btn-icon btn-sm action-btn" :class="hasServiceChanged(svc) ? 'btn-warning-pulse' : 'btn-success-static'" @click="confirmSaveService(svc)" :disabled="loading">
                          <i class="tim-icons icon-check-2"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-if="tabActive === 'general'">
              <div class="table-responsive">
                <table class="table table-sm custom-table">
                  <thead>
                    <tr>
                      <th class="text-left">OPERACIÓN / REGLA</th>
                      <th class="text-center">VALORES ($ / %)</th>
                      <th class="text-left">PATRONES</th>
                      <th class="text-center">ESTADO</th>
                      <th class="text-right">ACCIONES</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(rule, index) in filteredReglas" :key="'g-'+index">
                      <td class="text-left" style="min-width: 250px;">
                        <span class="d-block font-weight-bold plan-name">{{ rule.operation_name }}</span>
                        <badge type="default" class="text-muted">{{ rule.operation_code }}</badge>
                        <p class="small text-info mt-1 mb-0">{{ rule.description }}</p>
                      </td>
                      <td class="text-center">
                        <div class="d-flex flex-column align-items-center">
                          <input type="text" v-model="rule.amount_to_pay" class="form-control editable-input mb-1">
                          <input type="text" v-model="rule.amount_percentege" class="form-control editable-input">
                        </div>
                      </td>
                      <td class="text-left">
                        <div v-if="rule.operation_code === 'OT-014'" class="pattern-group">
                           <input type="text" :value="rule.origin_plan_pattern" class="form-control pattern-field-locked mb-1" readonly>
                           <input type="text" :value="rule.destination_plan_pattern" class="form-control pattern-field-locked" readonly>
                        </div>
                        <span v-else class="text-muted italic small">No requiere patrones</span>
                      </td>
                      <td class="text-center">
                        <badge :type="rule.commissionable_flag === 'Y' ? 'success' : 'danger'">{{ rule.commissionable_flag === 'Y' ? 'ACTIVO' : 'INACTIVO' }}</badge>
                        <div class="mt-2"><button class="btn btn-xs btn-link p-0 text-status-toggle" @click="toggleRule(rule)"><u>Cambiar</u></button></div>
                      </td>
                      <td class="text-right">
                        <button class="btn btn-link btn-icon btn-sm action-btn" :class="hasRuleChanged(rule) ? 'btn-warning-pulse' : 'btn-success-static'" @click="confirmSaveRule(rule)">
                          <i class="tim-icons icon-check-2"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-if="tabActive === 'catalog'" class="p-0">
              <div class="row px-4 pt-4">
                <div class="col-md-6 border-right-card">
                  <h5 class="header-section font-weight-800"><i class="tim-icons icon-simple-add"></i> Activar Plan</h5>
                  <div class="form-group">
                    <label class="font-weight-bold">Maestro de Planes</label>
                    <input type="text" class="form-control mb-2" placeholder="Filtrar planes..." v-model="filterPlanText" style="height: 35px; font-size: 0.85rem;">
                    
                    <div class="scroll-area-custom border" style="max-height: 200px; overflow-y: auto; background: white; border-radius: 8px; padding: 10px;">
                      <div v-for="p in filteredCatPlanes" :key="p.id_plan + p.id_instance_type" class="check-item d-flex align-items-center mb-1">
                        <input type="checkbox" :id="'cp-'+p.id_plan+p.id_instance_type" :value="p" v-model="selectedPlansFromCatalog">
                        <label :for="'cp-'+p.id_plan+p.id_instance_type" class="ml-2 mb-0" style="font-size: 0.85rem; color: #333; cursor:pointer;">
                          {{ p.display_value }} <small class="text-purple-digitel">({{ p.id_instance_type }})</small>
                        </label>
                      </div>
                    </div>
                    <div class="mt-2 d-flex justify-content-between">
                      <small class="text-muted">Seleccionados: <b>{{ selectedPlansFromCatalog.length }}</b></small>
                      <button v-if="selectedPlansFromCatalog.length > 0" class="btn btn-link btn-xs p-0 text-danger" @click="selectedPlansFromCatalog = []">Limpiar</button>
                    </div>
                  </div>

                  <div v-if="selectedPlansFromCatalog.length > 0" class="row animate__animated animate__fadeIn">
                    <div class="col-6"><label class="label-tiny">MONTO ($)</label><input v-model="formNewPlan.amount_to_pay" class="form-control editable-input w-100"></div>
                    <div class="col-6"><label class="label-tiny">PORCENTAJE (%)</label><input v-model="formNewPlan.amount_percentage" class="form-control editable-input w-100"></div>
                    <div class="col-12 mt-3">
                      <label class="label-tiny text-left">CANAL</label>
                      <select v-model="formNewPlan.channel" class="form-control custom-select-box">
                        <option v-for="c in catCanales" :key="c.id_channel" :value="c.id_channel">{{ c.id_channel }}</option>
                      </select>
                    </div>
                    <div class="col-12 mt-4">
                      <button class="btn btn-purple-digitel btn-block btn-round" @click="handleCreatePlan">
                        Insertar {{ selectedPlansFromCatalog.length }} Plan(es)
                      </button>
                    </div>
                  </div>
                </div>

                <div class="col-md-6">
                  <h5 class="header-section font-weight-800"><i class="tim-icons icon-settings"></i> Activar Servicio</h5>
                  <div class="form-group">
                    <label class="font-weight-bold">Maestro de Servicios</label>
                    <input type="text" class="form-control mb-2" placeholder="Filtrar servicios..." v-model="filterSvcText" style="height: 35px; font-size: 0.85rem;">
                    
                    <div class="scroll-area-custom border" style="max-height: 200px; overflow-y: auto; background: white; border-radius: 8px; padding: 10px;">
                      <div v-for="s in filteredCatServicios" :key="s.id_service" class="check-item d-flex align-items-center mb-1">
                        <input type="checkbox" :id="'cs-'+s.id_service" :value="s" v-model="selectedSvcsFromCatalog">
                        <label :for="'cs-'+s.id_service" class="ml-2 mb-0" style="font-size: 0.85rem; color: #333; cursor:pointer;">
                          {{ s.display_value }} <small class="text-muted">({{ s.id_service }})</small>
                        </label>
                      </div>
                    </div>
                    <div class="mt-2 d-flex justify-content-between">
                      <small class="text-muted">Seleccionados: <b>{{ selectedSvcsFromCatalog.length }}</b></small>
                      <button v-if="selectedSvcsFromCatalog.length > 0" class="btn btn-link btn-xs p-0 text-danger" @click="selectedSvcsFromCatalog = []">Limpiar</button>
                    </div>
                  </div>

                  <div v-if="selectedSvcsFromCatalog.length > 0" class="row animate__animated animate__fadeIn">
                    <div class="col-6"><label class="label-tiny">MONTO ($)</label><input v-model="formNewSvc.amount_to_pay" class="form-control editable-input w-100"></div>
                    <div class="col-6"><label class="label-tiny">PORCENTAJE (%)</label><input v-model="formNewSvc.amount_percentage" class="form-control editable-input w-100"></div>
                    <div class="col-12 mt-3">
                      <label class="label-tiny text-left">CANAL</label>
                      <select v-model="formNewSvc.channel" class="form-control custom-select-box">
                        <option v-for="c in catCanales" :key="c.id_channel" :value="c.id_channel">{{ c.id_channel }}</option>
                      </select>
                    </div>
                    <div class="col-12 mt-4">
                      <button class="btn btn-purple-digitel btn-block btn-round" @click="handleCreateService">
                        Insertar {{ selectedSvcsFromCatalog.length }} Servicio(s)
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="constructor-container mx-4 mt-5 mb-4 theme-adaptative-border">
                <div class="constructor-header gradient-purple">
                  <h4 class="m-0 text-white"><i class="tim-icons icon-link-72 mr-2"></i> Constructor de Reglas Lógicas</h4>
                </div>

                <div class="row p-4">
                  <div class="col-md-4">
                    <div class="setup-box theme-adaptative-card">
                      <div class="step-badge">1</div>
                      <label class="title-box">Configuración Básica</label>
                      
                      <input type="text" class="form-control mb-2" placeholder="Filtrar operación..." v-model="filterOTText" style="height: 35px; font-size: 0.85rem;">
                      <div class="scroll-area-custom border mb-3" style="max-height: 180px; overflow-y: auto; background: white; border-radius: 8px; padding: 10px;">
                        <div v-for="ot in filteredOrderTypes" :key="ot.id_order_type" class="check-item d-flex align-items-center mb-1 py-1">
                          <input type="radio" :id="'ot-'+ot.id_order_type" :value="ot.id_order_type" v-model="ruleForm.operation_code" style="cursor: pointer; accent-color: #5C068C;">
                          <label :for="'ot-'+ot.id_order_type" class="ml-2 mb-0" style="font-size: 0.8rem; cursor: pointer; color: #32325d;">
                            {{ ot.display_value }} <small class="text-muted">({{ ot.id_order_type }})</small>
                          </label>
                        </div>
                      </div>

                      <input v-model="ruleForm.description" class="form-control custom-input-box mb-3" placeholder="Descripción de la regla">
                      <div class="row text-center">
                        <div class="col-6">
                           <label class="label-tiny" style="color: #5C068C; font-weight: 800;">MONTO ($)</label>
                           <input v-model="ruleForm.amount_to_pay" class="form-control editable-input w-100" placeholder="0">
                        </div>
                        <div class="col-6">
                           <label class="label-tiny" style="color: #5C068C; font-weight: 800;">PORCENTAJE (%)</label>
                           <input v-model="ruleForm.amount_percentage" class="form-control editable-input w-100" placeholder="0">
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="col-md-4">
                    <div class="setup-box theme-adaptative-card">
                      <div class="step-badge">2</div>
                      <label class="title-box">Origen (Desde)</label>
                      <div class="mode-selector mb-3 theme-adaptative-card">
                        <button :class="{active: originMode === 'all'}" @click="originMode = 'all'">Cualquiera</button>
                        <button :class="{active: originMode === 'exclude'}" @click="originMode = 'exclude'">Excluir</button>
                      </div>
                      <div v-if="originMode !== 'all'" class="scroll-area-custom">
                        <div v-for="p in planesUnicos" :key="'orig-'+p" class="check-item">
                          <input type="checkbox" :id="'o-'+p" :value="p" v-model="selectedOriginPlanes">
                          <label :for="'o-'+p" class="ml-2 small text-dark">{{ p }}</label>
                        </div>
                      </div>
                      <div v-else class="empty-state text-center mt-5"><i class="tim-icons icon-world text-primary"></i></div>
                    </div>
                  </div>

                  <div class="col-md-4">
                    <div class="setup-box theme-adaptative-card">
                      <div class="step-badge">3</div>
                      <label class="title-box">Destino (Hacia)</label>
                      <div class="mode-selector mb-3 theme-adaptative-card">
                        <button :class="{active: destMode === 'all'}" @click="destMode = 'all'">Cualquiera</button>
                        <button :class="{active: destMode === 'include'}" @click="destMode = 'include'">Elegir</button>
                      </div>
                      <div v-if="destMode !== 'all'" class="scroll-area-custom">
                        <div v-for="p in planesUnicos" :key="'dest-'+p" class="check-item">
                          <input type="checkbox" :id="'d-'+p" :value="p" v-model="selectedDestPlanes">
                          <label :for="'d-'+p" class="ml-2 text-dark">{{ p }}</label>
                        </div>
                      </div>
                      <div v-else class="empty-state text-center mt-5"><i class="tim-icons icon-spaceship text-success"></i></div>
                    </div>
                  </div>
                </div>

                <div class="preview-footer theme-adaptative-preview">
                  <div class="preview-info">
                    <span class="preview-label text-purple-digitel">SQL PATTERN PREVIEW:</span>
                    <div class="badge-console-sql">
                      <span class="p-badge-sql">ORIGEN: <b class="text-purple-digitel">{{ previewOrigin }}</b></span>
                      <span class="p-badge-sql">DESTINO: <b class="text-purple-digitel">{{ previewDest }}</b></span>
                    </div>
                  </div>
                  <button class="btn btn-save-rule-final" @click="handleCreateGeneralRule" :disabled="!ruleForm.description || !ruleForm.operation_code">
                    <i class="tim-icons icon-cloud-upload-94 mr-2"></i> GUARDAR REGLA LÓGICA
                  </button>
                </div>
              </div>
            </div>
          </div>
        </card>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Parametros',
  data() {
    return {
      searchQuery: '', // Buscador de las tablas principales
      filterPlanText: '', // Buscador interno maestro planes
      filterSvcText: '', // Buscador interno maestro servicios
      filterOTText: '', // NUEVO: Buscador interno para Paso 1 del constructor
      loading: false,

      // Listas de datos
      planes: [], originalPlanes: [],
      servicios: [], originalServicios: [],
      reglasGenerales: [], originalReglasGenerales: [],
      
      // Catálogos
      catMaestroPlanes: [], 
      catMaestroServicios: [], 
      catCanales: [], 
      catOrderTypes: [],

      // Selecciones masivas para Catálogo
      selectedPlansFromCatalog: [],
      selectedSvcsFromCatalog: [],

      // Formularios
      formNewPlan: { amount_to_pay: '0', amount_percentage: '0', channel: 'AA' },
      formNewSvc: { amount_to_pay: '0', amount_percentage: '0', channel: 'AA' },
      ruleForm: { operation_code: '', amount_to_pay: '0', amount_percentage: '0', description: '' },
      
      // Constructor de Reglas
      tabActive: 'plans',
      originMode: 'all', 
      destMode: 'include',
      selectedOriginPlanes: [], 
      selectedDestPlanes: [],
    };
  },
  computed: {
    // FILTROS TABLAS PRINCIPALES
    filteredPlanes() {
      if (!this.searchQuery) return this.planes;
      const q = this.searchQuery.toLowerCase();
      return this.planes.filter(p => p.plan_name.toLowerCase().includes(q) || p.instance_name.toLowerCase().includes(q));
    },
    filteredServicios() {
      if (!this.searchQuery) return this.servicios;
      const q = this.searchQuery.toLowerCase();
      return this.servicios.filter(s => s.display_value.toLowerCase().includes(q) || s.id_service.toLowerCase().includes(q));
    },
    filteredReglas() {
      if (!this.searchQuery) return this.reglasGenerales;
      const q = this.searchQuery.toLowerCase();
      return this.reglasGenerales.filter(r => r.operation_name.toLowerCase().includes(q) || r.operation_code.toLowerCase().includes(q));
    },

    // FILTROS MAESTROS (GESTIÓN DE CATÁLOGO)
    filteredCatPlanes() {
      if (!this.filterPlanText) return this.catMaestroPlanes;
      const q = this.filterPlanText.toLowerCase();
      return this.catMaestroPlanes.filter(p => p.display_value.toLowerCase().includes(q));
    },
    filteredCatServicios() {
      if (!this.filterSvcText) return this.catMaestroServicios;
      const q = this.filterSvcText.toLowerCase();
      return this.catMaestroServicios.filter(s => s.display_value.toLowerCase().includes(q));
    },

    // NUEVO: FILTRO PARA PASO 1 DEL CONSTRUCTOR
    filteredOrderTypes() {
      if (!this.filterOTText) return this.catOrderTypes;
      const q = this.filterOTText.toLowerCase();
      return this.catOrderTypes.filter(ot => 
        ot.display_value.toLowerCase().includes(q) || 
        ot.id_order_type.toLowerCase().includes(q)
      );
    },

    // AUXILIARES CONSTRUCTOR
    planesUnicos() { return [...new Set(this.planes.map(p => p.plan_name))].sort(); },
    previewOrigin() { 
      if (this.originMode === 'all') return '%'; 
      return (this.originMode === 'exclude' ? 'NOT:' : '') + this.selectedOriginPlanes.join(','); 
    },
    previewDest() { 
      if (this.destMode === 'all') return '%'; 
      return this.selectedDestPlanes.join(','); 
    }
  },
  mounted() { 
    this.fetchData(); 
    this.fetchCatalogs(); 
  },
  methods: {
    async fetchData() {
      this.loading = true;
      try {
        const [resPlans, resServices, resRules] = await Promise.all([
          this.$http.get('/api/v1/business-rules/plans'),
          this.$http.get('/api/v1/business-rules/services'),
          this.$http.get('/api/v1/business-rules/general-rules')
        ]);
        this.planes = resPlans.data;
        this.originalPlanes = JSON.parse(JSON.stringify(resPlans.data));
        this.servicios = resServices.data;
        this.originalServicios = JSON.parse(JSON.stringify(resServices.data));
        this.reglasGenerales = resRules.data;
        this.originalReglasGenerales = JSON.parse(JSON.stringify(resRules.data));
      } catch (e) { 
        this.$notify({ type: 'danger', message: 'Error cargando datos.' }); 
      } finally { this.loading = false; }
    },

    async fetchCatalogs() {
      try {
        const [rP, rS, rC, rOT] = await Promise.all([
          this.$http.get('/api/v1/business-rules/catalog/plans'),
          this.$http.get('/api/v1/business-rules/catalog/services'),
          this.$http.get('/api/v1/business-rules/catalog/channels'),
          this.$http.get('/api/v1/business-rules/catalog/order-types')
        ]);
        this.catMaestroPlanes = rP.data; 
        this.catMaestroServicios = rS.data;
        this.catCanales = rC.data; 
        this.catOrderTypes = rOT.data;
      } catch (e) { console.error("Error catálogos", e); }
    },

    // --- ACCIONES MASIVAS (CATÁLOGO) ---
    async handleCreatePlan() {
      if (this.selectedPlansFromCatalog.length === 0) return;
      if (!window.confirm(`¿Desea agregar ${this.selectedPlansFromCatalog.length} planes a las comisiones?`)) return;

      this.loading = true;
      try {
        const user = localStorage.getItem('user_name') || 'ADMIN';
        const requests = this.selectedPlansFromCatalog.map(p => {
          return this.$http.post('/api/v1/business-rules/plans/create', {
            id_plan: p.id_plan,
            display_value: p.display_value,
            id_instance_type: p.id_instance_type,
            amount_to_pay: this.formNewPlan.amount_to_pay,
            channel: this.formNewPlan.channel,
            amount_percentage: this.formNewPlan.amount_percentage,
            created_who: user
          });
        });
        await Promise.all(requests);
        this.$notify({ type: 'success', message: 'Planes insertados correctamente.' });
        this.selectedPlansFromCatalog = [];
        this.filterPlanText = ''; // Limpiar filtro tras éxito
        this.fetchData();
      } catch (e) { this.$notify({ type: 'danger', message: 'Error al insertar planes.' }); }
      finally { this.loading = false; }
    },

    async handleCreateService() {
      if (this.selectedSvcsFromCatalog.length === 0) return;
      if (!window.confirm(`¿Desea agregar ${this.selectedSvcsFromCatalog.length} servicios a las comisiones?`)) return;

      this.loading = true;
      try {
        const user = localStorage.getItem('user_name') || 'ADMIN';
        const requests = this.selectedSvcsFromCatalog.map(s => {
          return this.$http.post('/api/v1/business-rules/services/create', {
            id_service: s.id_service,
            display_value: s.display_value,
            amount_to_pay: this.formNewSvc.amount_to_pay,
            channel: this.formNewSvc.channel,
            amount_percentage: this.formNewSvc.amount_percentage,
            created_who: user
          });
        });
        await Promise.all(requests);
        this.$notify({ type: 'success', message: 'Servicios insertados correctamente.' });
        this.selectedSvcsFromCatalog = [];
        this.filterSvcText = ''; // Limpiar filtro tras éxito
        this.fetchData();
      } catch (e) { this.$notify({ type: 'danger', message: 'Error al insertar servicios.' }); }
      finally { this.loading = false; }
    },

    // --- ACCIONES REGLAS LÓGICAS ---
    async handleCreateGeneralRule() {
      if (!window.confirm("¿Desea crear esta nueva regla lógica?")) return;
      try {
        await this.$http.post('/api/v1/business-rules/general-rules/create', { 
          ...this.ruleForm, 
          origin_plan_pattern: this.previewOrigin, 
          destination_plan_pattern: this.previewDest, 
          commissionable_flag: 'Y' 
        });
        this.$notify({ type: 'success', message: 'Regla creada.' });
        this.fetchData();
        this.ruleForm = { operation_code: '', amount_to_pay: '0', amount_percentage: '0', description: '' };
        this.filterOTText = ''; // Limpiar filtro de constructor
      } catch (e) { this.$notify({ type: 'danger', message: 'Error al crear.' }); }
    },

    // --- MANTENIMIENTO ---
    toggleStatus(item) { item.inactive_dt = item.inactive_dt ? null : 'PENDING_CHANGE'; },
    toggleRule(rule) { rule.commissionable_flag = rule.commissionable_flag === 'Y' ? 'N' : 'Y'; },

    hasPlanChanged(item) {
      const o = this.originalPlanes.find(x => x.id_plan === item.id_plan && x.channel === item.channel && x.id_instance_type === item.id_instance_type);
      if (!o) return false;
      const statusChanged = (item.inactive_dt === null && o.inactive_dt !== null) || (item.inactive_dt !== null && o.inactive_dt === null);
      return String(item.amount_to_pay) !== String(o.amount_to_pay) || String(item.amount_percentage) !== String(o.amount_percentage) || statusChanged;
    },

    hasServiceChanged(item) {
      const o = this.originalServicios.find(x => x.id_service === item.id_service && x.channel === item.channel);
      if (!o) return false;
      const statusChanged = (item.inactive_dt === null && o.inactive_dt !== null) || (item.inactive_dt !== null && o.inactive_dt === null);
      return String(item.amount_to_pay) !== String(o.amount_to_pay) || String(item.amount_percentage) !== String(o.amount_percentage) || statusChanged;
    },

    hasRuleChanged(item) {
      const o = this.originalReglasGenerales.find(o => o.operation_code === item.operation_code && o.description === item.description);
      return o ? (String(item.amount_to_pay) !== String(o.amount_to_pay) || String(item.amount_percentege) !== String(o.amount_percentege) || String(item.commissionable_flag) !== String(o.commissionable_flag)) : false;
    },

    async executeSavePlan(plan) {
      this.loading = true;
      try {
        await this.$http.put('/api/v1/business-rules/plans/update', { ...plan, is_active: plan.inactive_dt === null, change_who: localStorage.getItem('user_name') || 'ADMIN' });
        this.fetchData(); this.$notify({ type: 'success', message: 'Plan actualizado.' });
      } catch (e) { this.$notify({ type: 'danger', message: 'Error.' }); } finally { this.loading = false; }
    },

    async executeSaveService(svc) {
      this.loading = true;
      try {
        await this.$http.put('/api/v1/business-rules/services/update', { ...svc, is_active: svc.inactive_dt === null, change_who: localStorage.getItem('user_name') || 'ADMIN' });
        this.fetchData(); this.$notify({ type: 'success', message: 'Servicio actualizado.' });
      } catch (e) { this.$notify({ type: 'danger', message: 'Error.' }); } finally { this.loading = false; }
    },

    async executeSaveRule(rule) {
      this.loading = true;
      try {
        const original = this.originalReglasGenerales.find(o => o.operation_code === rule.operation_code && o.description === rule.description);
        await this.$http.put('/api/v1/business-rules/general-rules/update', { ...rule, description_original: original.description });
        this.fetchData(); this.$notify({ type: 'success', message: 'Regla actualizada.' });
      } catch (e) { this.$notify({ type: 'danger', message: 'Error.' }); } finally { this.loading = false; }
    },

    confirmSavePlan(plan) { if (this.hasPlanChanged(plan)) { if (window.confirm("¿Actualizar plan?")) this.executeSavePlan(plan); } },
    confirmSaveService(svc) { if (this.hasServiceChanged(svc)) { if (window.confirm("¿Actualizar servicio?")) this.executeSaveService(svc); } },
    confirmSaveRule(rule) { if (this.hasRuleChanged(rule)) { if (window.confirm("¿Actualizar regla?")) this.executeSaveRule(rule); } }
  }
}
</script>

<style scoped>
.text-purple-digitel { color: #5C068C !important; font-weight: 800; }
.custom-nav-tabs .nav-link { color: #525f7f !important; font-weight: 600; cursor: pointer; border: none !important; }
.custom-nav-tabs .nav-link.active { color: #5C068C !important; border-bottom: 3px solid #5C068C !important; background: transparent !important; }
.custom-table thead th { color: #8898aa !important; font-weight: 700; border-top: none; text-transform: uppercase; font-size: 0.7rem; }
.plan-name { color: #32325d !important; line-height: 1.2; }

/* INPUTS NORMALIZADOS (FONDO CLARO) */
.editable-input { 
  background-color: #f4f5f7 !important; 
  color: #5C068C !important; 
  border: 1px solid #d0d0d0 !important;
  text-align: center; 
  width: 80px; 
  height: 32px; 
  font-weight: 800; 
  font-size: 0.85rem; 
  border-radius: 6px;
  transition: all 0.3s ease;
}
.editable-input:focus { border-color: #5C068C !important; background-color: #ffffff !important; box-shadow: 0 0 5px rgba(92,6,140,0.2); }

/* CONSTRUCTOR UI (FORZADO CLARO) */
.constructor-container { border-radius: 12px; overflow: hidden; box-shadow: 0 5px 25px rgba(0,0,0,0.1); background-color: #ffffff !important; }
.theme-adaptative-border { border: 1px solid #5C068C; }
.constructor-header { background: linear-gradient(135deg, #5C068C 0%, #8e44ad 100%); padding: 15px 25px; }
.setup-box { border: 1px solid #e3e3e3 !important; border-radius: 10px; padding: 20px; position: relative; min-height: 350px; background-color: #f9f9f9 !important; }
.theme-adaptative-card { background-color: #ffffff !important; }
.step-badge { position: absolute; top: -12px; left: -12px; background: #00f2c3; color: #1e1e2f; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; box-shadow: 0 4px 8px rgba(0,242,195,0.3); }
.title-box { color: #5C068C; font-weight: 700; text-transform: uppercase; font-size: 11px; display: block; margin-bottom: 15px; }

.label-tiny { display: block; font-size: 9px; font-weight: 800; color: #8898aa; margin-bottom: 4px; text-align: center; }

/* MODOS SELECCIÓN */
.mode-selector { display: flex; background: rgba(0,0,0,0.05); border-radius: 8px; padding: 4px; }
.mode-selector button { flex: 1; border: none; background: transparent; padding: 6px; font-size: 10px; font-weight: 700; color: #8898aa; border-radius: 6px; transition: 0.2s; }
.mode-selector button.active { background: #fff; color: #5C068C; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }

/* FOOTER PREVIEW (NORMALIZADO) */
.preview-footer { background-color: #f4f5f7 !important; padding: 20px 30px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #e3e3e3; }
.badge-console-sql { display: flex; gap: 10px; }
.p-badge-sql { background: #ffffff !important; color: #32325d !important; padding: 6px 12px; border-radius: 4px; font-family: monospace; font-size: 13px; border: 1px solid #d0d0d0; }
.preview-label { font-size: 11px; font-weight: 800; }
.btn-save-rule-final { background: linear-gradient(135deg, #5C068C 0%, #8e44ad 100%); color: white; font-weight: 700; padding: 12px 25px; border-radius: 8px; border: none; cursor: pointer; }

/* SELECTS E INPUTS CUSTOM */
.custom-select-box, .custom-input-box { background-color: #ffffff !important; color: #32325d !important; border: 1px solid #d0d0d0 !important; font-size: 0.85rem; }

/* ESTADOS */
.text-status-toggle { color: #5C068C !important; font-weight: 600; cursor: pointer; }
.channel-badge { background-color: #5C068C !important; color: white !important; padding: 5px 12px; font-weight: bold; border-radius: 4px; }
.pattern-field-locked { background-color: #f4f5f7 !important; border: 1px solid #ced4da !important; font-size: 0.75rem; height: 30px; font-family: monospace; cursor: not-allowed; border-radius: 4px; }
.header-section { color: #5C068C; font-weight: 800; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 15px;}
.border-right-card { border-right: 1px solid #eee; }
.scroll-area-custom { max-height: 180px; overflow-y: auto; padding: 5px; }
.check-item { padding: 5px 0; border-bottom: 1px solid rgba(0,0,0,0.05); display: flex; align-items: center; }

.btn-warning-pulse { color: #ff8d72 !important; border: 1px solid #ff8d72 !important; border-radius: 50%; animation: pulse-orange 2s infinite; }
.btn-success-static { color: #00f2c3 !important; opacity: 0.5; }
@keyframes pulse-orange { 0% { box-shadow: 0 0 0 0 rgba(255, 141, 114, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(255, 141, 114, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 141, 114, 0); } }
</style>