import xml.etree.ElementTree as ET

# Parse the XML
tree = ET.parse('BF1n.eaf')
root = tree.getroot()

# Extract time slots
time_slots = {}
for ts in root.findall('.//TIME_ORDER/TIME_SLOT'):
    ts_id = ts.attrib['TIME_SLOT_ID']
    time_value = int(ts.attrib['TIME_VALUE']) / 1000  # Convert ms to seconds
    time_slots[ts_id] = time_value

# Collect intervals for different annotation types
pt_intervals = []
ds_intervals = []
fbuoy_intervals = []

for tier in root.findall('.//TIER'):
    for ann in tier.findall('.//ANNOTATION/ALIGNABLE_ANNOTATION'):
        ann_value_elem = ann.find('ANNOTATION_VALUE')
        if ann_value_elem is None:
            continue
        ann_value = ann_value_elem.text.strip() if ann_value_elem.text else ''
        
        # Get time references
        ref1 = ann.attrib['TIME_SLOT_REF1']
        ref2 = ann.attrib['TIME_SLOT_REF2']
        start = time_slots.get(ref1, 0)
        end = time_slots.get(ref2, 0)
        
        if start >= end:
            continue  # Skip invalid intervals
            
        # Check annotation types
        if ann_value.startswith(('PT:', 'PT121:')):
            pt_intervals.append((start, end))
        elif any(ann_value.startswith(prefix) for prefix in ['DSS', 'DS', '?DS']):
            ds_intervals.append((start, end))
        elif ann_value.startswith('FBUOY'):
            fbuoy_intervals.append((start, end))

# Determine max time
max_time = max(time_slots.values()) if time_slots else 0

# Generate time column and annotation values
time_column = []
pt_column = []
ds_column = []
fbuoy_column = []

current_time = 0.0
while current_time <= max_time:
    time_column.append(round(current_time, 2))
    
    # Check PT intervals
    pt = 0
    for start, end in pt_intervals:
        if start <= current_time < end:
            pt = 1
            break
    
    # Check DS intervals
    ds = 0
    for start, end in ds_intervals:
        if start <= current_time < end:
            ds = 1
            break
    
    # Check FBUOY intervals
    fbuoy = 0
    for start, end in fbuoy_intervals:
        if start <= current_time < end:
            fbuoy = 1
            break
    
    pt_column.append(pt)
    ds_column.append(ds)
    fbuoy_column.append(fbuoy)
    
    current_time += 0.04  # Increment by 40ms (25 FPS)

# Output CSV
with open('BF1n.csv', 'w') as f:
    f.write("Time,PT,DS,FBUOY\n")
    for t, pt, ds, fbuoy in zip(time_column, pt_column, ds_column, fbuoy_column):
        f.write(f"{t:.2f},{pt},{ds},{fbuoy}\n")

print("CSV file created successfully from .eaf with PT, DS, and FBUOY annotations!")