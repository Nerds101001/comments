#!/bin/bash
echo "🚀 Running Railway startup tasks..."

# Run migration (safe to run multiple times - it checks if already exists)
echo "📊 Running check-in sync tracking migration..."
python add_checkin_sync_tracking.py

# Start the application
echo "🌐 Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
