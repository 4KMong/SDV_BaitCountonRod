from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: python apply_qol_patch.py <julius-1.8.0-source-dir>")
root = Path(sys.argv[1]).resolve()
if not (root / "src").is_dir():
    raise SystemExit(f"src directory not found: {root}")

def read(rel): return (root/rel).read_text(encoding="utf-8")
def write(rel,s): (root/rel).write_text(s,encoding="utf-8",newline="\n")
def rep(rel, old, new, count=1):
    s=read(rel)
    if s.count(old) < count:
        raise RuntimeError(f"{rel}: anchor not found: {old[:100]!r}")
    write(rel,s.replace(old,new,count))

rep("src/core/config.h",
"    CONFIG_UI_SHOW_WATER_STRUCTURE_RANGE,\n    CONFIG_UI_SHOW_CONSTRUCTION_SIZE,\n    CONFIG_UI_HIGHLIGHT_LEGIONS,",
"    CONFIG_UI_SHOW_WATER_STRUCTURE_RANGE,\n    CONFIG_UI_SHOW_CONSTRUCTION_SIZE,\n    CONFIG_UI_SHOW_GRID,\n    CONFIG_UI_SHOW_PARTIAL_GRID_AROUND_CONSTRUCTION,\n    CONFIG_UI_SHOW_MARKET_RANGE,\n    CONFIG_UI_HIGHLIGHT_LEGIONS,")
rep("src/core/config.c",
'    "ui_show_water_structure_range",\n    "ui_show_construction_size",\n    "ui_highlight_legions",',
'    "ui_show_water_structure_range",\n    "ui_show_construction_size",\n    "ui_show_grid",\n    "ui_show_partial_grid_around_construction",\n    "ui_show_market_range",\n    "ui_highlight_legions",')
rep("src/translation/translation.h",
"    TR_CONFIG_SHOW_WATER_STRUCTURE_RANGE,\n    TR_CONFIG_SHOW_CONSTRUCTION_SIZE,\n    TR_CONFIG_HIGHLIGHT_LEGIONS,",
"    TR_CONFIG_SHOW_WATER_STRUCTURE_RANGE,\n    TR_CONFIG_SHOW_CONSTRUCTION_SIZE,\n    TR_CONFIG_SHOW_GRID,\n    TR_CONFIG_SHOW_PARTIAL_GRID_AROUND_CONSTRUCTION,\n    TR_CONFIG_SHOW_MARKET_RANGE,\n    TR_CONFIG_HIGHLIGHT_LEGIONS,")
rep("src/translation/english.c",
'    {TR_CONFIG_SHOW_CONSTRUCTION_SIZE, "Show draggable construction size"},',
'    {TR_CONFIG_SHOW_CONSTRUCTION_SIZE, "Show draggable construction size"},\n    {TR_CONFIG_SHOW_GRID, "Show construction grid"},\n    {TR_CONFIG_SHOW_PARTIAL_GRID_AROUND_CONSTRUCTION, "Show partial grid around construction"},\n    {TR_CONFIG_SHOW_MARKET_RANGE, "Show market range while building"},')
rep("src/translation/korean.c",
'    {TR_CONFIG_SHOW_CONSTRUCTION_SIZE, "드래그 건설 시 전체 크기 표시"},',
'    {TR_CONFIG_SHOW_CONSTRUCTION_SIZE, "드래그 건설 시 전체 크기 표시"},\n    {TR_CONFIG_SHOW_GRID, "격자 보이기"},\n    {TR_CONFIG_SHOW_PARTIAL_GRID_AROUND_CONSTRUCTION, "건설 주변 부분 격자 표시"},\n    {TR_CONFIG_SHOW_MARKET_RANGE, "시장 건설 시 범위 표시"},')
rep("src/window/config.c", "#define MAX_WIDGETS 26", "#define MAX_WIDGETS 29")
rep("src/window/config.c",
"    {TYPE_CHECKBOX, CONFIG_UI_SHOW_WATER_STRUCTURE_RANGE, TR_CONFIG_SHOW_WATER_STRUCTURE_RANGE},\n    {TYPE_CHECKBOX, CONFIG_UI_SHOW_CONSTRUCTION_SIZE, TR_CONFIG_SHOW_CONSTRUCTION_SIZE},\n    {TYPE_CHECKBOX, CONFIG_UI_HIGHLIGHT_LEGIONS, TR_CONFIG_HIGHLIGHT_LEGIONS},",
"    {TYPE_CHECKBOX, CONFIG_UI_SHOW_WATER_STRUCTURE_RANGE, TR_CONFIG_SHOW_WATER_STRUCTURE_RANGE},\n    {TYPE_CHECKBOX, CONFIG_UI_SHOW_CONSTRUCTION_SIZE, TR_CONFIG_SHOW_CONSTRUCTION_SIZE},\n    {TYPE_CHECKBOX, CONFIG_UI_SHOW_GRID, TR_CONFIG_SHOW_GRID},\n    {TYPE_CHECKBOX, CONFIG_UI_SHOW_PARTIAL_GRID_AROUND_CONSTRUCTION, TR_CONFIG_SHOW_PARTIAL_GRID_AROUND_CONSTRUCTION},\n    {TYPE_CHECKBOX, CONFIG_UI_SHOW_MARKET_RANGE, TR_CONFIG_SHOW_MARKET_RANGE},\n    {TYPE_CHECKBOX, CONFIG_UI_HIGHLIGHT_LEGIONS, TR_CONFIG_HIGHLIGHT_LEGIONS},")

