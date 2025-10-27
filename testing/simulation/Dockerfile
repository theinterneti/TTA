# TTA Simulation Framework - Production Docker Image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    curl \
    bash \
    git \
    python3 \
    py3-pip \
    && rm -rf /var/cache/apk/*

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install Node.js dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build TypeScript
RUN npm run build

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S simulation -u 1001 -G nodejs

# Create necessary directories
RUN mkdir -p /app/logs /app/reports /app/data && \
    chown -R simulation:nodejs /app

# Switch to non-root user
USER simulation

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3002/health || exit 1

# Expose port for simulation API
EXPOSE 3002

# Default command
CMD ["npm", "start"]
