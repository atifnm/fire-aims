FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
# Vite inlines import.meta.env.* into the built JS at build time, not at container runtime —
# so this has to be a build ARG (passed via `docker build --build-arg` or Railway's per-service
# "Build Variables"), not a normal runtime environment variable. Leave unset for docker-compose,
# where the frontend and backend share an origin via the nginx proxy below and no override is
# needed.
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
