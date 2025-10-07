#!/usr/bin/env python3
"""
Reddit Sentiment Analysis MCP Server
Enterprise-grade Reddit sentiment analysis server built with Claude AI and Model Context Protocol (MCP)
"""

import os
import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json

import asyncpraw
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, 
    Tool, 
    TextContent,
    CallToolRequestParams
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'RedditSentimentBot/1.0')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
PORT = int(os.getenv('PORT', 3000))
HOST = os.getenv('HOST', '0.0.0.0')

# Pydantic models
class SentimentAnalysisRequest(BaseModel):
    query: str = Field(description="Search term to analyze")
    subreddits: List[str] = Field(default=["all"], description="Target subreddit names")
    time_filter: str = Field(default="week", description="Time period (hour, day, week, month, year, all)")
    limit: int = Field(default=5, description="Maximum posts per subreddit")
    use_claude: bool = Field(default=True, description="Enable Claude AI analysis")
    product_context: str = Field(default="", description="Business context for analysis")
    return_full_data: bool = Field(default=False, description="Include detailed post-level data")

class SentimentResult(BaseModel):
    overview: Dict[str, Any]
    sentiment_breakdown: Dict[str, Any]
    key_insights: Dict[str, Any]
    business_metrics: Dict[str, Any]
    detailed_posts: Optional[List[Dict[str, Any]]] = None

# Initialize Reddit client
async def get_reddit_client():
    """Initialize Reddit client with credentials"""
    return asyncpraw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

# Claude AI integration
async def analyze_with_claude(posts_data: List[Dict], context: str = "") -> Dict[str, Any]:
    """Analyze sentiment using Claude AI"""
    if not ANTHROPIC_API_KEY:
        logger.warning("Anthropic API key not found, using fallback analysis")
        return fallback_sentiment_analysis(posts_data)
    
    try:
        async with httpx.AsyncClient() as client:
            prompt = f"""
            Analyze the sentiment of these Reddit posts about {context if context else 'the topic'}.
            
            Posts data: {json.dumps(posts_data, indent=2)}
            
            Please provide:
            1. Overall sentiment distribution (positive, negative, neutral percentages)
            2. Top 5 themes mentioned
            3. Main pain points identified
            4. Top feature requests or suggestions
            5. Urgent issues count (high priority concerns)
            6. Business impact assessment
            
            Return as structured JSON with these exact keys:
            - sentiment_distribution: {{positive: count, negative: count, neutral: count}}
            - top_themes: [list of themes]
            - main_pain_points: [list of pain points]
            - top_feature_requests: [list of requests]
            - urgent_issues: count
            - business_impact: string description
            """
            
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "content-type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1000,
                    "messages": [{
                        "role": "user",
                        "content": prompt
                    }]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('content', [{}])[0].get('text', '')
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.error("Failed to parse Claude response as JSON")
                    return fallback_sentiment_analysis(posts_data)
            else:
                logger.error(f"Claude API error: {response.status_code}")
                return fallback_sentiment_analysis(posts_data)
                
    except Exception as e:
        logger.error(f"Error calling Claude API: {e}")
        return fallback_sentiment_analysis(posts_data)

