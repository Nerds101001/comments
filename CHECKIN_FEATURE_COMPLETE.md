# Check-in/Check-out Feature - Complete Implementation

## ✅ What's Been Done

### 1. Database Model Created
- **New Table**: `checkins` table added to store check-in/check-out records
- **Fields**: emp_code, emp_name, comp_code, comp_name, checkin_date, checkin_time, checkout_time, duration_minutes, latitude, longitude, address, remarks
- **Unique Constraint**: Prevents duplicate records (emp_code + comp_code + checkin_date + checkin_time)
- **Indexes**: On emp_code, comp_code, and checkin_date for fast queries

### 2. Service Layer Updated
- **File**: `app/services/checkin_service.py`
- **Functions**:
  - `get_crm_token()` - Authenticate with CRM
  - `fetch_checkin_data_from_crm()` - Fetch data from CRM API
  - `sync_checkin_data()` - Sync data from CRM to database for all active reps
  - `get_checkin_data()` - Get check-in data from database
  - `analyze_visit_patterns()` - Analyze visit patterns from database
  - `get_team_visit_summary()` - Get team-wide statistics from database

### 3. API Endpoints Created
- **File**: `app/api/checkin.py`
- **Endpoints**:
  - `POST /api/checkin/sync` - Sync check-in data from CRM
  - `GET /api/checkin/rep/{emp_code}` - Get rep's check-in data
  - `GET /api/checkin/rep/{emp_code}/analysis` - Get rep's visit analysis
  - `GET /api/checkin/team/summary` - Get team visit summary
  - `GET /api/checkin/anomalies` - Get all visit anomalies
  - `GET /api/checkin/stats` - Get overall check-in statistics

### 4. Integration Complete
- Check-in router registered in `app/main.py`
- All endpoints available at `/api/checkin/*`
- Database model added to `app/models.py`

---

## 🚀 How to Use

### Step 1: Sync Data from CRM

Run the sync script to fetch check-in data from CRM:

```bash
python sync_checkin_data.py
```

Or use the API endpoint:

```bash
curl -X POST "http://localhost:8002/api/checkin/sync?days=30"
```

**What it does:**
- Fetches check-in data for all active reps from CRM
- Stores data in local database
- Updates existing records if they already exist
- Returns summary of sync operation

### Step 2: View Check-in Data

#### Get Rep's Check-in Data
```bash
curl "http://localhost:8002/api/checkin/rep/1811?days=7"
```

**Response:**
```json
{
  "emp_code": "1811",
  "from_date": "23-04-2026",
  "to_date": "30-04-2026",
  "total_visits": 15,
  "visits": [
    {
      "comp_code": "5989",
      "comp_name": "Patil Engineering Works",
      "checkin_date": "30-04-2026",
      "checkin_time": "10:30:00",
      "checkout_time": "11:15:00",
      "duration_minutes": 45,
      "address": "Pune, Maharashtra",
      "remarks": "Discussed VCI bags"
    }
  ]
}
```

#### Get Rep's Visit Analysis
```bash
curl "http://localhost:8002/api/checkin/rep/1811/analysis?days=7"
```

**Response:**
```json
{
  "emp_code": "1811",
  "rep_name": "Vishal Dhanraj Patil",
  "days_analyzed": 7,
  "analysis": {
    "total_visits": 15,
    "avg_duration_minutes": 42.5,
    "no_checkout": 2,
    "short_visits": 3,
    "long_visits": 1,
    "visits_by_day": {
      "30-04-2026": 3,
      "29-04-2026": 4
    },
    "anomalies": [
      {
        "type": "no_checkout",
        "customer": "ABC Company",
        "date": "30-04-2026",
        "checkin": "10:30:00"
      },
      {
        "type": "short_visit",
        "customer": "XYZ Industries",
        "date": "29-04-2026",
        "duration": "8 min"
      }
    ]
  }
}
```

#### Get Team Summary
```bash
curl "http://localhost:8002/api/checkin/team/summary?days=7"
```

**Response:**
```json
{
  "days_analyzed": 7,
  "summary": {
    "total_visits": 450,
    "total_reps": 96,
    "avg_visits_per_rep": 4.7,
    "reps_with_anomalies": 12,
    "top_performers": [
      {
        "emp_code": "1811",
        "name": "Vishal Dhanraj Patil",
        "visits": 15,
        "avg_duration": 42.5,
        "anomalies": 2
      }
    ],
    "needs_attention": [
      {
        "emp_code": "1752",
        "name": "Ravi Kumar Negi",
        "visits": 2,
        "avg_duration": 15.0,
        "anomalies": 5
      }
    ]
  }
}
```

#### Get All Anomalies
```bash
curl "http://localhost:8002/api/checkin/anomalies?days=7"
```

#### Get Overall Statistics
```bash
curl "http://localhost:8002/api/checkin/stats"
```

---

## 📊 Features

### 1. Data Storage
- ✅ All check-in data stored in local database
- ✅ Fast queries without hitting CRM API every time
- ✅ Automatic deduplication (no duplicate records)
- ✅ Update existing records on re-sync

