# Phase 5: Data Quality & Manual Corrections Validation

## Complete Plan

**Status**: Ready for Preparation & Execution
**Date**: 2026-01-24
**Objective**: Verify data quality system works correctly and manual corrections are properly logged
**Duration**: ~1.5 hours
**Prerequisites**: Phase 4 must pass first

---

## Phase 5 Overview

Phase 5 validates that the data quality system functions correctly, including data quality scoring, stale data detection, manual corrections with audit trails, and verification workflows.

### What Gets Tested
1. **Data Quality Scores** - Quality metrics for all competitor data
2. **Stale Data Detection** - Identifies fields needing refresh
3. **Manual Corrections** - User corrections with reason logging
4. **Verification Workflow** - Tracks last verification timestamp
5. **Audit Trails** - Complete change history with attribution
6. **Source Attribution** - Data sources properly documented

### Why It Matters
Data quality is critical for:
- Trust in competitive intelligence
- Identifying when data needs refresh
- Audit compliance and user accountability
- Decision-making confidence
- SLA compliance for data freshness

---

## Test Cases: Phase 5

### Test 5.1: Data Quality Scores
**Endpoint**: `GET /api/data-quality/scores`

**What It Tests**:
- Can retrieve quality metrics for all competitors
- Quality scores are calculated correctly
- Freshness is tracked
- Completeness percentages accurate

**Expected Behavior**:
1. Request returns quality metrics for all competitors
2. Each metric includes:
   - Overall quality score (0-100)
   - Freshness score (days since update)
   - Completeness percentage
   - Last updated timestamp
3. Scores are reasonable (not all 100% or 0%)

**Success Criteria**:
- ✅ Endpoint returns data without error
- ✅ All competitors included
- ✅ Scores between 0-100
- ✅ Freshness timestamps valid
- ✅ Completeness percentages reasonable

**Test Commands**:
```bash
# Get quality scores
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/scores \
  | python3 -m json.tool | head -50

# Count competitors with scores
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/scores \
  | grep -o '"id"' | wc -l
# Should match competitor count from Phase 3
```

---

### Test 5.2: Stale Data Detection
**Endpoint**: `GET /api/data-quality/stale`

**What It Tests**:
- System identifies fields that need refresh
- Stale detection threshold works correctly
- Returns list of fields requiring update

**Expected Behavior**:
1. Request returns stale fields across all competitors
2. Response includes:
   - Competitor ID
   - Field name
   - Days since last update
   - Current quality score
3. Fields are sorted by staleness

**Success Criteria**:
- ✅ Endpoint returns data without error
- ✅ Stale fields identified
- ✅ Days-since-update accurate
- ✅ Reasonable threshold applied
- ✅ Most stale fields listed first

**Test Commands**:
```bash
# Get stale data report
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/stale \
  | python3 -m json.tool | head -100

# Count stale fields
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/stale \
  | grep -o '"field_name"' | wc -l
```

---

### Test 5.3: Manual Corrections - Create
**Endpoint**: `POST /api/competitors/{id}/correct`

**What It Tests**:
- Can submit manual data correction
- Correction is saved to database
- Reason is recorded
- User is attributed

**Expected Behavior**:
1. Request submits correction with:
   - Competitor ID
   - Field name
   - New value
   - Reason for correction
2. System responds with:
   - Confirmation message
   - Timestamp of correction
   - User attribution

**Success Criteria**:
- ✅ Correction accepted without error
- ✅ Response confirms receipt
- ✅ Timestamp provided
- ✅ Field is updated
- ✅ Reason is logged

**Test Commands**:
```bash
# Submit correction
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "employee_count",
    "new_value": "2500",
    "reason": "Updated from latest news article"
  }' \
  http://localhost:8000/api/competitors/1/correct

# Response should confirm:
# {"status": "success", "message": "Correction recorded", "timestamp": "..."}
```

---

### Test 5.4: Audit Trail - Verify Changes
**Endpoint**: `GET /api/data-quality/audit/{competitor_id}`

**What It Tests**:
- Change history is recorded
- User attribution works
- Timestamps are accurate
- Reasons are documented

