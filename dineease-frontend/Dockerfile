# Use the latest LTS Node.js image
FROM node:lts

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json with ownership for 'node' user
COPY --chown=node:node package*.json ./

# Install dependencies as 'node' user
USER root
RUN npm install

# Switch back to root to copy the rest of the files
COPY --chown=node:node . .

# Ensure permissions for .nuxt, node_modules, and other directories
RUN mkdir -p .nuxt node_modules/.cache && \
    chown -R node:node /app

# Switch back to 'node' user for running the application
USER node

# Expose the Nuxt development server port
EXPOSE 3000

# Start the Nuxt application in development mode
CMD ["npm", "run", "dev"]