rep("src/widget/city_without_overlay.c", '#include "graphics/image.h"\n', '#include "graphics/graphics.h"\n#include "graphics/image.h"\n')
grid_code = r'''static void blend_grid_pixel(int x, int y)
{
    color_t *pixel = graphics_get_pixel(x, y);
    color_t c = *pixel;
    int r = (c >> 16) & 0xff;
    int g = (c >> 8) & 0xff;
    int b = c & 0xff;
    r = (r * 3 + 96) / 4;
    g = (g * 3 + 96) / 4;
    b = (b * 3 + 96) / 4;
    *pixel = (r << 16) | (g << 8) | b;
}

static void draw_grid_segment(int x, int y, int dx, int dy)
{
    for (int i = 0; i <= 30; i++) {
        blend_grid_pixel(x + dx * i / 30, y + dy * i / 30);
    }
}

static void draw_grid_tile(int x, int y)
{
    const clip_info *clip = graphics_get_clip_info(x, y, 61, 31);
    if (!clip->is_visible || clip->clipped_pixels_left || clip->clipped_pixels_right ||
        clip->clipped_pixels_top || clip->clipped_pixels_bottom) {
        return;
    }
    draw_grid_segment(x + 30, y, 30, 15);
    draw_grid_segment(x + 60, y + 15, -30, 15);
    draw_grid_segment(x + 30, y + 30, -30, -15);
    draw_grid_segment(x, y + 15, 30, -15);
}

'''
rep("src/widget/city_without_overlay.c", "static void draw_footprint(int x, int y, int grid_offset)\n{", grid_code+"static void draw_footprint(int x, int y, int grid_offset)\n{")
rep("src/widget/city_without_overlay.c",
"        image_draw_isometric_footprint_from_draw_tile(image_id, x, y, color_mask);\n    }\n}",
"        image_draw_isometric_footprint_from_draw_tile(image_id, x, y, color_mask);\n        if (!building_id && config_get(CONFIG_UI_SHOW_GRID)) {\n            draw_grid_tile(x, y);\n        }\n    }\n}")

