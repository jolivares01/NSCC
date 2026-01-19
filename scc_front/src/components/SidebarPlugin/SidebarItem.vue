<template>
  <li class="nav-item">
    <a
      class="nav-link"
      :class="{ collapsed: !isExpanded }"
      data-toggle="collapse"
      :href="'#' + id"
      @click="toggle"
    >
      <i v-if="icon" :class="icon"></i>
      <p>
        {{ title }}
        <b class="caret"></b>
      </p>
    </a>
    <div :id="id" class="collapse" :class="{ show: isExpanded }">
      <ul class="nav">
        <slot></slot>
      </ul>
    </div>
  </li>
</template>

<script>
export default {
  name: "SidebarItem",
  props: {
    title: String,
    icon: String,
    id: {
      type: String,
      default: () => Math.random().toString(36).substr(2, 9)
    }
  },
  data() {
    return {
      isExpanded: false
    };
  },
  methods: {
    toggle() {
      this.isExpanded = !this.isExpanded;
    }
  }
};
</script>

<style>
/* Estilos para el desplegable */
.nav-item .nav-link {
  cursor: pointer;
}
.nav-item .nav-link .caret {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  transition: transform 0.3s;
}
.nav-item .nav-link:not(.collapsed) .caret {
  transform: translateY(-50%) rotate(180deg);
}
</style>