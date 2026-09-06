from pathlib import Path
import re, sys

if len(sys.argv) != 2:
    raise SystemExit('Usage: python grid_topmenu_overlay.py <patched-julius-source-dir>')
root = Path(sys.argv[1]).resolve()

def read(rel):
    return (root / rel).read_text(encoding='utf-8')

def write(rel, text):
    (root / rel).write_text(text, encoding='utf-8', newline='\n')

def rep(rel, old, new, count=1):
    s = read(rel)
    if s.count(old) < count:
        raise RuntimeError(f'{rel}: anchor not found: {old[:160]!r}')
    write(rel, s.replace(old, new, count))

# 1) Augustus draws Grid_Full with COLOR_GRID 0xff180800. The embedded sprite
# currently contains white RGB + source alpha, so recolor only the grid array.
rel = 'src/graphics/augustus_qol_assets.c'
s = read(rel)
head, tail = s.split('static const uint32_t ROADBLOCK_PIXELS', 1)
head2 = re.sub(r'0x([0-9a-fA-F]{2})ffffffu', lambda m: f'0x{m.group(1)}180800u', head)
if head2 == head:
    raise RuntimeError('grid pixel recolor matched nothing')
write(rel, head2 + 'static const uint32_t ROADBLOCK_PIXELS' + tail)

# 2) Two compiled strings for the in-game Options dropdown state.
rep('src/translation/translation.h',
    '    TR_CONFIG_SHOW_GRID,\n    TR_CONFIG_SHOW_ROAMING_PATH,\n    TR_BUILDING_ROADBLOCK_NAME,',
    '    TR_CONFIG_SHOW_GRID,\n    TR_CONFIG_SHOW_ROAMING_PATH,\n'
    '    TR_TOP_MENU_GRID_ENABLE,\n    TR_TOP_MENU_GRID_DISABLE,\n'
    '    TR_BUILDING_ROADBLOCK_NAME,')
rep('src/translation/english.c',
    '    {TR_CONFIG_SHOW_ROAMING_PATH, "Show worker roaming range while placing buildings"},',
    '    {TR_CONFIG_SHOW_ROAMING_PATH, "Show worker roaming range while placing buildings"},\n'
    '    {TR_TOP_MENU_GRID_ENABLE, "Grid: Off (click to enable)"},\n'
    '    {TR_TOP_MENU_GRID_DISABLE, "Grid: On (click to disable)"},')
rep('src/translation/korean.c',
    '    {TR_CONFIG_SHOW_ROAMING_PATH, "건물 작업자 이동범위 표시"},',
    '    {TR_CONFIG_SHOW_ROAMING_PATH, "건물 작업자 이동범위 표시"},\n'
    '    {TR_TOP_MENU_GRID_ENABLE, "격자 표시: 꺼짐 (클릭하여 켜기)"},\n'
    '    {TR_TOP_MENU_GRID_DISABLE, "격자 표시: 켜짐 (클릭하여 끄기)"},')

# 3) Grid is no longer a main-menu configuration checkbox. Roamer preview stays there.
rep('src/window/config.c', '#define MAX_WIDGETS 28', '#define MAX_WIDGETS 27')
rep('src/window/config.c',
    '    {TYPE_CHECKBOX, CONFIG_UI_SHOW_CONSTRUCTION_SIZE, TR_CONFIG_SHOW_CONSTRUCTION_SIZE},\n'
    '    {TYPE_CHECKBOX, CONFIG_UI_SHOW_GRID, TR_CONFIG_SHOW_GRID},\n'
    '    {TYPE_CHECKBOX, CONFIG_UI_SHOW_ROAMING_PATH, TR_CONFIG_SHOW_ROAMING_PATH},',
    '    {TYPE_CHECKBOX, CONFIG_UI_SHOW_CONSTRUCTION_SIZE, TR_CONFIG_SHOW_CONSTRUCTION_SIZE},\n'
    '    {TYPE_CHECKBOX, CONFIG_UI_SHOW_ROAMING_PATH, TR_CONFIG_SHOW_ROAMING_PATH},')

