from pathlib import Path
import re, sys

root = Path(sys.argv[1]).resolve()
patterns = [
    r'show.?grid', r'partial.?grid', r'grid.?button', r'CONFIG.*GRID', r'TR_.*GRID',
    r'roadblock', r'BUILDING_ROADBLOCK', r'ROADBLOCK',
    r'construction.?range', r'building.?range', r'show.?range', r'walker.?range',
    r'service.?range', r'labor.?range', r'worker.?range', r'influence', r'preview.?range',
    r'BUILDING_GRANARY', r'BUILDING_WAREHOUSE', r'TERRAIN_ROAD',
]
rx = re.compile('|'.join(f'(?:{p})' for p in patterns), re.I)

for p in sorted(root.joinpath('src').rglob('*')):
    if not p.is_file() or p.suffix.lower() not in {'.c','.h','.cpp','.hpp','.json','.txt'}:
        continue
    try:
        lines = p.read_text(encoding='utf-8', errors='replace').splitlines()
    except Exception:
        continue
    hits = [i for i,line in enumerate(lines) if rx.search(line)]
    if not hits:
        continue
    print('\n' + '='*100)
    print(p.relative_to(root))
    printed=set()
    for i in hits:
        lo=max(0,i-4); hi=min(len(lines),i+5)
        if any(j in printed for j in range(lo,hi)):
            continue
        for j in range(lo,hi):
            print(f'{j+1:5}: {lines[j]}')
            printed.add(j)
        print('-'*80)
