# TradingView Webhook Server

TradingView alerts ko receive karne ke liye Flask webhook server.

## Setup

### 1. Dependencies Install Karein
```bash
pip install -r requirements.txt
```

### 2. Environment File Setup
`.env.example` ko copy karke `.env` banayein:
```bash
cp .env.example .env
```

`.env` file ko edit karein:
```
FLASK_ENV=production
PORT=5000
WEBHOOK_SECRET=your_secret_key
```

### 3. Server Run Karein (Local Testing)
```bash
python app.py
```

Server start hoga: `http://localhost:5000`

## TradingView Integration

### Step 1: TradingView Alert Create Karein
1. TradingView Chart kholeein
2. **Alert** button click karein
3. Naya Alert create karein
4. **Webhook URL** mein yeh URL daalein:
   ```
   http://your-server-ip:5000/webhook
   ```
   
   Ya agar Railway/Heroku deploy ho toh:
   ```
   https://your-app-name.railway.app/webhook
   ```

### Step 2: Message Format
TradingView Alert ke **Message** field mein JSON copy-paste karein:
```json
{
  "symbol": "{{ticker}}",
  "order_action": "{{strategy.order.action}}",
  "entry_position": "{{strategy.order.price}}",
  "lot_size": 0.3
}
```

### Step 3: Alert Trigger Karein
- Alert save karein
- Jab bhi condition match ho toh webhook call hoga

## API Endpoints

### 1. Receive Signal
```
POST /webhook
Content-Type: application/json

{
  "symbol": "EURUSD",
  "order_action": "BUY",
  "entry_position": 1.0850,
  "lot_size": 0.3
}
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Signal received and logged",
  "signal": {
    "timestamp": "2026-05-29T10:30:45.123456",
    "symbol": "EURUSD",
    "order_action": "BUY",
    "entry_position": 1.0850,
    "lot_size": 0.3,
    "status": "received"
  }
}
```

### 2. Get All Signals
```
GET /signals
```

Sab received signals dekhen (signals.jsonl mein jo logged hain)

### 3. Health Check
```
GET /health
```

Server status check karein

### 4. Documentation
```
GET /
```

API documentation dekhen

## Deployment (Railway)

### 1. Project Setup
Railway par account banayein: https://railway.app

### 2. GitHub Connect Karein
Aapka code GitHub par push karein

### 3. Railway Deployment
1. Railway dashboard kholeein
2. New Project > GitHub repo select karein
3. Build aur deploy khud ho jayega
4. **Webhook URL:**
   ```
   https://your-app-name.railway.app/webhook
   ```

## Signals Check Karein

Server chalte hue:
```bash
curl http://localhost:5000/signals
```

Ya browser mein:
```
http://localhost:5000/signals
```

Sab signals dekh sakte ho JSON format mein.

## Troubleshooting

### Issue: "Connection Refused"
- Server running hai kya? `python app.py` run karein
- Port 5000 use ho raha hai? `.env` mein PORT change karein

### Issue: "Invalid JSON format"
- Message ko check karein - double quotes use karein
- {{ticker}} properly set hai kya?

### Issue: "Missing required field"
- TradingView message mein sab fields hain kya?
- symbol, order_action, entry_position, lot_size - sab mandatory hain

## Files Explanation

- `app.py` - Main Flask webhook server
- `requirements.txt` - Python dependencies
- `signals.jsonl` - Log file (sab signals yahan save hote hain)
- `.env.example` - Environment variables template
- `Procfile` - Heroku/Railway deployment config
- `railway.toml` - Railway platform config
# Trading-view-webhook-server-
