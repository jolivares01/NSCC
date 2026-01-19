<template>
  <transition name="fade">
    <div 
      v-if="show" 
      class="notification"
      :class="type"
    >
      <div class="notification-content">
        <i :class="iconClass" class="notification-icon"></i>
        <span class="notification-message">{{ message }}</span>
      </div>
      <button class="notification-close" @click="$emit('close')">
        &times;
      </button>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'Notification',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'success',
      validator: (value) => ['success', 'warning', 'danger', 'info'].includes(value)
    },
    message: {
      type: String,
      default: ''
    }
  },
  computed: {
    iconClass() {
      const icons = {
        success: 'tim-icons icon-check-2',
        warning: 'tim-icons icon-alert-circle-exc',
        danger: 'tim-icons icon-simple-remove',
        info: 'tim-icons icon-bell-55'
      };
      return icons[this.type] || icons.info;
    }
  }
}
</script>

<style scoped>
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  min-width: 300px;
  max-width: 400px;
  padding: 15px 20px;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  justify-content: space-between;
  align-items: center;
  animation: slideIn 0.3s ease;
}

.notification.success {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.notification.warning {
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  color: #856404;
}

.notification.danger {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.notification.info {
  background-color: #d1ecf1;
  border: 1px solid #bee5eb;
  color: #0c5460;
}

.notification-content {
  display: flex;
  align-items: center;
  flex: 1;
}

.notification-icon {
  margin-right: 10px;
  font-size: 18px;
}

.notification-message {
  flex: 1;
  font-size: 14px;
  line-height: 1.4;
}

.notification-close {
  background: none;
  border: none;
  font-size: 20px;
  color: inherit;
  opacity: 0.7;
  cursor: pointer;
  padding: 0;
  margin-left: 10px;
  line-height: 1;
}

.notification-close:hover {
  opacity: 1;
}

/* Animaciones */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>