**Expected Behavior**:
1. Request returns change history for competitor
2. Each change includes:
   - Field name
   - Old value
   - New value
   - User who made change
   - Timestamp
   - Reason (if manual correction)
3. Changes sorted by recency

**Success Criteria**:
- ✅ Audit trail exists for competitor
- ✅ Manual corrections appear
- ✅ User attribution correct
- ✅ Timestamps valid
- ✅ Values and reasons present

**Test Commands**:
```bash
# Get audit trail
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/audit/1 \
  | python3 -m json.tool | head -100

# Filter for manual corrections
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/audit/1 \
  | grep -A 5 "manual"
```

---

### Test 5.5: Verification Workflow
**Endpoint**: `POST /api/data-quality/verify/{competitor_id}`

**What It Tests**:
- Can mark competitor as verified
- Verification timestamp recorded
- Quality score reflects verification

**Expected Behavior**:
1. Request marks competitor as verified
2. System records:
   - Verification timestamp
   - User who verified
   - Updated quality score
3. Dashboard reflects verified status

**Success Criteria**:
- ✅ Verification accepted
- ✅ Timestamp recorded
- ✅ Quality score updated
- ✅ Status changed to "verified"
- ✅ Appears in verification list

**Test Commands**:
```bash
# Verify competitor data
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/verify/1

# Check verification status
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/scores \
  | grep -A 10 '"id": 1'
# Should show recent verification timestamp
```

---

### Test 5.6: Source Attribution
**Endpoint**: `GET /api/data-quality/sources/{competitor_id}`

**What It Tests**:
- Data sources are tracked for each field
- Source attribution is accurate
- Source freshness tracked

**Expected Behavior**:
1. Request returns source info for all fields
2. For each field:
   - Field name
   - Current value
   - Source (scraper, manual, fallback)
   - Last updated from source
   - Confidence score
3. Shows data provenance

**Success Criteria**:
- ✅ All fields have sources
- ✅ Sources are appropriate
- ✅ Timestamps are valid
- ✅ Confidence scores present
- ✅ Manual corrections marked

**Test Commands**:
```bash
# Get source attribution
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/sources/1 \
  | python3 -m json.tool | head -50

# Count different sources
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/sources/1 \
  | grep -o '"source":' | wc -l
```

---

### Test 5.7: Data Completeness Check
**Endpoint**: `GET /api/competitors/{id}` with completeness analysis

**What It Tests**:
- All required fields present
- Optional fields have reasonable coverage
- No critical gaps

**Expected Behavior**:
1. Retrieve full competitor record
2. Check completeness:
   - 100% required fields present
   - 80%+ optional fields present
   - No null/empty critical fields
3. Calculate completeness percentage

**Success Criteria**:
- ✅ All required fields present
- ✅ High optional field coverage
- ✅ No critical gaps
- ✅ Overall completeness > 90%

**Test Commands**:
```bash
# Get competitor details
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/competitors/1 \
  | python3 -m json.tool > competitor.json

# Count fields
grep -c '":' competitor.json

# Check for nulls
grep -c 'null' competitor.json
# Should be minimal

# Check completeness score
grep 'completeness\|quality' competitor.json
```

---

### Test 5.8: Quality Score Calculation Verification
**Method**: Cross-check quality score calculations

**What It Tests**:
- Quality scores calculated correctly
- Formula is consistent
- Edge cases handled properly

**Expected Behavior**:
1. Quality score = (Freshness + Completeness) / 2
2. Freshness decreases over time (0-30 days = high, 30+ days = low)
3. Completeness = fields_populated / total_fields
4. Final score: 0-100

**Success Criteria**:
- ✅ Score calculation correct
- ✅ Formula consistent across records
- ✅ Scores reflect actual data state
- ✅ Edge cases handled (new data, missing data)

**Test Commands**:
```bash
# Manual calculation example
# If competitor has:
# - 45/50 fields populated (90% complete)
# - Last updated 15 days ago (75% fresh)
# Quality = (75 + 90) / 2 = 82.5

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/scores \
  | python3 << 'EOF'
import json, sys
data = json.load(sys.stdin)
for comp in data[:3]:
    print(f"ID: {comp['id']}")
    print(f"  Quality: {comp['quality_score']}")
    print(f"  Freshness: {comp['freshness_score']}")
    print(f"  Completeness: {comp['completeness_score']}")
EOF
```

