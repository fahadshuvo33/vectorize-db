
FROM node:25-alpine AS development

WORKDIR /app

COPY package*.json ./

# BuildKit cache for npm (FAST!)
# Cache npm packages and node_modules downloads
RUN --mount=type=cache,target=/root/.npm,sharing=locked \
    npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ===================================
# Build Stage
# ===================================
FROM node:25-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN --mount=type=cache,target=/root/.npm,sharing=locked \
    npm ci

COPY . .

RUN npm run build

# ===================================
# Production Stage
# ===================================
FROM nginx:alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]