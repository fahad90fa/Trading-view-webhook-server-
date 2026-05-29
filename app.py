"""
TradingView Webhook Handler
Receives webhook signals from TradingView and processes them
Expected payload format:
{
    "symbol": "{{ticker}}",
    "order_action": "{{strategy.order.action}}",
    "entry_position": "{{strategy.order.price}}",
    "lot_size": 0.3
}
"""

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')
SIGNALS_FILE = 'signals.json'


def validate_signal(data):
    """Validate incoming signal data"""
    required_fields = ['symbol', 'order_action', 'entry_position', 'lot_size']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate data types
    if not isinstance(data['symbol'], str) or not data['symbol'].strip():
        return False, "Symbol must be a non-empty string"
    
    if not isinstance(data['order_action'], str) or not data['order_action'].strip():
        return False, "Order action must be a non-empty string"
    
    try:
        entry_price = float(data['entry_position'])
        if entry_price < 0:
            return False, "Entry position must be positive"
    except (ValueError, TypeError):
        return False, "Entry position must be a valid number"
    
    try:
        lot_size = float(data['lot_size'])
        if lot_size <= 0:
            return False, "Lot size must be positive"
    except (ValueError, TypeError):
        return False, "Lot size must be a valid number"
    
    return True, "Valid"


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Receive webhook from TradingView
    POST /webhook with JSON payload
    """
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        # Validate signal
        is_valid, validation_msg = validate_signal(data)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': validation_msg
            }), 400
        
        # Process signal
        signal = {
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'tradingview',
            'symbol': data['symbol'].upper(),
            'order_action': data['order_action'].upper(),
            'entry_position': float(data['entry_position']),
            'lot_size': float(data['lot_size']),
            'status': 'received'
        }
        
        # Keep only the latest signal by overwriting the file
        with open(SIGNALS_FILE, 'w') as f:
            f.write(json.dumps(signal))
        
        # Log to console
        print(f"✓ Signal received: {signal['symbol']} - {signal['order_action']} @ {signal['entry_position']}")
        
        return jsonify({
            'status': 'success',
            'message': 'Signal received and logged',
            'signal': signal
        }), 200
    
    except json.JSONDecodeError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid JSON format'
        }), 400
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/signals', methods=['GET'])
def get_signals():
    """
    Get the latest received signal from TradingView
    Returns only the original TradingView data fields
    GET /signals
    """
    try:
        if not os.path.exists(SIGNALS_FILE):
            return jsonify({}), 200

        with open(SIGNALS_FILE, 'r') as f:
            signal = json.load(f)

        if signal.get('source') != 'tradingview':
            return jsonify({}), 200

        clean_signal = {
            'symbol': signal.get('symbol'),
            'order_action': signal.get('order_action'),
            'entry_position': signal.get('entry_position'),
            'lot_size': signal.get('lot_size')
        }

        return jsonify(clean_signal), 200
    except json.JSONDecodeError:
        return jsonify({}), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Index endpoint with API documentation"""
    return jsonify({
        'name': 'TradingView Webhook Server',
        'version': '1.0',
        'endpoints': {
            'POST /webhook': 'Receive trading signals from TradingView',
            'GET /signals': 'Get all received signals',
            'GET /health': 'Health check',
            'GET /': 'This documentation'
        },
        'expected_payload': {
            'symbol': 'string (e.g., EURUSD)',
            'order_action': 'string (BUY or SELL)',
            'entry_position': 'number (entry price)',
            'lot_size': 'number (0.3)'
        }
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f"🚀 Starting TradingView Webhook Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