---

## Phase 5 Test Execution Plan

### Prerequisites
- ✅ Phase 4 tests pass
- ✅ Backend running
- ✅ Database with competitor data
- ✅ Valid authentication token

### Step 1: Authenticate and Get Token
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "username=admin@certifyhealth.com&password=certifyintel2024&grant_type=password" \
  | grep -o '"access_token":\"[^\"]*' | cut -d'\"' -f4)

echo $TOKEN
```

### Step 2: Test Data Quality Scores
```bash
echo "Testing data quality scores..."
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/scores \
  | python3 -m json.tool > scores.json

# Verify structure
python3 << 'EOF'
import json
with open('scores.json') as f:
    data = json.load(f)
    print(f"Total competitors: {len(data)}")
    print(f"Sample scores:")
    for comp in data[:3]:
        print(f"  {comp['name']}: Quality={comp['quality_score']}, Freshness={comp['freshness_score']}")
EOF
```

### Step 3: Test Stale Data Detection
```bash
echo "Testing stale data detection..."
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/stale \
  | python3 -m json.tool > stale.json

# Count stale fields
python3 << 'EOF'
import json
with open('stale.json') as f:
    data = json.load(f)
    print(f"Stale fields detected: {len(data)}")
    print(f"Most stale field: {data[0]['field_name']} ({data[0]['days_since_update']} days)")
EOF
```

### Step 4: Test Manual Corrections
```bash
echo "Testing manual corrections..."

# Make a correction
RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "employee_count",
    "new_value": "2500",
    "reason": "Updated from Glassdoor latest report"
  }' \
  http://localhost:8000/api/competitors/1/correct)

echo "Correction response:"
echo $RESPONSE | python3 -m json.tool

# Verify it was recorded
sleep 1
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/audit/1 \
  | python3 -m json.tool | grep -A 5 "employee_count"
```

### Step 5: Test Verification Workflow
```bash
echo "Testing verification workflow..."

# Mark competitor as verified
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/verify/1 \
  | python3 -m json.tool

# Check updated quality score
sleep 1
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/scores \
  | python3 -m json.tool | grep -A 5 '"id": 1'
```

### Step 6: Test Source Attribution
```bash
echo "Testing source attribution..."
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/sources/1 \
  | python3 -m json.tool | head -100

# Count sources
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/sources/1 \
  | python3 << 'EOF'
import json, sys
data = json.load(sys.stdin)
sources = {}
for field in data:
    source = field.get('source', 'unknown')
    sources[source] = sources.get(source, 0) + 1
print("Source breakdown:")
for source, count in sorted(sources.items(), key=lambda x: -x[1]):
    print(f"  {source}: {count} fields")
EOF
```

### Step 7: Verify Data Completeness
```bash
echo "Testing data completeness..."
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/competitors/1 \
  | python3 << 'EOF'
import json, sys
data = json.load(sys.stdin)
total = len(data)
filled = sum(1 for v in data.values() if v is not None and v != "")
empty = total - filled
percentage = (filled / total * 100) if total > 0 else 0
print(f"Completeness Analysis:")
print(f"  Total fields: {total}")
print(f"  Filled fields: {filled}")
print(f"  Empty fields: {empty}")
print(f"  Completeness: {percentage:.1f}%")
EOF
```

---

## Expected Phase 5 Results

### Data Quality Scores
```
Endpoint: /api/data-quality/scores
✅ All competitors included (30+)
✅ Scores calculated (0-100 range)
✅ Freshness tracked (days since update)
✅ Completeness percentages (40-100%)
✅ Status: PASS
```

### Stale Data Detection
```
Endpoint: /api/data-quality/stale
✅ Stale fields identified
✅ Days-since-update accurate
✅ Sorted by staleness
✅ Appropriate threshold applied
✅ Status: PASS
```

### Manual Corrections
```
Endpoint: /api/competitors/{id}/correct
✅ Correction saved
✅ Reason logged
✅ Timestamp recorded
✅ User attributed
✅ Audit trail updated
✅ Status: PASS
```

### Audit Trail
```
Endpoint: /api/data-quality/audit/{id}
✅ All changes recorded
✅ User attribution present
✅ Timestamps valid
✅ Reasons documented
✅ Complete history available
✅ Status: PASS
```

### Verification Workflow
```
Endpoint: /api/data-quality/verify/{id}
✅ Verification recorded
✅ Timestamp updated
✅ Quality score affected
✅ Status marked
✅ Status: PASS
```

### Source Attribution
```
Endpoint: /api/data-quality/sources/{id}
✅ All fields have sources
✅ Source accuracy high
✅ Timestamps valid
✅ Confidence scores present
✅ Status: PASS
```

### Data Completeness
```
Overall Results:
✅ Required fields: 100% present
✅ Optional fields: 80%+ present
✅ Critical gaps: None
✅ Overall completeness: 90%+
✅ Status: PASS
```

---

## Phase 5 Troubleshooting

### Issue: Quality Score Endpoint Returns Empty
**Symptom**: "[]" or no data returned
**Cause**: No competitors in database or endpoint not implemented
**Fix**:
```bash
# Verify competitors exist
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/competitors | grep -o '"id"' | wc -l

