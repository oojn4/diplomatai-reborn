# Stage 1: Build the React app
FROM node:14 AS build

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./

RUN npm install --force

COPY . ./

RUN npm run build

CMD ["npm", "start"]