# --- ETAPA 1: COMPILACIÓN ---
# Usamos una imagen de Node estable y liviana para construir los archivos estáticos
FROM node:16-alpine AS build-stage

WORKDIR /app

# Copiamos los archivos de configuración de dependencias primero para aprovechar la caché de Docker
COPY package*.json ./

# Instalamos los paquetes respetando los overrides de seguridad que configuramos en tu package.json
RUN npm install

# Copiamos todo el código fuente del FrontEnd al contenedor
COPY . .

# Compilamos la aplicación de Vue para producción (esto generará la carpeta /dist)
RUN npm run build


# --- ETAPA 2: PRODUCCIÓN ---
# Usamos un servidor Nginx ligero para servir de forma ultra rápida el HTML y JS compilado
FROM nginx:stable-alpine AS production-stage

# Copiamos los archivos generados en la etapa anterior a la ruta por defecto de Nginx
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Exponemos el puerto 80 dentro del contenedor
EXPOSE 80

# Arrancamos Nginx en primer plano
CMD ["nginx", "-g", "daemon off;"]