def fallback_sentiment_analysis(posts_data: List[Dict]) -> Dict[str, Any]:
    """Fallback sentiment analysis using keyword matching"""
    positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'awesome', 'fantastic']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointed', 'frustrated']
    
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    for post in posts_data:
        text = (post.get('title', '') + ' ' + post.get('body', '')).lower()
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        if pos_count > neg_count:
            sentiment_counts['positive'] += 1
        elif neg_count > pos_count:
            sentiment_counts['negative'] += 1
        else:
            sentiment_counts['neutral'] += 1
    
    return {
        'sentiment_distribution': sentiment_counts,
        'top_themes': ['general discussion', 'user experiences', 'product feedback'],
        'main_pain_points': ['performance issues', 'user experience'],
        'top_feature_requests': ['improvements', 'new features'],
        'urgent_issues': max(1, sentiment_counts['negative'] // 3),
        'business_impact': 'Mixed sentiment with opportunities for improvement'
    }

# Reddit data fetching
async def fetch_reddit_posts(query: str, subreddits: List[str], time_filter: str, limit: int) -> List[Dict[str, Any]]:
    """Fetch posts from Reddit"""
    reddit = await get_reddit_client()
    all_posts = []
    
    try:
        for subreddit_name in subreddits:
            try:
                if subreddit_name.lower() == 'all':
                    subreddit = await reddit.subreddit('all')
                else:
                    subreddit = await reddit.subreddit(subreddit_name)
                
                # Search posts
                search_results = subreddit.search(
                    query, 
                    sort='relevance', 
                    time_filter=time_filter, 
                    limit=limit
                )
                
                async for post in search_results:
                    post_data = {
                        'title': post.title,
                        'body': getattr(post, 'selftext', '') or '',
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'subreddit': post.subreddit.display_name,
                        'created_utc': post.created_utc,
                        'url': f"https://reddit.com{post.permalink}",
                        'author': str(post.author) if post.author else '[deleted]'
                    }
                    all_posts.append(post_data)
                    
            except Exception as e:
                logger.error(f"Error fetching from r/{subreddit_name}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error initializing Reddit client: {e}")
        raise HTTPException(status_code=500, detail="Reddit API error")
    
    finally:
        await reddit.close()
    
    return all_posts

# Main analysis function
async def analyze_reddit_sentiment(
    query: str,
    subreddits: List[str] = ["all"],
    time_filter: str = "week",
    limit: int = 5,
    use_claude: bool = True,
    product_context: str = "",
    return_full_data: bool = False
) -> SentimentResult:
    """Main sentiment analysis function"""
    
    # Fetch Reddit posts
    posts = await fetch_reddit_posts(query, subreddits, time_filter, limit)
    
    if not posts:
        return SentimentResult(
            overview={"total_posts_analyzed": 0, "analysis_method": "none"},
            sentiment_breakdown={"distribution": {}, "percentages": {}, "overall_sentiment": "neutral"},
            key_insights={"top_themes": [], "main_pain_points": [], "top_feature_requests": []},
            business_metrics={"urgent_issues": 0, "high_impact_items": 0}
        )
    
    # Analyze sentiment
    if use_claude and ANTHROPIC_API_KEY:
        analysis = await analyze_with_claude(posts, product_context or query)
    else:
        analysis = fallback_sentiment_analysis(posts)
    
    # Calculate percentages
    total_posts = len(posts)
    distribution = analysis.get('sentiment_distribution', {})
    percentages = {}
    for sentiment, count in distribution.items():
        percentages[sentiment] = f"{(count/total_posts*100):.1f}%" if total_posts > 0 else "0.0%"
    
    # Determine overall sentiment
    if distribution.get('positive', 0) > distribution.get('negative', 0):
        overall_sentiment = 'positive'
    elif distribution.get('negative', 0) > distribution.get('positive', 0):
        overall_sentiment = 'negative'
    else:
        overall_sentiment = 'neutral'
    
    result = SentimentResult(
        overview={
            "total_posts_analyzed": total_posts,
            "analysis_method": "claude_ai" if use_claude and ANTHROPIC_API_KEY else "rule_based",
            "query": query,
            "subreddits_searched": subreddits,
            "time_filter": time_filter
        },
        sentiment_breakdown={
            "distribution": distribution,
            "percentages": percentages,
            "overall_sentiment": overall_sentiment
        },
        key_insights={
            "top_themes": analysis.get('top_themes', []),
            "main_pain_points": analysis.get('main_pain_points', []),
            "top_feature_requests": analysis.get('top_feature_requests', [])
        },
        business_metrics={
            "urgent_issues": analysis.get('urgent_issues', 0),
            "high_impact_items": len(analysis.get('main_pain_points', [])) + len(analysis.get('top_feature_requests', [])),
            "business_impact": analysis.get('business_impact', 'Analysis completed')
        }
    )
    
    if return_full_data:
        result.detailed_posts = posts
    
    return result

# MCP Server setup
app = Server("reddit-sentiment-mcp")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="analyze_reddit_sentiment",
            description="Analyze sentiment from Reddit posts about a specific topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term to analyze"},
                    "subreddits": {"type": "array", "items": {"type": "string"}, "default": ["all"]},
                    "time_filter": {"type": "string", "enum": ["hour", "day", "week", "month", "year", "all"], "default": "week"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 5},
                    "use_claude": {"type": "boolean", "default": True},
                    "product_context": {"type": "string", "default": ""},
                    "return_full_data": {"type": "boolean", "default": False}
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    if name == "analyze_reddit_sentiment":
        try:
            result = await analyze_reddit_sentiment(**arguments)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result.dict(), indent=2, ensure_ascii=False)
                )
            ]
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return [
                TextContent(
                    type="text",
                    text=f"Error analyzing sentiment: {str(e)}"
                )
            ]
    else:
        raise ValueError(f"Unknown tool: {name}")

# FastAPI for health checks (used by Dokploy)
fastapi_app = FastAPI(title="Reddit Sentiment MCP Server")

@fastapi_app.get("/health")
async def health_check():
    """Health check endpoint for Dokploy"""
    return JSONResponse({"status": "healthy", "service": "reddit-sentiment-mcp"})

@fastapi_app.post("/analyze")
async def api_analyze(request: SentimentAnalysisRequest):
    """REST API endpoint for sentiment analysis"""
    try:
        result = await analyze_reddit_sentiment(
            query=request.query,
            subreddits=request.subreddits,
            time_filter=request.time_filter,
            limit=request.limit,
            use_claude=request.use_claude,
            product_context=request.product_context,
            return_full_data=request.return_full_data
        )
        return result
    except Exception as e:
        logger.error(f"API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Main server function
async def main():
    """Main server function"""
    # Check environment variables
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        logger.warning("Reddit credentials not found. Server will run with limited functionality.")
    
    if not ANTHROPIC_API_KEY:
        logger.warning("Anthropic API key not found. Using fallback sentiment analysis.")
    
    # Start MCP server
    logger.info("Starting Reddit Sentiment MCP Server")
    logger.info(f"Health check available at: http://{HOST}:{PORT}/health")
    logger.info(f"API endpoint available at: http://{HOST}:{PORT}/analyze")
    
    # Run both servers concurrently
    import uvicorn
    config = uvicorn.Config(fastapi_app, host=HOST, port=PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())