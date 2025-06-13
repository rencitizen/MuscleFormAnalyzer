# Frontend Dockerfile for TENAX FIT
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build the application (for production)
# RUN npm run build

# Expose port
EXPOSE 3000

# Development command (use npm start for production)
CMD ["npm", "run", "dev"]