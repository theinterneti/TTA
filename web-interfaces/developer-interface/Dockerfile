# Multi-stage build for Developer Interface
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY ../shared/package*.json ../shared/

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .
COPY ../shared ../shared

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine as production

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Add environment variable substitution script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3006/health || exit 1

# Expose port
EXPOSE 3006

# Start with environment variable substitution
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
