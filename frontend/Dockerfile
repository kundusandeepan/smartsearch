# FROM node:18-alpine
# WORKDIR /app
# COPY package.json package-lock.json ./
# RUN npm install
# COPY . .
# CMD ["npm", "start"]


FROM node:18-alpine
# Set the working directory to /app inside the container
WORKDIR /app
# Copy the package.json and package-lock.json from chatapp directory in the build context
COPY ./chatapp/package.json ./chatapp/package-lock.json ./
# Install dependencies
RUN npm install
# Copy the rest of the app files from chatapp directory into /app inside the container
COPY ./chatapp /app
# Set the command to start the application
CMD ["npm", "start"]
