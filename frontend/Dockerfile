FROM node:18

WORKDIR /app

# 패키지 설치 (캐시 최적화)
COPY package.json package-lock.json* ./
RUN npm install

# 전체 소스 복사
COPY . .

# Vite 개발 서버 실행
CMD ["npm", "run", "dev"]
