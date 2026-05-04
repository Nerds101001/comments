#!/bin/bash
echo "🚀 Running Railway startup tasks..."

# Run check-in sync tracking migration
echo "📊 Running check-in sync tracking migration..."
python add_checkin_sync_tracking.py

# Run SMTP settings migration
echo "📧 Running SMTP settings migration..."
python add_smtp_settings_to_db.py

# Start the application
echo "🌐 Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