# Check if endpoint exists (may be implemented as /api/competitors with filtering)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/competitors/1 | grep quality
```

### Issue: Stale Data Detection Inaccurate
**Symptom**: "All fields show same freshness" or "No stale fields detected"
**Cause**: Data recently updated or calculation error
**Fix**:
```bash
# Check last update timestamps
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/competitors/1 \
  | grep -i "updated\|timestamp"

# Manual verification of freshness calculation
# Days = current_date - last_update_date
```

### Issue: Manual Corrections Not Appearing in Audit
**Symptom**: "Correction submitted but not in history"
**Cause**: Database transaction not committed or endpoint error
**Fix**:
```bash
# Check backend logs for errors
# Verify database permissions
# Retry correction with same data

# Debug: Check if correction endpoint exists
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/competitors/1/correct \
  -d '{"field_name":"test","new_value":"test","reason":"test"}' -v
```

### Issue: Verification Workflow Not Working
**Symptom**: "Verification endpoint not found" or "No change in quality score"
**Cause**: Endpoint not implemented or score calculation doesn't use verification
**Fix**:
```bash
# Check if endpoint exists
curl -X OPTIONS -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/verify/1

# May need to use alternative endpoint
# Check main.py for actual endpoint names
```

### Issue: Source Attribution Missing
**Symptom**: "Endpoint not found" or "Empty sources list"
**Cause**: Feature not fully implemented or different endpoint name
**Fix**:
```bash
# Check for data_sources table
grep -r "data_sources" backend/

# May be implemented as field metadata
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/competitors/1 \
  | grep -i "source"
```

---

## Phase 5 Success Criteria

### Minimum Success (MVP)
```
✅ Data quality scores retrieve without error
✅ Stale data detection identifies fields
✅ Manual corrections can be submitted
✅ Audit trail exists and logs changes
✅ Data completeness measurable
```

### Expected Success (Full Features)
```
✅ All quality endpoints working
✅ Scores reflect actual data state
✅ Verification workflow functional
✅ Source attribution accurate
✅ Complete audit trails
✅ Manual corrections with reasons logged
```

### Excellent Success
```
✅ All tests above
✅ Quality scores in real-time
✅ Stale detection proactive and accurate
✅ Verification affects quality score
✅ Full source provenance tracked
✅ Audit trail queryable and detailed
✅ Completeness scores 90%+ across system
```

---

## Phase 5 Test Documentation

After testing, create `PHASE_5_RESULTS.md`:

```markdown
# Phase 5: Data Quality Testing Results

**Date**: [date tested]
**Duration**: [time spent]
**Status**: PASS / PARTIAL / FAIL

## Test Results Summary

### Data Quality Scores
- Endpoint works: ✅ / ⚠️ / ❌
- Scores calculated: ✅ / ⚠️ / ❌
- Freshness tracked: ✅ / ⚠️ / ❌
- Completeness accurate: ✅ / ⚠️ / ❌
- Status: PASS / WARN / FAIL

