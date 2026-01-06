# FastEmbed Embedding Service

A lightweight, self-hosted embedding generation API built with FastAPI and FastEmbed, optimized for ARM architecture and low-resource environments.

## Features

- **OpenAI-compatible API**: Drop-in replacement for OpenAI embeddings API
- **Fast & Efficient**: Optimized for ARM CPUs (Oracle Cloud, Raspberry Pi, Apple Silicon)
- **Long Context Support**: Uses nomic-ai/nomic-embed-text-v1.5 (768 dimensions, 8K token context)
- **Docker-ready**: Simple deployment with Docker Compose
- **Production-ready**: Includes health checks and proper error handling
- **High Quality**: Superior semantic understanding with 768-dimensional embeddings

## Model Specifications

- **Model**: nomic-ai/nomic-embed-text-v1.5
- **Dimensions**: 768 (high-quality embeddings)
- **Max Tokens**: 8,192 tokens (~6,000+ words)
- **Max Characters**: ~25,000-30,000 characters
- **Speed**: ~228ms per embedding on Oracle ARM (actual benchmark)
- **Memory**: ~540MB model size, ~1GB inference memory
- **Context**: Handles entire articles, blog posts, and documentation pages in a single embedding

## Requirements

- Docker & Docker Compose
- 2GB RAM minimum (recommended 4GB)
- 2GB disk space for Docker image
- ARM CPU (Oracle Cloud, Apple Silicon) or x86 CPU

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/embedding-service.git
cd embedding-service

# Build and start the service
docker-compose up -d --build

# Check logs (model download ~540MB)
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
  "model": "nomic-ai/nomic-embed-text-v1.5",
  "usage": {
    "prompt_tokens": 42,
    "total_tokens": 42
  }
}
```

## Integration Examples

### PHP/WordPress

```php
<?php
$text = wp_strip_all_tags($post->post_content);

$response = wp_remote_post('http://localhost:8000/v1/embeddings', [
    'headers' => ['Content-Type' => 'application/json'],
    'body' => json_encode(['input' => $text]),
    'timeout' => 30
]);

if (!is_wp_error($response)) {
    $data = json_decode(wp_remote_retrieve_body($response), true);
    $embedding = $data['data'][0]['embedding']; // Array of 768 floats
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
      memory: 4G
    reservations:
      cpus: '1'
      memory: 1G
```

### Port Configuration

Change the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8000:8000"  # Change first 8000 to your desired port
```

## Performance

### Actual Benchmarks (Real-World Testing)

- **Oracle Cloud ARM (Ampere A1)**: 228ms per embedding (42 tokens) ⚡
- **Apple M1/M2**: 466ms per embedding (42 tokens)
- **Throughput**: ~4+ embeddings per second on Oracle ARM
- **Daily Capacity**: Hundreds of thousands of articles

### What You Can Handle

- **Your average 600-word articles**: ✅ Fit entirely in one embedding (~10% of capacity)
- **Multiple articles at once**: ✅ Send up to ~6,000 words per request
- **Real-time embedding**: ✅ Fast enough for WordPress content publish hooks
- **Background processing**: ✅ Excellent for cron jobs and queued tasks

## Content Size Examples

| Content Type | Word Count | Tokens | Fits? |
|---|---|---|---|
| Blog post | 600 | ~800 | ✅ Yes |
| Long article | 2,000 | ~2,600 | ✅ Yes |
| Academic paper | 5,000 | ~6,600 | ✅ Yes |
| E-book chapter | 6,000 | ~8,000 | ✅ Yes (max) |
| Multiple articles | 10,000+ | 13,000+ | ❌ Requires chunking |

## Performance Optimization

### For Production Use

1. **Batch requests**: Send multiple texts in one request for better throughput
2. **Cache embeddings**: Store generated embeddings in a database to avoid re-computing
3. **Background processing**: Generate embeddings asynchronously via cron/queue
4. **Use Nginx**: Add reverse proxy with caching for better performance
5. **Enable multiple workers**: Update Dockerfile CMD for concurrent requests

### Production Configuration

```dockerfile
# In Dockerfile, change:
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '3'
      memory: 4G
    reservations:
      cpus: '2'
      memory: 1G
```

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
        proxy_buffering off;
    }
}
```

## Best Practices

1. **Text Preprocessing**: Strip HTML tags and clean text before sending
2. **No Chunking Needed**: With 8K token context, most content fits in one embedding
3. **Error Handling**: Implement retry logic for failed requests
4. **Monitoring**: Use health check endpoint for uptime monitoring
5. **Batch Processing**: Group multiple texts for better efficiency

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
- Consider increasing worker count in Dockerfile
- Verify no other processes are consuming resources

### Out of memory

- Reduce workers to 1 in Dockerfile CMD
- Increase memory limit in docker-compose.yml
- Check available RAM: `free -h`
- Restart the service: `docker-compose restart`

### Model download fails

- Ensure you have stable internet connection
- Check disk space: `df -h` (need ~2GB)
- Try manually: `docker-compose up -d --build` (will retry download)

## Cost Comparison

**Your Self-Hosted Solution (Oracle Free Tier)**
- Cost: **$0/month** ✅
- Embeddings: **Unlimited**
- Speed: **228ms per embedding**
- Total Value: **Priceless**

**OpenAI API (text-embedding-3-small)**
- Cost: **$0.02 per 1M tokens**
- Example: 1,000 articles × 42 tokens = $0.84
- Speed: ~API latency + network overhead

## Deployment on Oracle Cloud

```bash
# SSH into your Oracle server
ssh user@your-oracle-server

# Clone the repository
git clone https://github.com/yourusername/embedding-service.git
cd embedding-service

# Build and start the service
docker-compose up -d --build

# Watch logs during model download
docker-compose logs -f

# Test it works
curl http://localhost:8000/health
```

## License

MIT

## Credits

- **FastEmbed**: [Qdrant FastEmbed](https://github.com/qdrant/fastembed)
- **Model**: [nomic-ai/nomic-embed-text-v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Server**: [Uvicorn](https://www.uvicorn.org/)