# Sherlock Docker Setup

Complete Docker setup for Sherlock Username Search with web interface, PostgreSQL, and Redis.

## Overview

This Docker setup includes:
- **sherlock_web**: Flask web interface for easy username searching
- **sherlock_postgres**: PostgreSQL database for storing search history
- **sherlock_redis**: Redis cache for performance optimization

## Credentials

**Database & Redis:**
- Username: `tony`
- Password: `hrpassword123`
- Database Name: `sherlock_db`

**Ports (to avoid conflicts with eboss project):**
- Web Interface: `5050` (instead of 5000)
- PostgreSQL: `5433` (instead of 5432)
- Redis: `6380` (instead of 6379)

**Docker Names:**
- Containers: `sherlock_web`, `sherlock_postgres`, `sherlock_redis`
- Network: `sherlock_network`
- Volumes: `sherlock_postgres_data`, `sherlock_redis_data`, `sherlock_results`

## Quick Start

### 1. Build and Start Services

```bash
# Build and start all containers
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f sherlock_web
```

### 2. Access the Web Interface

Open your browser to:
- **Local:** http://localhost:5050
- **Network:** http://192.168.1.22:5050 (if on network 192.168.1.22)

### 3. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v
```

## Docker Commands

### Container Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a specific service
docker-compose restart sherlock_web

# View running containers
docker ps

# View all containers (including stopped)
docker ps -a
```

### Logs and Debugging

```bash
# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f sherlock_web
docker-compose logs -f sherlock_postgres

# Execute command in container
docker exec -it sherlock_web bash
docker exec -it sherlock_postgres psql -U tony -d sherlock_db
docker exec -it sherlock_redis redis-cli -a hrpassword123
```

### Database Access

```bash
# Connect to PostgreSQL from host machine
PGPASSWORD=hrpassword123 psql -h localhost -p 5433 -U tony -d sherlock_db

# Connect to PostgreSQL inside container
docker exec -it sherlock_postgres psql -U tony -d sherlock_db

# Backup database
docker exec sherlock_postgres pg_dump -U tony sherlock_db > backup.sql

# Restore database
docker exec -i sherlock_postgres psql -U tony -d sherlock_db < backup.sql
```

### Redis Access

```bash
# Connect to Redis from host machine
redis-cli -h localhost -p 6380 -a hrpassword123

# Connect to Redis inside container
docker exec -it sherlock_redis redis-cli -a hrpassword123

# Test Redis connection
docker exec sherlock_redis redis-cli -a hrpassword123 ping
# Should return: PONG
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Edit `.env` to change:
- Database credentials
- Port numbers
- Container names
- Volume names

### Custom Ports

If you need to change ports, edit `docker-compose.yml`:

```yaml
services:
  sherlock_web:
    ports:
      - "YOUR_PORT:5000"  # Change YOUR_PORT

  sherlock_postgres:
    ports:
      - "YOUR_PORT:5432"  # Change YOUR_PORT

  sherlock_redis:
    ports:
      - "YOUR_PORT:6379"  # Change YOUR_PORT
```

## Network Configuration

All services run on the `sherlock_network` Docker network. This allows:
- Services to communicate using container names
- Isolation from other Docker projects
- Easy service discovery

## Volume Management

### Data Persistence

Data is stored in Docker volumes:
- `sherlock_postgres_data`: Database data
- `sherlock_redis_data`: Cache data
- `sherlock_results`: Search results and exports

### Backup Volumes

```bash
# Backup PostgreSQL volume
docker run --rm -v sherlock_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore PostgreSQL volume
docker run --rm -v sherlock_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

### Clean Up Volumes

```bash
# Remove all volumes (CAUTION: deletes all data)
docker-compose down -v

# Remove specific volume
docker volume rm sherlock_postgres_data
```

## Health Checks

All services have health checks configured:

```bash
# Check container health status
docker ps

# View health check logs
docker inspect sherlock_web | grep -A 20 Health
```

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

1. Check what's using the port:
   ```bash
   lsof -i :5050  # For web interface
   lsof -i :5433  # For PostgreSQL
   lsof -i :6380  # For Redis
   ```

2. Change the port in `docker-compose.yml`

### Container Won't Start

Check logs:
```bash
docker-compose logs sherlock_web
```

### Database Connection Issues

1. Ensure PostgreSQL is healthy:
   ```bash
   docker ps
   # Look for "healthy" status
   ```

2. Test connection:
   ```bash
   docker exec sherlock_postgres pg_isready -U tony -d sherlock_db
   ```

### Redis Connection Issues

1. Test Redis:
   ```bash
   docker exec sherlock_redis redis-cli -a hrpassword123 ping
   ```

2. Check Redis logs:
   ```bash
   docker-compose logs sherlock_redis
   ```

## Production Deployment

For production deployment on 192.168.1.22:

1. **Update docker-compose.yml** to bind to network interface:
   ```yaml
   services:
     sherlock_web:
       ports:
         - "0.0.0.0:5050:5000"
   ```

2. **Enable security features:**
   - Use strong passwords
   - Enable SSL/TLS
   - Set up firewall rules
   - Use environment-specific configs

3. **Monitor services:**
   - Set up logging
   - Configure alerts
   - Monitor resource usage

## Integration with eboss Project

This setup is designed to coexist with your eboss project:

| Service | eboss Port | Sherlock Port |
|---------|-----------|---------------|
| Web | N/A | 5050 |
| PostgreSQL | 5432 | 5433 |
| Redis | 6379 | 6380 |

**Same credentials, different databases:**
- Username: `tony` (same)
- Password: `hrpassword123` (same)
- eboss database: `eboss_db`
- Sherlock database: `sherlock_db`

## Useful Commands Summary

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# Restart web interface
docker-compose restart sherlock_web

# View logs
docker-compose logs -f

# Access database
docker exec -it sherlock_postgres psql -U tony -d sherlock_db

# Access Redis
docker exec -it sherlock_redis redis-cli -a hrpassword123

# Backup database
docker exec sherlock_postgres pg_dump -U tony sherlock_db > backup.sql

# Clean up everything
docker-compose down -v
```

## Support

For issues or questions, check:
- Container logs: `docker-compose logs`
- Health status: `docker ps`
- Network connectivity: `docker network inspect sherlock_network`
