from pathlib import Path
import re, sys

if len(sys.argv) != 2:
    raise SystemExit('Usage: python apply_grid_topmenu_clean.py <patched-julius-source-dir>')
root = Path(sys.argv[1]).resolve()

def read(rel):
    return (root / rel).read_text(encoding='utf-8')

def write(rel, text):
    (root / rel).write_text(text, encoding='utf-8', newline='\n')

def rep(rel, old, new, count=1):
    s = read(rel)
    found = s.count(old)
    if found < count:
        raise RuntimeError(f'{rel}: expected anchor at least {count}x, found {found}: {old[:180]!r}')
    write(rel, s.replace(old, new, count))

# Keep the exact Augustus Grid_Full shape from the known-good patch,
# recolor only the grid to a visible dark-chocolate tone and strengthen alpha.
# Roadblock pixels are deliberately untouched.
rel = 'src/graphics/augustus_qol_assets.c'
s = read(rel)
marker = 'static const uint32_t ROADBLOCK_PIXELS'
if marker not in s:
    raise RuntimeError('ROADBLOCK_PIXELS marker not found')
grid_part, rest = s.split(marker, 1)
pixel_re = re.compile(r'0x([0-9a-fA-F]{2})([0-9a-fA-F]{6})u')
changed = 0

def recolor(m):
    global changed
    a = int(m.group(1), 16)
    if a == 0:
        return m.group(0)
    a2 = min(255, (a * 7 + 2) // 4)
    changed += 1
    return f'0x{a2:02x}5a2d18u'  # dark chocolate #5A2D18

grid_part2 = pixel_re.sub(recolor, grid_part)
if changed == 0:
    raise RuntimeError('No non-transparent Grid_Full pixels were recolored')
write(rel, grid_part2 + marker + rest)

# Roamer preview stays in the normal config window. Grid does not: it belongs
# to the in-game top Options menu per user request.
rep('src/window/config.c', '#define MAX_WIDGETS 28', '#define MAX_WIDGETS 27')
rep(
    'src/window/config.c',
    '    {TYPE_CHECKBOX, CONFIG_UI_SHOW_CONSTRUCTION_SIZE, TR_CONFIG_SHOW_CONSTRUCTION_SIZE},\n'
    '    {TYPE_CHECKBOX, CONFIG_UI_SHOW_GRID, TR_CONFIG_SHOW_GRID},\n'
    '    {TYPE_CHECKBOX, CONFIG_UI_SHOW_ROAMING_PATH, TR_CONFIG_SHOW_ROAMING_PATH},',
    '    {TYPE_CHECKBOX, CONFIG_UI_SHOW_CONSTRUCTION_SIZE, TR_CONFIG_SHOW_CONSTRUCTION_SIZE},\n'
    '    {TYPE_CHECKBOX, CONFIG_UI_SHOW_ROAMING_PATH, TR_CONFIG_SHOW_ROAMING_PATH},'
)

# In-game top menu. Use Julius' native c3.eng menu-text mechanism instead of
# modifying the generic menu renderer. Group 19 items 64/65 are supplied in the
# patched c3.eng that ships with the final package.
rep('src/widget/top_menu.c', '#include "city/population.h"\n', '#include "city/population.h"\n#include "core/config.h"\n')
rep('src/widget/top_menu.c', 'static void menu_options_autosave(int param);',
    'static void menu_options_autosave(int param);\nstatic void menu_options_grid(int param);')
rep(
    'src/widget/top_menu.c',
    'static menu_item menu_options[] = {\n'
    '    {2, 1, menu_options_display, 0},\n'
    '    {2, 2, menu_options_sound, 0},\n'
    '    {2, 3, menu_options_speed, 0},\n'
    '    {2, 6, menu_options_difficulty, 0},\n'
    '    {19, 51, menu_options_autosave, 0},\n'
    '};',
    'static menu_item menu_options[] = {\n'
    '    {2, 1, menu_options_display, 0},\n'
    '    {2, 2, menu_options_sound, 0},\n'
    '    {2, 3, menu_options_speed, 0},\n'
    '    {2, 6, menu_options_difficulty, 0},\n'
    '    {19, 51, menu_options_autosave, 0},\n'
    '    {19, 64, menu_options_grid, 0},\n'
    '};'
)
rep('src/widget/top_menu.c', '    {2, menu_options, 5},', '    {2, menu_options, 6},')
rep(
    'src/widget/top_menu.c',
    'static void set_text_for_autosave(void)\n'
    '{\n'
    '    menu_update_text(&menu[INDEX_OPTIONS], 4, setting_monthly_autosave() ? 51 : 52);\n'
    '}',
    'static void set_text_for_autosave(void)\n'
    '{\n'
    '    menu_update_text(&menu[INDEX_OPTIONS], 4, setting_monthly_autosave() ? 51 : 52);\n'
    '}\n\n'
    'static void set_text_for_grid(void)\n'
    '{\n'
    '    menu_update_text(&menu[INDEX_OPTIONS], 5, config_get(CONFIG_UI_SHOW_GRID) ? 65 : 64);\n'
    '}'
)
rep('src/widget/top_menu.c',
    '    set_text_for_autosave();\n    set_text_for_tooltips();',
    '    set_text_for_autosave();\n    set_text_for_grid();\n    set_text_for_tooltips();')
rep(
    'src/widget/top_menu.c',
    'static void menu_options_autosave(int param)\n'
    '{\n'
    '    setting_toggle_monthly_autosave();\n'
    '    set_text_for_autosave();\n'
    '}',
    'static void menu_options_autosave(int param)\n'
    '{\n'
    '    setting_toggle_monthly_autosave();\n'
    '    set_text_for_autosave();\n'
    '}\n\n'
    'static void menu_options_grid(int param)\n'
    '{\n'
    '    config_set(CONFIG_UI_SHOW_GRID, !config_get(CONFIG_UI_SHOW_GRID));\n'
    '    config_save();\n'
    '    set_text_for_grid();\n'
    '    window_request_refresh();\n'
    '}'
)

# Fail hard if any of the old incorrect market-radius experiment leaked in.
for needle in ('CONFIG_UI_SHOW_MARKET_RANGE', 'MARKET_MAX_DISTANCE', 'draw_market_range'):
    hits = []
    for p in (root / 'src').rglob('*'):
        if p.is_file() and p.suffix in ('.c', '.h'):
            try:
                txt = p.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            if needle in txt:
                hits.append(str(p.relative_to(root)))
    if hits:
        raise RuntimeError(f'Forbidden legacy market-range code found: {needle}: {hits}')

# Confirm the known-good roaming preview plumbing is still present.
required = {
    'src/figure/roamer_preview.c': ['BUILDING_DOCTOR', 'CONFIG_UI_SHOW_ROAMING_PATH', 'TOTAL_ROAMERS 4'],
    'src/widget/city_building_ghost.c': ['figure_roamer_preview_create'],
    'src/widget/city_without_overlay.c': ['draw_roamer_frequency', 'figure_roamer_preview_get_frequency'],
    'src/widget/top_menu.c': ['{19, 64, menu_options_grid, 0}', 'config_set(CONFIG_UI_SHOW_GRID'],
}
for rel, needles in required.items():
    txt = read(rel)
    for needle in needles:
        if needle not in txt:
            raise RuntimeError(f'{rel}: required clean-patch marker missing: {needle}')

print(f'Clean grid/top-menu overlay applied; recolored {changed} Grid_Full pixels')
