# Member C — Frontend Development Tasks

The database is ready and the backend API is live. You can start building the frontend dashboard.

---

## Prerequisites
- Member A has restarted the backend with the updated database
- API running at `http://localhost:5000`
- Test: `http://localhost:5000/api/health` should return `{"status": "healthy"}`

## API Endpoints Available

| Endpoint | Returns |
|----------|---------|
| `GET /api/health` | Health check + DB status |
| `GET /api/trips?limit=N&offset=N` | Paginated trip records |
| `GET /api/stats/summary` | Total trips, avg fare, avg distance, avg duration, etc. |
| `GET /api/insights/hourly_pattern` | Trip count & avg fare for each of 24 hours |
| `GET /api/insights/borough_stats` | Trips, avg fare, total revenue per borough |
| `GET /api/insights/top_locations?limit=10` | Top pickup zones by trip count |
| `GET /api/insights/daily_pattern` | Trip count & avg fare by day of week |
| `GET /api/insights/fare_distribution` | Fare distribution buckets |
| `GET /api/insights/payment_types` | Payment method breakdown |

---

## Tasks

### 1. Set Up Frontend Project
```
frontend/
├── index.html      ← Main dashboard page
├── css/
│   └── style.css   ← Styles
├── js/
│   ├── app.js      ← Main app logic
│   ├── api.js      ← API calls
│   └── charts.js   ← Chart rendering
└── assets/         ← Images, icons
```

### 2. Build the Dashboard Layout
- **Header**: Title ("NYC Taxi Trip Analyzer"), team info
- **KPI Cards Row**: Total trips, avg fare, avg distance, avg duration (from `/api/stats/summary`)
- **Charts Section**:
  - Bar chart: Hourly trip volume (from `/api/insights/hourly_pattern`)
  - Bar chart: Borough comparison (from `/api/insights/borough_stats`)
  - Pie chart: Payment types (from `/api/insights/payment_types`)
  - Bar chart: Top 10 pickup locations (from `/api/insights/top_locations`)
  - Line chart: Day-of-week pattern (from `/api/insights/daily_pattern`)
  - Bar chart: Fare distribution (from `/api/insights/fare_distribution`)
- **Data Table**: Paginated trip records (from `/api/trips`)
- **Footer**: Attribution, data source info

### 3. Implement API Integration
```javascript
// Example: Fetch summary stats
const BASE_URL = 'http://localhost:5000/api';

async function fetchSummary() {
    const res = await fetch(`${BASE_URL}/stats/summary`);
    const data = await res.json();
    // Update KPI cards with data
}

async function fetchHourlyPattern() {
    const res = await fetch(`${BASE_URL}/insights/hourly_pattern`);
    const data = await res.json();
    // Render chart with data
}
```

### 4. Add Charts (use Chart.js)
Include via CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### 5. Add Filtering & Sorting
- Borough filter dropdown on the data table
- Sort by fare, distance, duration
- Date range filter (if supported by API)

### 6. Make it Responsive
- Mobile-friendly layout (CSS Grid / Flexbox)
- Charts resize on smaller screens

### 7. Style & Polish
- Use a modern color scheme (dark mode recommended)
- Add loading spinners while data fetches
- Error handling for failed API calls

---

## Suggested Libraries
| Library | Purpose | CDN |
|---------|---------|-----|
| Chart.js | Charts | `cdn.jsdelivr.net/npm/chart.js` |
| Bootstrap 5 | Layout/grid | `cdn.jsdelivr.net/npm/bootstrap@5` |
| Font Awesome | Icons | `cdnjs.cloudflare.com/ajax/libs/font-awesome/6` |

---

## Testing Checklist
- [ ] All KPI cards show real numbers
- [ ] All 6 charts render with data
- [ ] Data table loads and paginates
- [ ] Page is responsive on mobile
- [ ] No console errors
- [ ] Loading states work
