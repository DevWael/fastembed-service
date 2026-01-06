# FastEmbed Embedding Service

A lightweight, self-hosted embedding generation API built with FastAPI and FastEmbed, optimized for ARM architecture and low-resource environments.

## Features

- **OpenAI-compatible API**: Drop-in replacement for OpenAI embeddings API
- **Fast & Efficient**: Optimized for ARM CPUs (Oracle Cloud, Raspberry Pi, Apple Silicon)
- **Lightweight**: Uses sentence-transformers/all-MiniLM-L6-v2 (22M parameters, 384 dimensions)
- **Docker-ready**: Simple deployment with Docker Compose
- **Production-ready**: Includes health checks and proper error handling

## Model Specifications

- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Dimensions**: 384
- **Max Tokens**: 256 word pieces (~200 words)
- **Speed**: ~14.7ms per 1K tokens on standard hardware
- **Memory**: ~85MB inference memory
- **Accuracy**: 78.1% retrieval accuracy, suitable for production use

## Requirements

- Docker & Docker Compose
- 1GB RAM minimum
- 2GB disk space for Docker image

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/embedding-service.git
cd embedding-service

# Build and start the service
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Verify service is running
curl http://localhost:8000/health
```

## Usage

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "healthy"}
```

### Service Information

```bash
curl http://localhost:8000/
```

### Single Text Embedding

```bash
curl -X POST http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Your text to embed here"
  }'
```

### Batch Embedding

```bash
curl -X POST http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": [
      "First text to embed",
      "Second text to embed",
      "Third text to embed"
    ]
  }'
```

### Response Format

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.123, -0.456, 0.789, ...]
    }
  ],
  "model": "sentence-transformers/all-MiniLM-L6-v2",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

## Integration Examples

### PHP/WordPress

```php
<?php
$text = "Your content here";

$response = wp_remote_post('http://localhost:8000/v1/embeddings', [
    'headers' => ['Content-Type' => 'application/json'],
    'body' => json_encode(['input' => $text]),
    'timeout' => 30
]);

if (!is_wp_error($response)) {
    $data = json_decode(wp_remote_retrieve_body($response), true);
    $embedding = $data['data'][0]['embedding']; // Array of 384 floats
}
```

### Python

```python
import requests

response = requests.post(
    'http://localhost:8000/v1/embeddings',
    json={'input': 'Your text here'}
)

embedding = response.json()['data'][0]['embedding']
```

### JavaScript/Node.js

```javascript
const response = await fetch('http://localhost:8000/v1/embeddings', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ input: 'Your text here' })
});

const data = await response.json();
const embedding = data.data[0].embedding;
```

## Docker Commands

```bash
# Start service
docker-compose up -d

# Stop service
docker-compose down

# Restart service
docker-compose restart

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose up -d --build

# Check container status
docker-compose ps
```

## Configuration

### Resource Limits

Edit `docker-compose.yml` to adjust resource limits:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 512M
```

### Port Configuration

Change the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8000:8000"  # Change first 8000 to your desired port
```

## Performance Optimization

### For Production Use

1. **Batch requests**: Send multiple texts in one request for better throughput
2. **Cache embeddings**: Store generated embeddings in a database
3. **Background processing**: Generate embeddings asynchronously, not during page loads
4. **Use Nginx**: Add reverse proxy with caching for better performance

### Expected Performance

- **Oracle Cloud ARM (Ampere A1)**: 50-100ms per single text, thousands per minute in batch
- **Apple M1/M2**: 10-20ms per single text
- **Standard x86 CPU**: 30-60ms per single text

## Nginx Reverse Proxy (Optional)

Add SSL and authentication by proxying through Nginx:

```nginx
server {
    listen 443 ssl http2;
    server_name embeddings.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## Best Practices

1. **Text Preprocessing**: Strip HTML tags and clean text before sending
2. **Token Limit**: Keep input under 200 words for best results
3. **Error Handling**: Implement retry logic for failed requests
4. **Monitoring**: Use health check endpoint for uptime monitoring

## Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose logs

# Verify port is not in use
lsof -i :8000

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Slow performance

- Use batch requests instead of individual calls
- Check CPU/memory usage: `docker stats`
- Consider increasing resource limits in docker-compose.yml

### Out of memory

- Reduce workers to 1 in Dockerfile CMD
- Increase memory limit in docker-compose.yml
- Restart the service: `docker-compose restart`

## License

MIT

## Credits

- **FastEmbed**: [Qdrant FastEmbed](https://github.com/qdrant/fastembed)
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Framework**: FastAPI