rep("src/widget/city_building_ghost.c", '#include "graphics/image.h"\n', '#include "graphics/graphics.h"\n#include "graphics/image.h"\n')
rep("src/widget/city_building_ghost.c", "#define MAX_TILES 25\n", "#define MAX_TILES 25\n#define MARKET_MAX_DISTANCE 40\n")
ghost_code = r'''static void blend_partial_grid_pixel(int x, int y)
{
    color_t *pixel = graphics_get_pixel(x, y);
    color_t c = *pixel;
    int r = (c >> 16) & 0xff;
    int g = (c >> 8) & 0xff;
    int b = c & 0xff;
    r = (r * 3 + 112) / 4;
    g = (g * 3 + 112) / 4;
    b = (b * 3 + 112) / 4;
    *pixel = (r << 16) | (g << 8) | b;
}

static void draw_partial_grid_segment(int x, int y, int dx, int dy)
{
    for (int i = 0; i <= 30; i++) {
        blend_partial_grid_pixel(x + dx * i / 30, y + dy * i / 30);
    }
}

static void draw_partial_grid_tile(int x, int y, int grid_offset)
{
    const clip_info *clip = graphics_get_clip_info(x, y, 61, 31);
    if (!clip->is_visible || clip->clipped_pixels_left || clip->clipped_pixels_right ||
        clip->clipped_pixels_top || clip->clipped_pixels_bottom) {
        return;
    }
    draw_partial_grid_segment(x + 30, y, 30, 15);
    draw_partial_grid_segment(x + 60, y + 15, -30, 15);
    draw_partial_grid_segment(x + 30, y + 30, -30, -15);
    draw_partial_grid_segment(x, y + 15, 30, -15);
}

static void draw_market_range(int x, int y, int grid_offset)
{
    image_draw_blend_alpha(image_group(GROUP_TERRAIN_FLAT_TILE), x, y, COLOR_MASK_BLUE);
}

'''
rep("src/widget/city_building_ghost.c", "static void draw_flat_tile(int x, int y, color_t color_mask)\n{", ghost_code+"static void draw_flat_tile(int x, int y, color_t color_mask)\n{")
rep("src/widget/city_building_ghost.c",
"    } else if (type == BUILDING_WELL) {\n        if (config_get(CONFIG_UI_SHOW_WATER_STRUCTURE_RANGE)) {\n            city_view_foreach_tile_in_range(grid_offset, 1, 2, draw_fountain_range);\n        }\n        draw_building(image_id, x, y);\n    } else if (type != BUILDING_CLEAR_LAND) {",
"    } else if (type == BUILDING_WELL) {\n        if (config_get(CONFIG_UI_SHOW_WATER_STRUCTURE_RANGE)) {\n            city_view_foreach_tile_in_range(grid_offset, 1, 2, draw_fountain_range);\n        }\n        draw_building(image_id, x, y);\n    } else if (type == BUILDING_MARKET) {\n        if (config_get(CONFIG_UI_SHOW_MARKET_RANGE)) {\n            city_view_foreach_tile_in_range(grid_offset, 2, MARKET_MAX_DISTANCE, draw_market_range);\n        }\n        draw_building(image_id, x, y);\n    } else if (type != BUILDING_CLEAR_LAND) {")
rep("src/widget/city_building_ghost.c",
"    int grid_offset = tile->grid_offset;\n    int fully_blocked = is_fully_blocked(tile->x, tile->y, type, building_size, grid_offset);",
"    int grid_offset = tile->grid_offset;\n    if (config_get(CONFIG_UI_SHOW_PARTIAL_GRID_AROUND_CONSTRUCTION)) {\n        city_view_foreach_tile_in_range(grid_offset, building_size, 2, draw_partial_grid_tile);\n    }\n    int fully_blocked = is_fully_blocked(tile->x, tile->y, type, building_size, grid_offset);")
print("QoL patch applied:", root)

