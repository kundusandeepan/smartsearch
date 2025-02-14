docker-compose down && docker-compose up --build 
cd frontend
cd chatapp

npm install
npm start

curl "http://localhost:8000/search?query=fatigue"
curl "http://localhost:8000/search?query=acidity"