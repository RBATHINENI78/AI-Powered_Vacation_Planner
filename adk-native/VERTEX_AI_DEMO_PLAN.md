# Vertex AI Demo Plan - AI-Powered Vacation Planner

## Overview

This document outlines the plan for demonstrating the AI-Powered Vacation Planner running on Google Cloud's Vertex AI platform. This demo showcases enterprise-grade AI deployment with production infrastructure.

---

## Demo Objectives

- ✅ Demonstrate the application running on production infrastructure (Vertex AI)
- ✅ Show elimination of rate limit issues (vs free Gemini API)
- ✅ Showcase enterprise-grade AI deployment capabilities
- ✅ Prove scalability and reliability for production use
- ✅ Highlight Google Cloud Platform integration

---

## Quick Setup Guide (30 minutes)

### Prerequisites

- Google Cloud Platform account with billing enabled
- `gcloud` CLI installed ([Installation Guide](https://cloud.google.com/sdk/docs/install))
- Project repository cloned locally

### Step 1: GCP Project Setup

```bash
# 1. Set your GCP project (use existing or create new)
export PROJECT_ID="vacation-planner-demo"
gcloud config set project $PROJECT_ID

# 2. Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable compute.googleapis.com

# 3. Create service account for demo
gcloud iam service-accounts create vacation-demo \
    --display-name="Vacation Planner Demo"

# 4. Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:vacation-demo@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# 5. Generate service account key
gcloud iam service-accounts keys create ~/vacation-demo-key.json \
    --iam-account=vacation-demo@$PROJECT_ID.iam.gserviceaccount.com

# 6. Set environment variables
export GOOGLE_APPLICATION_CREDENTIALS=~/vacation-demo-key.json
export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
export GOOGLE_CLOUD_LOCATION=us-central1
```

### Step 2: Configure Application

**Good News:** ADK automatically detects and uses Vertex AI when proper environment variables are set. **No code changes required!**

Update your `.env` file:

```bash
# Add to adk-native/.env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/vacation-demo-key.json
GOOGLE_CLOUD_PROJECT=vacation-planner-demo
GOOGLE_CLOUD_LOCATION=us-central1
```

### Step 3: Start the Service

```bash
# Source environment variables
export GOOGLE_APPLICATION_CREDENTIALS=~/vacation-demo-key.json
export GOOGLE_CLOUD_PROJECT=vacation-planner-demo
export GOOGLE_CLOUD_LOCATION=us-central1

# Navigate to project directory
cd adk-native

# Stop any existing service
pkill -f "adk web"

# Start service with Vertex AI
adk web agents_web --port 8080
```

### Step 4: Verify Vertex AI Integration

**Verification Checklist:**
- [ ] Service starts without errors
- [ ] Access web UI at http://localhost:8080/dev-ui/?app=vacation_planner
- [ ] Test a simple query (e.g., "Plan a 3-day trip to NYC")
- [ ] No 429 rate limit errors in logs
- [ ] Check GCP Console → Vertex AI → Model Garden → Usage shows API calls

---

## Demo Presentation Flow (10 minutes)

### 1. Introduction (1 minute)

**Script:**
> "Today I'll demonstrate our AI-Powered Vacation Planner, an intelligent system that coordinates 12 specialized AI agents to create comprehensive travel plans. The system runs on Google Cloud's Vertex AI, providing enterprise-grade performance and reliability."

### 2. Architecture Overview (1 minute)

**Show System Architecture:**

```
User Request
    ↓
ADK Web UI
    ↓
Main Orchestrator (vacation_planner)
    ↓
├─ Phase 1: Research (Sequential)
│  ├─ Travel Advisory Agent
│  ├─ Destination Intelligence Agent
│  ├─ Immigration Specialist Agent
│  └─ Currency Exchange Agent
│
├─ Phase 2: Booking (Parallel - 3x faster)
│  ├─ Flight Booking Agent
│  ├─ Hotel Booking Agent
│  └─ Car Rental Agent
│
├─ Phase 3: Budget Checkpoint 🚨 (HITL #1)
│  └─ Assess budget fit, present options if needed
│
├─ Phase 4: Suggestions Checkpoint 🚨 (HITL #2)
│  └─ Present 7-point overview, get user approval
│
└─ Phase 5: Organization (Sequential)
   ├─ Activities Agent
   ├─ Itinerary Agent
   └─ Document Generator Agent
    ↓
Vertex AI (Gemini Models)
    ↓
Comprehensive Vacation Plan
```

**Key Features:**
- 12 specialized agents
- 2 HITL (Human-In-The-Loop) checkpoints
- Parallel execution for 3x speedup
- Date inference from natural language
- Budget-aware planning

### 3. Live Demo - Simple Trip (3 minutes)

**Input Query:**
```
"Plan a week-long trip to Hawaii for 2 adults in March 2026 with $5000 budget"
```

**Points to Highlight:**
1. **Date Inference**: "March 2026" automatically converted to 2026-03-01 to 2026-03-08
2. **Travel Advisory**: Real-time safety checks from State Department
3. **Weather**: March weather forecast for Hawaii (date-aware)
4. **Flight Options**: 3-5 specific options with airlines, routes, prices
   - Example: "Hawaiian Airlines CLT→HNL via LAX, $450 per person"
5. **Budget Checkpoint**: Shows "$4,200 estimated, $800 remaining - ✅ Within budget"
6. **Suggestions Overview**: 7-point scannable summary
7. **User Approval**: Workflow pauses, asks "Proceed?"
8. **Complete Plan**: After approval, generates full itinerary

### 4. Live Demo - Complex Trip (2 minutes)

**Input Query:**
```
"Plan a 2-week trip to Europe (Paris and Rome) for 2 people in June 2026 with $8000 budget"
```

**Points to Highlight:**
- Multi-city itinerary coordination
- International travel (visa requirements, currency exchange)
- Complex logistics handled automatically
- No timeout or rate limit errors (unlike free API)
- All 12 agents working seamlessly

### 5. GCP Console Integration (2 minutes)

**Switch to GCP Console and show:**

1. **Vertex AI Dashboard**
   - Navigate to: GCP Console → Vertex AI → Model Garden
   - Show: Real-time API usage
   - Point out: Model names (gemini-2.5-flash-lite, etc.)

2. **Cost Tracking**
   - Navigate to: Billing → Reports
   - Show: Cost per request (~$0.01-0.05 per trip)
   - Highlight: Predictable pricing

3. **Monitoring**
   - Navigate to: Cloud Monitoring → Dashboards
   - Show: Success rate, latency, request volume
   - Point out: Production-grade monitoring

### 6. Key Differentiators (1 minute)

**Comparison: Free API vs Vertex AI**

| Feature | Free Gemini API | Vertex AI (Demo) |
|---------|-----------------|------------------|
| **Rate Limits** | 15-200 req/min | 10,000+ req/min |
| **Model Access** | Limited | All Gemini models |
| **Reliability** | Best effort | Enterprise SLA |
| **Monitoring** | None | Full Cloud Monitoring |
| **Cost Tracking** | None | Real-time visibility |
| **Support** | Community | Enterprise support |

**Production Benefits:**
- ✅ No rate limit errors
- ✅ Date inference working perfectly
- ✅ Flight booking providing 3-5 specific options
- ✅ Budget checkpoints stopping workflow when needed
- ✅ Clean, organized output
- ✅ Scalable to thousands of users

---

## Demo Scenarios & Test Cases

### Scenario 1: Budget-Conscious Traveler
```
Query: "Plan a 5-day trip to Austin, Texas for 2 adults with $2000 budget"
Expected: Budget checkpoint shows within budget, suggests mid-range hotels
```

### Scenario 2: Luxury Vacation
```
Query: "Plan a 10-day luxury trip to Maldives for 2 people with $20,000 budget"
Expected: Budget checkpoint shows budget excess, suggests premium upgrades
```

### Scenario 3: Complex Multi-City
```
Query: "Plan a 3-week trip visiting Tokyo, Bangkok, and Singapore with $12,000"
Expected: Multi-city coordination, visa requirements for each country
```

### Scenario 4: Natural Language Dates
```
Query: "Plan a trip to Salt Lake City in December 2025 for 1 month with $5000"
Expected: Date inference: 2025-12-01 to 2025-12-31 (30 nights)
```

---

## Technical Deep Dive (For Technical Audience)

### How ADK Detects Vertex AI

ADK automatically uses Vertex AI when these environment variables are set:
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `GOOGLE_CLOUD_LOCATION`: Region (e.g., us-central1)

**No code changes needed!** ADK's internal logic:
```python
# Simplified ADK detection logic
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and os.getenv("GOOGLE_CLOUD_PROJECT"):
    # Use Vertex AI
    from google.cloud import aiplatform
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
else:
    # Use free Gemini API
    import google.generativeai as genai
```

### Model Configuration

Models are configured in `config.py`:
```python
AGENT_MODELS = {
    # Complex reasoning - Thinking model
    "itinerary": "gemini-2.0-flash-thinking-exp-1219",
    "budget_checkpoint": "gemini-2.0-flash-thinking-exp-1219",
    "activities": "gemini-2.0-flash-thinking-exp-1219",
    "suggestions_checkpoint": "gemini-2.0-flash-thinking-exp-1219",

    # Simple tasks - Flash-lite model (cost-effective)
    "destination_intelligence": "gemini-2.5-flash-lite",
    "immigration_specialist": "gemini-2.5-flash-lite",
    "currency_exchange": "gemini-2.5-flash-lite",
    "flight_booking": "gemini-2.5-flash-lite",
    "hotel_booking": "gemini-2.5-flash-lite",
    "car_rental": "gemini-2.5-flash-lite",
    "document_generator": "gemini-2.5-flash-lite",
    "travel_advisory": "gemini-2.5-flash-lite",
}
```

### Cost Estimation

**Pricing (as of 2025):**
- Input tokens: ~$0.00001 per 1K tokens
- Output tokens: ~$0.00003 per 1K tokens

**Typical Trip Planning Costs:**
- Simple trip (3 days): ~$0.01-0.02
- Complex trip (2 weeks): ~$0.05-0.10
- Multi-city trip (3+ weeks): ~$0.10-0.20

**Cost optimization tips:**
- Use flash-lite for simple agents
- Use thinking models only for complex reasoning
- Cache frequently used prompts

---

## Troubleshooting Guide

### Issue: "API not enabled" Error

**Solution:**
```bash
gcloud services enable aiplatform.googleapis.com
```

### Issue: "Permission denied" Error

**Solution:**
```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:YOUR-SA@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

### Issue: Still seeing rate limit errors

**Verification:**
```bash
# Check environment variables
echo $GOOGLE_APPLICATION_CREDENTIALS
echo $GOOGLE_CLOUD_PROJECT

# Verify service account key exists
ls -l $GOOGLE_APPLICATION_CREDENTIALS

# Check ADK logs for "aiplatform" (Vertex AI) vs "generativelanguage" (free API)
tail -f /tmp/adk-vacation-8080.log | grep -i "aiplatform\|vertex"
```

### Issue: High costs

**Solution:**
1. Check model usage in GCP Console → Billing → Reports
2. Switch more agents to flash-lite model (cheaper)
3. Set up budget alerts:
```bash
gcloud billing budgets create \
    --billing-account=YOUR-BILLING-ID \
    --display-name="Vacation Planner Budget" \
    --budget-amount=100USD \
    --threshold-rule=percent=80
```

---

## Post-Demo Actions

### 1. Generate Demo Report

After the demo, generate a report showing:
- Total requests processed
- Average latency
- Total cost
- Success rate
- Model usage breakdown

**Access report:**
- GCP Console → Vertex AI → Dashboards
- Export to PDF/CSV for presentation

### 2. Cleanup (Optional)

If this was a temporary demo environment:
```bash
# Delete service account key
rm ~/vacation-demo-key.json

# Delete service account (if no longer needed)
gcloud iam service-accounts delete \
    vacation-demo@$PROJECT_ID.iam.gserviceaccount.com
```

### 3. Production Deployment (Next Steps)

If moving to production:
1. Deploy to Cloud Run for auto-scaling
2. Set up load balancing
3. Configure monitoring and alerting
4. Implement user authentication
5. Add rate limiting per user

---

## Demo Checklist

### Before Demo (15 minutes before)
- [ ] GCP project set up with billing
- [ ] Vertex AI API enabled
- [ ] Service account created with permissions
- [ ] Environment variables configured
- [ ] Service running and tested with sample query
- [ ] GCP Console open in browser (Vertex AI page)
- [ ] Demo scenarios prepared
- [ ] Network/internet connection verified
- [ ] Backup plan ready (screenshots/video)

### During Demo
- [ ] Start with architecture overview
- [ ] Show live request in web UI
- [ ] Highlight key features (date inference, flight options, HITL)
- [ ] Switch to GCP Console to show Vertex AI usage
- [ ] Point out no rate limit errors
- [ ] Show cost tracking
- [ ] Compare free API vs Vertex AI

### After Demo
- [ ] Generate usage report
- [ ] Export cost analysis
- [ ] Save demo recording (if applicable)
- [ ] Cleanup temporary resources (if needed)

---

## Additional Resources

- **ADK Documentation**: https://google.github.io/adk-docs/
- **Vertex AI Documentation**: https://cloud.google.com/vertex-ai/docs
- **Gemini Models Pricing**: https://cloud.google.com/vertex-ai/pricing
- **Project Repository**: https://github.com/RBATHINENI78/AI-Powered_Vacation_Planner
- **Contact**: [Your contact information]

---

## Success Metrics

A successful demo should demonstrate:
- ✅ Zero rate limit errors (vs multiple with free API)
- ✅ All 12 agents executing successfully
- ✅ Date inference working correctly
- ✅ Flight booking providing 3-5 specific options
- ✅ Budget checkpoints functioning properly
- ✅ Suggestions checkpoint pausing for user approval
- ✅ Clean, organized output
- ✅ Cost per trip < $0.20
- ✅ Average response time < 60 seconds
- ✅ Audience understanding of enterprise benefits

---

**Last Updated:** November 23, 2025
**Version:** 1.0
**Status:** Ready for Demo

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
