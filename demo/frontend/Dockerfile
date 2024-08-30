# Use the official Node.js image as the base image
FROM node:18

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install frontend dependencies
RUN npm install

# Copy all frontend files to the working directory
COPY . .

# Expose port 3000 for the frontend
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"]