# 4) Existing Julius menu items are c3.eng group/item pairs. Add a sentinel text_group=-1
# so one menu entry can use the compiled translation table and remain EXE-only.
rep('src/graphics/menu.c', '#include "graphics/panel.h"\n',
    '#include "graphics/panel.h"\n#include "graphics/text.h"\n#include "translation/translation.h"\n')
rep('src/graphics/menu.c',
    '        int width_pixels = lang_text_get_width(\n'
    '            sub->text_group, sub->text_number, FONT_NORMAL_BLACK);',
    '        int width_pixels = sub->text_group == -1 ?\n'
    '            text_get_width(translation_for((translation_key) sub->text_number), FONT_NORMAL_BLACK) :\n'
    '            lang_text_get_width(sub->text_group, sub->text_number, FONT_NORMAL_BLACK);')
rep('src/graphics/menu.c',
    '            lang_text_draw_colored(sub->text_group, sub->text_number,\n'
    '                menu->x_start + 8, y_offset, FONT_NORMAL_PLAIN, COLOR_FONT_ORANGE);',
    '            if (sub->text_group == -1) {\n'
    '                text_draw(translation_for((translation_key) sub->text_number),\n'
    '                    menu->x_start + 8, y_offset, FONT_NORMAL_PLAIN, COLOR_FONT_ORANGE);\n'
    '            } else {\n'
    '                lang_text_draw_colored(sub->text_group, sub->text_number,\n'
    '                    menu->x_start + 8, y_offset, FONT_NORMAL_PLAIN, COLOR_FONT_ORANGE);\n'
    '            }')
rep('src/graphics/menu.c',
    '            lang_text_draw(sub->text_group, sub->text_number,\n'
    '                menu->x_start + 8, y_offset, FONT_NORMAL_BLACK);',
    '            if (sub->text_group == -1) {\n'
    '                text_draw(translation_for((translation_key) sub->text_number),\n'
    '                    menu->x_start + 8, y_offset, FONT_NORMAL_BLACK, 0);\n'
    '            } else {\n'
    '                lang_text_draw(sub->text_group, sub->text_number,\n'
    '                    menu->x_start + 8, y_offset, FONT_NORMAL_BLACK);\n'
    '            }')
rep('src/graphics/menu.c',
    '        int item_width = lang_text_get_width(\n'
    '            menu->items[index].text_group, text_number, FONT_NORMAL_BLACK);',
    '        int item_width = menu->items[index].text_group == -1 ?\n'
    '            text_get_width(translation_for((translation_key) text_number), FONT_NORMAL_BLACK) :\n'
    '            lang_text_get_width(menu->items[index].text_group, text_number, FONT_NORMAL_BLACK);')

# 5) In-game top menu: Options -> Grid: On/Off.
rep('src/widget/top_menu.c', '#include "city/population.h"\n',
    '#include "city/population.h"\n#include "core/config.h"\n')
rep('src/widget/top_menu.c', '#include "widget/city.h"\n',
    '#include "widget/city.h"\n#include "translation/translation.h"\n')
rep('src/widget/top_menu.c',
    'static void menu_options_autosave(int param);',
    'static void menu_options_autosave(int param);\nstatic void menu_options_grid(int param);')
rep('src/widget/top_menu.c',
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
    '    {-1, TR_TOP_MENU_GRID_ENABLE, menu_options_grid, 0},\n'
    '};')
rep('src/widget/top_menu.c', '    {2, menu_options, 5},', '    {2, menu_options, 6},')
rep('src/widget/top_menu.c',
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
    '    menu_update_text(&menu[INDEX_OPTIONS], 5,\n'
    '        config_get(CONFIG_UI_SHOW_GRID) ? TR_TOP_MENU_GRID_DISABLE : TR_TOP_MENU_GRID_ENABLE);\n'
    '}')
rep('src/widget/top_menu.c',
    '    set_text_for_autosave();\n    set_text_for_tooltips();',
    '    set_text_for_autosave();\n    set_text_for_grid();\n    set_text_for_tooltips();')
rep('src/widget/top_menu.c',
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
    '}')

print('Grid top-menu overlay applied')
