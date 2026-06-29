from scripts.date_utils import parse_date

tests = ['3 цаг', '1 цаг', '2 өдөр', '6 өдөр', '2026.06.19', '2026.06.29', 'Өчигдөр']
for t in tests:
    dt = parse_date(t)
    result = str(dt) if dt else 'NONE (not parsed)'
    print(f'{t:20s} -> {result}')
