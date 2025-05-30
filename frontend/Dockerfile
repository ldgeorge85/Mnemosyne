# Frontend Dockerfile with multi-stage build
# Stage 1: Development
FROM node:18-alpine AS development

# Set working directory
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Development only needs dependencies installed
# The actual code will be mounted as a volume

# Set environment variables for Vite
ENV VITE_API_URL=/api/v1
ENV CHOKIDAR_USEPOLLING=true

# Stage 2: Build
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy all files
COPY . .

# Set environment variables for production build
ENV VITE_API_URL=/api/v1

# Build the application
RUN npm run build

# Stage 3: Production
FROM nginx:alpine AS production

# Copy built assets from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