import re
rep('src/building/type.h','    BUILDING_DISTRIBUTION_CENTER_UNUSED = 50,','    BUILDING_ROADBLOCK = 50,')
rep('src/building/menu.c','    {BUILDING_GARDENS, BUILDING_PLAZA, BUILDING_ENGINEERS_POST, BUILDING_LOW_BRIDGE, BUILDING_SHIP_BRIDGE,','    {BUILDING_GARDENS, BUILDING_PLAZA, BUILDING_ROADBLOCK, BUILDING_ENGINEERS_POST, BUILDING_LOW_BRIDGE, BUILDING_SHIP_BRIDGE,')
rep('src/building/menu.c','    enable_if_allowed(enabled, type, BUILDING_DISTRIBUTION_CENTER_UNUSED);','    if (type == BUILDING_ROADBLOCK) {\n        *enabled = 1;\n    }')
rep('src/scenario/building.c','        case BUILDING_DISTRIBUTION_CENTER_UNUSED:\n            return scenario.allowed_buildings[ALLOWED_BUILDING_DISTRIBUTION_CENTER];','        case BUILDING_ROADBLOCK:\n            return 1;')

r='src/building/properties.c'; s=read(r); a=s.index('static building_properties properties[140] = {'); e=s.index('};',a); lines=s[a:e].splitlines(); idx=-1
for i,line in enumerate(lines):
    if re.match(r'^\s*\{\s*\d',line):
        idx+=1
        if idx==50:
            lines[i]='    {1, 1,  24, 0}, // BUILDING_ROADBLOCK'
            break
else: raise RuntimeError('properties initializer #50 not found')
write(r,s[:a]+'\n'.join(lines)+s[e:])

rep('src/building/building.c','    if (b->type == BUILDING_DISTRIBUTION_CENTER_UNUSED) {\n        city_buildings_remove_distribution_center(b);\n    }\n','')
rep('src/building/construction.c','            !(type == BUILDING_DISTRIBUTION_CENTER_UNUSED && city_buildings_has_distribution_center())) {','            1) {')
rep('src/window/build_menu.c','        int cost = model_get_building(type)->cost;','        int cost = type == BUILDING_ROADBLOCK ? 10 : model_get_building(type)->cost;')
rep('src/building/construction.c','    int current_cost = model_get_building(type)->cost;','    int current_cost = type == BUILDING_ROADBLOCK ? 10 : model_get_building(type)->cost;')
rep('src/building/construction.c','    int placement_cost = model_get_building(type)->cost;','    int placement_cost = type == BUILDING_ROADBLOCK ? 10 : model_get_building(type)->cost;')

rep('src/building/construction_building.c','#include "map/building_tiles.h"\n','#include "map/building_tiles.h"\n#include "map/grid.h"\n')
rep('src/building/construction_building.c','        // distribution center (also unused)\n        case BUILDING_DISTRIBUTION_CENTER_UNUSED:\n            city_buildings_add_distribution_center(b);\n            break;','        case BUILDING_ROADBLOCK:\n            map_building_tiles_add(b->id, b->x, b->y, 1,\n                image_group(GROUP_BUILDING_WALL), TERRAIN_BUILDING | TERRAIN_ROAD);\n            map_tiles_update_area_roads(b->x, b->y, 3);\n            break;')
rep('src/building/construction_building.c','    int waterside_orientation_abs = 0, waterside_orientation_rel = 0;\n    if (type == BUILDING_SHIPYARD || type == BUILDING_WHARF) {','    int waterside_orientation_abs = 0, waterside_orientation_rel = 0;\n    if (type == BUILDING_ROADBLOCK) {\n        int road_offset = map_grid_offset(x, y);\n        if (!map_terrain_is(road_offset, TERRAIN_ROAD) ||\n            map_terrain_is(road_offset, TERRAIN_WATER | TERRAIN_BUILDING | TERRAIN_AQUEDUCT)) {\n            city_warning_show(WARNING_CLEAR_LAND_NEEDED);\n            return 0;\n        }\n    } else if (type == BUILDING_SHIPYARD || type == BUILDING_WHARF) {')