### 2. Visit Analysis
- ✅ Total visits per rep
- ✅ Average visit duration
- ✅ Visits by day breakdown
- ✅ Anomaly detection:
  - No checkout (rep checked in but didn't check out)
  - Short visits (< 10 minutes)
  - Long visits (> 2 hours)

### 3. Team Insights
- ✅ Team-wide visit statistics
- ✅ Top performers (most visits)
- ✅ Reps needing attention (low visits or many anomalies)
- ✅ Average visits per rep

### 4. Sync Management
- ✅ Manual sync via API or script
- ✅ Configurable date range (1-90 days)
- ✅ Sync summary with counts and errors
- ✅ Handles all active reps automatically

---

## 🔄 Automatic Sync (Optional)

You can add automatic check-in sync to the scheduler in `app/main.py`:

```python
# In _start_scheduler() function, add:

async def _poll_checkin():
    async with AsyncSessionLocal() as db:
        from app.services import checkin_service
        logger.info("Check-in auto-sync: starting...")
        try:
            result = await checkin_service.sync_checkin_data(db, days=7)
            logger.info(f"Check-in sync: {result['total_new']} new, {result['total_updated']} updated")
        except Exception as exc:
            logger.error("Check-in sync error: %s", exc)

scheduler.add_job(
    _poll_checkin,
    trigger=IntervalTrigger(hours=6),  # Sync every 6 hours
    id="checkin_sync",
    replace_existing=True,
)
```

---

## 🎨 Frontend Integration (Optional)

You can add a "Check-in Reports" tab to the frontend to display:

### 1. Team Dashboard
- Total visits today/week
- Average visit duration
- Top performers list
- Anomalies alert

### 2. Rep Details
- Click on rep to see visit history
- Visit pattern analysis
- Customer visit frequency
- Map view of visits (using latitude/longitude)

### 3. Anomalies View
- List of all anomalies
- Filter by type (no checkout, short visit, long visit)
- Filter by rep or date range

### Example Frontend Code:

```javascript
// Load team summary
async function loadCheckInSummary() {
  const response = await fetch('/api/checkin/team/summary?days=7');
  const data = await response.json();
  
  // Display summary
  document.getElementById('totalVisits').textContent = data.summary.total_visits;
  document.getElementById('avgVisits').textContent = data.summary.avg_visits_per_rep;
  
  // Show top performers
  const topPerformers = data.summary.top_performers;
  // ... render list
}

// Load anomalies
async function loadAnomalies() {
  const response = await fetch('/api/checkin/anomalies?days=7');
  const data = await response.json();
  
  // Display anomalies with color coding
  const anomalies = data.anomalies;
  // ... render list
}

// Sync check-in data
async function syncCheckInData() {
  const response = await fetch('/api/checkin/sync?days=30', { method: 'POST' });
  const data = await response.json();
  
  alert(`Synced ${data.data.total_new} new check-ins!`);
  loadCheckInSummary(); // Refresh display
}
```

---

## 📝 CRM API Details

### Endpoint
```
POST https://api-crm.rustx.net/api/Reports/GetCheckinData
```

### Request
```json
{
  "empCode": 1811,
  "fromDate": "01-04-2026",
  "toDate": "30-04-2026"
}
```

### Response
```json
{
  "Data": [
    {
      "EMP_CODE": 1811,
      "EMP_NAME": "Vishal Dhanraj Patil",
      "COMP_CODE": 5989,
      "COMP_NAME": "Patil Engineering Works",
      "Date": "30-04-2026",
      "CheckInTime": "10:30:00",
      "CheckOutTime": "11:15:00",
      "Duration": "00:45:00",
      "Latitude": "18.5204",
      "Longitude": "73.8567",
      "Address": "Pune, Maharashtra",
      "Remarks": "Discussed VCI bags"
    }
  ],
  "StatusMessage": "Data has been fetched successfully",
  "StatusCode": 200
}
```

**Note:** `empCode` must be an integer, not a string!

---

## 🧪 Testing

### Test Sync
```bash
python sync_checkin_data.py
```

### Test API Endpoints
```bash
# Test sync
curl -X POST "http://localhost:8002/api/checkin/sync?days=30"

# Test rep data
curl "http://localhost:8002/api/checkin/rep/1811?days=7"

# Test analysis
curl "http://localhost:8002/api/checkin/rep/1811/analysis?days=7"

# Test team summary
curl "http://localhost:8002/api/checkin/team/summary?days=7"

# Test anomalies
curl "http://localhost:8002/api/checkin/anomalies?days=7"

# Test stats
curl "http://localhost:8002/api/checkin/stats"
```

### Test in Browser
Open: http://localhost:8002/docs

Look for "checkin" tag and try the endpoints with "Try it out" button.

---

## 📁 Files Modified/Created

### Created:
1. `sync_checkin_data.py` - Sync script
2. `test_checkin_api.py` - CRM API test script
3. `CHECKIN_FEATURE_COMPLETE.md` - This documentation

### Modified:
1. `app/models.py` - Added CheckIn model
2. `app/services/checkin_service.py` - Complete rewrite with database support
3. `app/api/checkin.py` - Updated endpoints to use database
4. `app/main.py` - Already has checkin router registered

---

## ✅ Summary

### What Works Now:
- ✅ Check-in data syncs from CRM to database
- ✅ All check-in data stored locally for fast access
- ✅ Visit pattern analysis with anomaly detection
- ✅ Team-wide statistics and insights
- ✅ API endpoints for all check-in operations
- ✅ Automatic deduplication and updates

### Next Steps (Optional):
1. Add frontend dashboard for check-in reports
2. Add automatic sync scheduler (every 6 hours)
3. Add map view using latitude/longitude
4. Add email alerts for anomalies
5. Add export to Excel/PDF functionality

---

## 🎯 Quick Start

1. **Sync data from CRM:**
   ```bash
   python sync_checkin_data.py
   ```

2. **View team summary:**
   ```bash
   curl "http://localhost:8002/api/checkin/team/summary?days=7"
   ```

3. **View anomalies:**
   ```bash
   curl "http://localhost:8002/api/checkin/anomalies?days=7"
   ```

4. **Open API docs:**
   http://localhost:8002/docs

---

**Check-in feature is now fully functional and integrated!** 🚀
