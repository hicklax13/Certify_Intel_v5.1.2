# Power Query Connection Guide

Connect your Excel dashboard to the Certify Intel API for live data.

---

## Prerequisites

1. **Backend server running** at `http://localhost:8000`
2. Excel 2016 or later (with Power Query)

---

## Option 1: Connect via JSON API (Recommended)

### Step 1: Open Power Query

1. Open Excel
2. Go to **Data** tab → **Get Data** → **From Other Sources** → **From Web**

### Step 2: Enter API URL

Enter this URL:

```
http://localhost:8000/api/export/json
```

Click **OK**.

### Step 3: Transform Data

1. Power Query will show the JSON response
2. Click on **competitors** to expand the record
3. Click **To Table** to convert to table
4. Click the expand icon (double arrows) on the column header
5. Select all columns you want → **OK**

### Step 4: Load to Excel

1. Click **Close & Load**
2. Data will load into a new sheet

### Step 5: Set Up Refresh

1. Right-click the table
2. Select **Properties**
3. Check **Refresh every X minutes**
4. Or click **Refresh All** in the Data tab to manually refresh

---

## Option 2: Direct Excel Export

### Download Latest Excel

1. Open browser
2. Go to: `http://localhost:8000/api/export/excel`
3. Excel file downloads automatically
4. Open and copy data to your dashboard

---

## Power Query M Code (Advanced)

Paste this into a blank query to connect:

```powerquery
let
    Source = Json.Document(Web.Contents("http://localhost:8000/api/export/json")),
    competitors = Source[competitors],
    ToTable = Table.FromList(competitors, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    ExpandColumns = Table.ExpandRecordColumn(ToTable, "Column1", {
        "name", "website", "status", "threat_level", "last_updated",
        "pricing_model", "base_price", "price_unit",
        "product_categories", "key_features", "integration_partners", "certifications",
        "target_segments", "customer_size_focus", "geographic_focus",
        "customer_count", "key_customers", "g2_rating",
        "employee_count", "year_founded", "headquarters",
        "funding_total", "latest_round", "pe_vc_backers",
        "website_traffic", "social_following", "recent_launches", "news_mentions"
    })
in
    ExpandColumns
```

### To Use This Code

1. **Data** → **Get Data** → **From Other Sources** → **Blank Query**
2. Click **Advanced Editor**
3. Paste the code above
4. Click **Done**
5. Click **Close & Load**

---

## API Endpoints Reference

| Endpoint | Description |
|----------|-------------|
| `/api/export/json` | JSON data for Power Query |
| `/api/export/excel` | Download Excel file directly |
| `/api/competitors` | List all competitors (JSON) |
| `/api/dashboard/stats` | Summary statistics |

---

## Troubleshooting

### "Unable to connect"

- Make sure the backend server is running
- Check the URL is correct: `http://localhost:8000`

### "Access denied"

- The API allows all origins by default
- Check if a firewall is blocking port 8000

### Data not refreshing

- Click **Refresh All** in the Data tab
- Or set up automatic refresh in query properties

---

## Running the Backend Server

```powershell
cd C:\Users\conno\Downloads\Certify_Health_Intelv1\backend
python -m uvicorn main:app --reload --port 8000
```

The server must be running for Power Query to connect.