rep('src/widget/city_building_ghost.c','    if (type == BUILDING_PLAZA && !map_terrain_is(grid_offset, TERRAIN_ROAD)) {\n        return 1;\n    }','    if (type == BUILDING_PLAZA && !map_terrain_is(grid_offset, TERRAIN_ROAD)) {\n        return 1;\n    }\n    if (type == BUILDING_ROADBLOCK && !map_terrain_is(grid_offset, TERRAIN_ROAD)) {\n        return 1;\n    }')
rep('src/widget/city_building_ghost.c','        if (type == BUILDING_GATEHOUSE || type == BUILDING_TRIUMPHAL_ARCH || type == BUILDING_PLAZA) {\n            forbidden_terrain &= ~TERRAIN_ROAD;\n        }','        if (type == BUILDING_GATEHOUSE || type == BUILDING_TRIUMPHAL_ARCH ||\n            type == BUILDING_PLAZA || type == BUILDING_ROADBLOCK) {\n            forbidden_terrain &= ~TERRAIN_ROAD;\n        }')
rep('src/map/road_access.c','        if (b->type == BUILDING_GATEHOUSE) {\n            is_road = 0;','        if (b->type == BUILDING_GATEHOUSE || b->type == BUILDING_ROADBLOCK) {\n            is_road = 0;')
rep('src/figure/movement.c','            if (building_get(map_building_at(target_grid_offset))->type == BUILDING_GATEHOUSE) {\n                // do not allow roaming through gatehouse','            building_type blocked_type = building_get(map_building_at(target_grid_offset))->type;\n            if (blocked_type == BUILDING_GATEHOUSE || blocked_type == BUILDING_ROADBLOCK) {\n                // do not allow roaming through gatehouse/roadblock')

rep('src/map/building_tiles.c','    building *b = building_get(building_id);\n    if (building_id && building_is_farm(b->type)) {','    building *b = building_get(building_id);\n    int restore_road = building_id && b->type == BUILDING_ROADBLOCK;\n    if (building_id && building_is_farm(b->type)) {')
rep('src/map/building_tiles.c','            } else {\n                map_image_set(grid_offset,\n                    image_group(GROUP_TERRAIN_UGLY_GRASS) +\n                    (map_random_get(grid_offset) & 7));\n                map_terrain_remove(grid_offset, TERRAIN_CLEARABLE);\n            }','            } else if (restore_road) {\n                map_terrain_set(grid_offset, TERRAIN_ROAD);\n                map_tiles_set_road(x + dx, y + dy);\n            } else {\n                map_image_set(grid_offset,\n                    image_group(GROUP_TERRAIN_UGLY_GRASS) +\n                    (map_random_get(grid_offset) & 7));\n                map_terrain_remove(grid_offset, TERRAIN_CLEARABLE);\n            }',1)

rep('src/translation/translation.h','    TR_CONFIG_SHOW_MARKET_RANGE,\n    TR_CONFIG_HIGHLIGHT_LEGIONS,','    TR_CONFIG_SHOW_MARKET_RANGE,\n    TR_BUILDING_ROADBLOCK_NAME,\n    TR_BUILDING_ROADBLOCK_DESC,\n    TR_CONFIG_HIGHLIGHT_LEGIONS,')
rep('src/translation/english.c','    {TR_CONFIG_SHOW_CONSTRUCTION_SIZE, "Show draggable construction size"},','    {TR_CONFIG_SHOW_CONSTRUCTION_SIZE, "Show draggable construction size"},\n    {TR_BUILDING_ROADBLOCK_NAME, "Roadblock"},\n    {TR_BUILDING_ROADBLOCK_DESC, "Blocks roaming service walkers while allowing destination-based walkers to pass."},')
rep('src/translation/korean.c','    {TR_CONFIG_SHOW_CONSTRUCTION_SIZE, "드래그 건설 시 전체 크기 표시"},','    {TR_CONFIG_SHOW_CONSTRUCTION_SIZE, "드래그 건설 시 전체 크기 표시"},\n    {TR_BUILDING_ROADBLOCK_NAME, "노상 장애물"},\n    {TR_BUILDING_ROADBLOCK_DESC, "배회형 서비스 인력의 통행을 막고, 목적지가 정해진 운반·구매 인력은 통과시킵니다."},')

