# Use the latest LTS Node.js image
FROM node:lts

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json with ownership for 'node' user
COPY --chown=node:node package*.json ./

# Switch to 'node' user and install dependencies
USER node
# RUN npm install

# Switch back to root to copy the rest of the files
USER root
COPY --chown=node:node . .

# Ensure permissions for .nuxt and other directories
RUN mkdir -p .nuxt node_modules/.cache && \
    chown -R node:node /app

# Switch to 'node' user for running the application
USER node

# Expose the Nuxt development server port
EXPOSE 3000

# Start the Nuxt application in development mode
CMD ["npm", "run", "dev"]
