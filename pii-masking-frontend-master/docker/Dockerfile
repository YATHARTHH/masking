# Multi-stage production build for React + Vite SPA
# Stage 1: Build static assets
FROM node:26-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source files and build
COPY . .
RUN npm run build

# Stage 2: Serve using NGINX Alpine
FROM nginx:1.27-alpine AS production

# Copy custom NGINX configuration
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled SPA bundle from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