rep('src/window/build_menu.c','        if (is_all_button(type)) {\n            text_draw_centered(translation_for(TR_BUILD_ALL_TEMPLES),\n                item_x_align, data.y_offset + MENU_Y_OFFSET + 4 + MENU_ITEM_HEIGHT * i,\n                MENU_ITEM_WIDTH, FONT_NORMAL_GREEN, 0);\n        } else {\n            lang_text_draw_centered(28, type, item_x_align, data.y_offset + MENU_Y_OFFSET + 4 + MENU_ITEM_HEIGHT * i,\n                MENU_ITEM_WIDTH, FONT_NORMAL_GREEN);\n        }','        if (is_all_button(type)) {\n            text_draw_centered(translation_for(TR_BUILD_ALL_TEMPLES),\n                item_x_align, data.y_offset + MENU_Y_OFFSET + 4 + MENU_ITEM_HEIGHT * i,\n                MENU_ITEM_WIDTH, FONT_NORMAL_GREEN, 0);\n        } else if (type == BUILDING_ROADBLOCK) {\n            text_draw_centered(translation_for(TR_BUILDING_ROADBLOCK_NAME),\n                item_x_align, data.y_offset + MENU_Y_OFFSET + 4 + MENU_ITEM_HEIGHT * i,\n                MENU_ITEM_WIDTH, FONT_NORMAL_GREEN, 0);\n        } else {\n            lang_text_draw_centered(28, type, item_x_align, data.y_offset + MENU_Y_OFFSET + 4 + MENU_ITEM_HEIGHT * i,\n                MENU_ITEM_WIDTH, FONT_NORMAL_GREEN);\n        }')

rep('src/window/building_info.c','#include "graphics/screen.h"\n','#include "graphics/screen.h"\n#include "graphics/text.h"\n')
rep('src/window/building_info.c','#include "window/building/utility.h"\n','#include "window/building/utility.h"\n#include "translation/translation.h"\n')
rep('src/window/building_info.c','            case BUILDING_POTTERY_WORKSHOP:\n                return 1;','            case BUILDING_POTTERY_WORKSHOP:\n            case BUILDING_ROADBLOCK:\n                return 1;')
anchor='static void draw_background(void)\n{\n'
roadinfo='''static void draw_roadblock_info(building_info_context *c)
{
    c->help_id = 0;
    outer_panel_draw(c->x_offset, c->y_offset, c->width_blocks, c->height_blocks);
    text_draw_centered(translation_for(TR_BUILDING_ROADBLOCK_NAME),
        c->x_offset, c->y_offset + 12, BLOCK_SIZE * c->width_blocks, FONT_LARGE_BLACK, 0);
    text_draw_multiline(translation_for(TR_BUILDING_ROADBLOCK_DESC),
        c->x_offset + 32, c->y_offset + 64, BLOCK_SIZE * c->width_blocks - 64, FONT_NORMAL_BLACK, 0);
}

'''
rep('src/window/building_info.c',anchor,roadinfo+anchor)
rep('src/window/building_info.c','        } else if (btype == BUILDING_MARKET) {\n            window_building_draw_market(&context);','        } else if (btype == BUILDING_ROADBLOCK) {\n            draw_roadblock_info(&context);\n        } else if (btype == BUILDING_MARKET) {\n            window_building_draw_market(&context);')

print('Single-exe roadblock patch applied:',root)