### Stale Data Detection
- Endpoint works: ✅ / ⚠️ / ❌
- Fields identified: ✅ / ⚠️ / ❌
- Days-since-update correct: ✅ / ⚠️ / ❌
- Sorted properly: ✅ / ⚠️ / ❌
- Status: PASS / WARN / FAIL

### Manual Corrections
- Endpoint works: ✅ / ⚠️ / ❌
- Corrections saved: ✅ / ⚠️ / ❌
- Reason logged: ✅ / ⚠️ / ❌
- Timestamp recorded: ✅ / ⚠️ / ❌
- Status: PASS / WARN / FAIL

### Audit Trail
- Endpoint works: ✅ / ⚠️ / ❌
- All changes recorded: ✅ / ⚠️ / ❌
- User attribution: ✅ / ⚠️ / ❌
- Timestamps valid: ✅ / ⚠️ / ❌
- Status: PASS / WARN / FAIL

### Verification Workflow
- Endpoint works: ✅ / ⚠️ / ❌
- Verification recorded: ✅ / ⚠️ / ❌
- Quality score updated: ✅ / ⚠️ / ❌
- Status: PASS / WARN / FAIL

### Source Attribution
- Endpoint works: ✅ / ⚠️ / ❌
- Sources tracked: ✅ / ⚠️ / ❌
- Accuracy verified: ✅ / ⚠️ / ❌
- Status: PASS / WARN / FAIL

## Issues Found
[List any failures or warnings]

## Recommendations
[Next steps if any issues found]

## Ready for Production?
✅ YES - All data quality systems working
⚠️ PARTIAL - Some warnings, documented
❌ NO - Issues must be fixed first

## Summary
[Overall assessment of data quality system readiness]
```

---

## Quick Reference: Phase 5 Commands

```bash
# Authenticate
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "username=admin@certifyhealth.com&password=certifyintel2024&grant_type=password" \
  | jq -r .access_token)

# Get quality scores
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/scores | jq .

# Get stale data
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/stale | jq .

# Submit correction
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"field_name":"field","new_value":"value","reason":"reason"}' \
  http://localhost:8000/api/competitors/1/correct | jq .

# Get audit trail
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/audit/1 | jq .

# Verify competitor
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/verify/1 | jq .

# Get source attribution
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/sources/1 | jq .
```

---

## Phase 5 Timeline

| Task | Duration | Cumulative |
|------|----------|-----------|
| Setup auth token | 30 sec | 30 sec |
| Test quality scores | 2 min | 2.5 min |
| Test stale detection | 2 min | 4.5 min |
| Test manual corrections | 3 min | 7.5 min |
| Test audit trail | 2 min | 9.5 min |
| Test verification | 2 min | 11.5 min |
| Test source attribution | 2 min | 13.5 min |
| Test data completeness | 2 min | 15.5 min |
| Document results | 5 min | 20.5 min |
| **TOTAL** | | **~21 minutes** |

---

## Next Steps After Phase 5

### If Phase 5 Passes
```
✅ All data quality systems working
✅ Audit trails complete
✅ Manual corrections functional
✅ Ready for production deployment
→ System fully validated
→ Ready for user training
→ Deploy to production
```

### If Phase 5 Has Warnings
```
⚠️ Most data quality features work
⚠️ But some features incomplete
→ Document warnings
→ Proceed with caution
→ Monitor in production
→ Fix issues in Phase 6
```

### If Phase 5 Fails
```
❌ Critical data quality features broken
→ Fix identified issues
→ Retry Phase 5
→ Cannot deploy until fixed
```

---

## Phase 5 Completion Criteria

Phase 5 is complete when:
```
✅ All 8 test cases executed
✅ Summary shows: Passed ≥ 6/8, Failed = 0
✅ Results documented in PHASE_5_RESULTS.md
✅ All critical features working
✅ Data quality system production-ready
```

---

## Summary

Phase 5 validates that:
- ✅ Data quality is measurable and tracked
- ✅ Stale data can be identified
- ✅ Manual corrections are logged with audit trail
- ✅ Verification workflow is functional
- ✅ Source attribution is maintained
- ✅ System is ready for production

**Expected Duration**: ~21 minutes
**Expected Success**: 95%+ (quality systems usually work if core system works)

**Next**: Production Deployment & User Training

---

**Phase 5 preparation complete and ready for execution.**
