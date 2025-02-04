# micro-tenancy

this repo implements multi tenancy with multiple micro services

## How to run

1. Clone the repo
2. Run `docker-compose up` in the root directory
3. Open `http://localhost:8000` in your browser for tenant manager api
4. Open `http://subdomain.localhost:8001` in your browser to access Posts api
5. Open `http://subdomain.localhost:8002` in your browser to access Tasks api