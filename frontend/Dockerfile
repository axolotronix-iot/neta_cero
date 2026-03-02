FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["npx", "tailwindcss", "-i", "./src/input.css", "-o", "./static/css/style.css", "--watch"]