# Reddit Sentiment Analysis MCP Server 🚀

[![Deploy to Dokploy](https://img.shields.io/badge/Deploy%20to-Dokploy-blue)](https://github.com/asmaamohamed0264/reddit-sentiment-mcp-server)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An **enterprise-grade Reddit sentiment analysis server** built with Claude AI and Model Context Protocol (MCP) that provides advanced sentiment analysis capabilities for business intelligence and product research.

## 🎯 Key Features

✅ **Enterprise Ready**: Production-grade server optimized for Dokploy deployment  
✅ **Claude AI Integration**: Advanced sentiment analysis with reasoning capabilities  
✅ **Multi-subreddit Analysis**: Analyze across multiple communities simultaneously  
✅ **Business Intelligence**: Extract pain points, feature requests, and urgency levels  
✅ **Real-time Processing**: Async architecture for high performance  
✅ **MCP Protocol**: Full Model Context Protocol implementation  
✅ **REST API**: Traditional REST endpoints alongside MCP  
✅ **Docker Optimized**: Secure, lightweight container deployment  

## 🚀 Quick Deploy to Dokploy

### 1. Create Application in Dokploy
- Create new project: `reddit-sentiment-mcp`
- Add new application: `reddit-sentiment-server`

### 2. Configure Git Repository
- **Repository**: `https://github.com/asmaamohamed0264/reddit-sentiment-mcp-server.git`
- **Branch**: `main`
- **Build Type**: `dockerfile`
- **Port**: `3000`

### 3. Environment Variables

Add these environment variables in Dokploy:

```env
# Reddit API Credentials (Required for full functionality)
REDDIT_CLIENT_ID=YJYHcDTzrPJ--F7vgOX4Fg
REDDIT_CLIENT_SECRET=your_reddit_secret_here
REDDIT_USER_AGENT=RedditSentimentBot/1.0 by YourUsername

# Claude AI Integration (Optional - falls back to rule-based analysis)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Server Configuration
PORT=3000
HOST=0.0.0.0
ENVIRONMENT=production
```

### 4. Deploy
- Click **Deploy** in Dokploy
- Server will be available at your Dokploy domain

## 📊 API Usage

### Health Check
```bash
GET /health
```

### Sentiment Analysis
```bash
POST /analyze
Content-Type: application/json

{
  "query": "iPhone 15",
  "subreddits": ["technology", "apple", "iphone"],
  "time_filter": "week",
  "limit": 10,
  "use_claude": true,
  "product_context": "Apple iPhone 15 launch analysis",
  "return_full_data": false
}
```

### Response Format
```json
{
  "overview": {
    "total_posts_analyzed": 25,
    "analysis_method": "claude_ai",
    "query": "iPhone 15",
    "subreddits_searched": ["technology", "apple", "iphone"],
    "time_filter": "week"
  },
  "sentiment_breakdown": {
    "distribution": {"positive": 15, "negative": 5, "neutral": 5},
    "percentages": {"positive": "60.0%", "negative": "20.0%", "neutral": "20.0%"},
    "overall_sentiment": "positive"
  },
  "key_insights": {
    "top_themes": ["performance", "design", "price"],
    "main_pain_points": ["battery life", "price point"],
    "top_feature_requests": ["better camera", "longer battery"]
  },
  "business_metrics": {
    "urgent_issues": 2,
    "high_impact_items": 4,
    "business_impact": "Generally positive reception with specific improvement areas identified"
  }
}
```

## 🔧 MCP Integration

This server implements the Model Context Protocol and can be used with Claude Desktop or other MCP clients:

```json
{
  "mcpServers": {
    "reddit-sentiment": {
      "command": "npx",
      "args": ["-c", "curl -X POST https://your-dokploy-domain.com/analyze"],
      "env": {}
    }
  }
}
```

## 🎯 Business Applications

### Product Management
- **Feature Prioritization**: Based on user feedback volume and sentiment
- **Competitive Analysis**: Track brand mentions and sentiment
- **Release Impact**: Monitor sentiment changes after product launches

### Customer Success
- **Proactive Issue Identification**: Early warning through pain point analysis
- **Support Optimization**: Prevent tickets via community sentiment monitoring
- **Satisfaction Tracking**: Monitor customer satisfaction across product updates

### Marketing Intelligence
- **Brand Perception**: Monitor brand sentiment across relevant communities
- **Campaign Effectiveness**: Measure sentiment shifts during campaigns
- **Influencer Identification**: Find high-impact feedback and discussions

## 🏗️ Technical Architecture

- **FastAPI**: High-performance async web framework
- **AsyncPRAW**: Async Reddit API wrapper for optimal performance
- **Claude AI**: Advanced sentiment analysis with reasoning
- **MCP Protocol**: Standard AI assistant integration
- **Docker**: Secure containerized deployment
- **Health Checks**: Dokploy-optimized monitoring

## 🔒 Security Features

- Non-root container user
- Environment-based configuration
- Input validation with Pydantic
- Rate limiting and timeout protection
- Secure API key handling

## 🚧 Advanced Configuration

### Custom Docker Build
```bash
docker build -t reddit-sentiment-mcp .
docker run -p 3000:3000 \
  -e REDDIT_CLIENT_ID=your_id \
  -e REDDIT_CLIENT_SECRET=your_secret \
  -e ANTHROPIC_API_KEY=your_key \
  reddit-sentiment-mcp
```

### Local Development
```bash
git clone https://github.com/asmaamohamed0264/reddit-sentiment-mcp-server.git
cd reddit-sentiment-mcp-server
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python server.py
```

## 📈 Performance & Limits

- **Concurrent Requests**: Async architecture supports high concurrency
- **Reddit API**: Respects Reddit rate limits (60-100 requests/minute)
- **Claude AI**: Optimized prompts for cost-effective analysis
- **Memory Usage**: ~50MB base, scales with request volume
- **Response Time**: ~2-5 seconds for typical analysis

## 🤝 Support & Contributing

- **Issues**: [GitHub Issues](https://github.com/asmaamohamed0264/reddit-sentiment-mcp-server/issues)
- **Documentation**: This README and inline code comments
- **License**: MIT - Use it however you want!

## 🏆 Why This Server?

**Enterprise Grade**: Built for production use with proper error handling, logging, and monitoring.

**AI-Powered**: Uses Claude AI for sophisticated sentiment analysis beyond simple keyword matching.

**Dokploy Optimized**: Specifically designed for seamless Dokploy deployment with health checks and proper containerization.

**Full-Stack**: Provides both MCP protocol integration AND REST API for maximum flexibility.

**Business Focused**: Extracts actionable business intelligence, not just sentiment scores.

---

**Built with ❤️ for the MCP community and optimized for Dokploy deployment**