using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using StardewModdingAPI;
using StardewValley;
using StardewValley.ItemTypeDefinitions;
using StardewValley.Objects;
using StardewValley.Tools;
using SObject = StardewValley.Object;

namespace BaitCountOverlay
{
    public sealed class ModEntry : Mod
    {
        internal static IMonitor Log = null!;

        public override void Entry(IModHelper helper)
        {
            Log = this.Monitor;

            // Cached item sprites may become stale when another mod invalidates game content.
            // The cache is tiny, so clearing it on any content invalidation is cheap and robust.
            helper.Events.Content.AssetsInvalidated += (_, _) => BaitOverlayPatch.ClearSpriteCache();

            try
            {
                var harmony = new Harmony(this.ModManifest.UniqueID);
                harmony.PatchAll(Assembly.GetExecutingAssembly());
            }
            catch (Exception ex)
            {
                this.Monitor.Log($"Failed to apply Harmony patches:\n{ex}", LogLevel.Error);
            }
        }
    }

    [HarmonyPatch]
    internal static class BaitOverlayPatch
    {
        private static readonly Dictionary<string, (Texture2D Tex, Rectangle Src)> SpriteCache =
            new(StringComparer.Ordinal);

        internal static void ClearSpriteCache()
        {
            SpriteCache.Clear();
        }

        // Patch only ONE primary overload (max parameters) to avoid duplicate drawing.
        static IEnumerable<MethodBase> TargetMethods()
        {
            MethodInfo? rodPrimary = GetPrimaryDrawInMenuDeclared(typeof(FishingRod));
            if (rodPrimary != null)
                return new[] { rodPrimary };

            MethodInfo? toolPrimary = GetPrimaryDrawInMenuDeclared(typeof(Tool));
            if (toolPrimary != null)
                return new[] { toolPrimary };

            ModEntry.Log?.Log("No drawInMenu method found to patch; mod will do nothing.", LogLevel.Warn);
            return Array.Empty<MethodBase>();
        }

        private static MethodInfo? GetPrimaryDrawInMenuDeclared(Type type)
        {
            var candidates = AccessTools.GetDeclaredMethods(type)
                .Where(m => m.Name.Equals("drawInMenu", StringComparison.OrdinalIgnoreCase))
                .Where(m =>
                {
                    var p = m.GetParameters();
                    return p.Length >= 5
                        && p[0].ParameterType == typeof(SpriteBatch)
                        && p[1].ParameterType == typeof(Vector2)
                        && p[2].ParameterType == typeof(float)
                        && p[3].ParameterType == typeof(float)
                        && p[4].ParameterType == typeof(float);
                })
                .ToList();

            return candidates.Count == 0
                ? null
                : candidates.OrderByDescending(m => m.GetParameters().Length).First();
        }

        static void Postfix(object __instance, object[] __args)
        {
            try
            {
                if (!Context.IsWorldReady)
                    return;

                if (__instance is not FishingRod rod)
                    return;

                if (__args == null || __args.Length < 5)
                    return;

                if (__args[0] is not SpriteBatch spriteBatch)
                    return;
                if (__args[1] is not Vector2 location)
                    return;
                if (__args[2] is not float scaleSize)
                    return;
                if (__args[3] is not float transparency)
                    return;

                // match vanilla behavior when stack drawing is hidden
                StackDrawType? stackDraw = FindStackDrawType(__args);
                if (stackDraw.HasValue && stackDraw.Value == StackDrawType.Hide)
                    return;

                Item? bait = TryGetBaitItem(rod);
                if (bait == null || bait.Stack <= 0)
                    return;

                // bait icon in top-left
                DrawBaitIcon(spriteBatch, bait, location, scaleSize, transparency);

                // bait count, matching the vanilla slingshot stack-count placement
                int count = bait.Stack;
                float digitsScale = 3f * scaleSize;
                int width = Utility.getWidthOfTinyDigitString(count, digitsScale);

                Vector2 digitsPos = location + new Vector2(
                    (float)(64 - width) + 3f * scaleSize,
                    64f - 18f * scaleSize + 1f
                );

                Utility.drawTinyDigits(count, spriteBatch, digitsPos, digitsScale, 1f, Color.White);
            }
            catch (Exception ex)
            {
                ModEntry.Log?.Log($"Bait overlay draw failed:\n{ex}", LogLevel.Trace);
            }
        }

        private static StackDrawType? FindStackDrawType(object[] args)
        {
            foreach (var a in args)
                if (a is StackDrawType s)
                    return s;
            return null;
        }

        private static Item? TryGetBaitItem(FishingRod rod)
        {
            try
            {
                Item? bait = rod.GetBait();
                if (bait != null && IsBait(bait))
                    return bait;
            }
            catch (Exception ex)
            {
                ModEntry.Log?.Log($"FishingRod.GetBait failed: {ex.Message}", LogLevel.Trace);
            }

            // Defensive fallback for unusual/custom rod implementations.
            try
            {
                foreach (var att in rod.attachments)
                    if (att is Item it && IsBait(it))
                        return it;
            }
            catch { }

            return null;
        }

        private static bool IsBait(Item item)
        {
            if (item is not SObject obj)
                return false;

            try { return obj.Category == SObject.baitCategory; }
            catch { return false; }
        }

        private static void DrawBaitIcon(SpriteBatch b, Item bait, Vector2 location, float scaleSize, float transparency)
        {
            Vector2 iconPos = location + new Vector2(4f, 3f);
            float iconScale = 2f * scaleSize;

            // SpecificBait / colored bait must be drawn like ColoredObject.drawInMenu (base + overlay)
            if (bait is ColoredObject colored)
            {
                int? variantIndex = GetVariantIndexForSpecificBait(bait) ?? colored.ParentSheetIndex;

                string baseQid = "(O)" + bait.ItemId;
                ParsedItemData itemData = ItemRegistry.GetDataOrErrorItem(baseQid);
                Texture2D tex = itemData.GetTexture();

                if (tex == null)
                    return;

                if (!colored.ColorSameIndexAsParentSheetIndex)
                {
                    Rectangle baseRect = itemData.GetSourceRect(0, variantIndex);
                    Rectangle overlayRect = itemData.GetSourceRect(1, variantIndex);

                    b.Draw(tex, iconPos, baseRect, Color.White * transparency, 0f, Vector2.Zero, iconScale, SpriteEffects.None, 1f);
                    b.Draw(tex, iconPos, overlayRect, colored.color.Value * transparency, 0f, Vector2.Zero, iconScale, SpriteEffects.None, 1f);
                }
                else
                {
                    Rectangle rect = itemData.GetSourceRect(0, variantIndex);
                    b.Draw(tex, iconPos, rect, colored.color.Value * transparency, 0f, Vector2.Zero, iconScale, SpriteEffects.None, 1f);
                }

                return;
            }

            // normal bait
            if (!TryGetSprite(bait.QualifiedItemId, out Texture2D tex2, out Rectangle src2))
                return;

            b.Draw(
                tex2,
                iconPos,
                src2,
                Color.White * transparency,
                0f,
                Vector2.Zero,
                iconScale,
                SpriteEffects.None,
                1f
            );
        }

        private static int? GetVariantIndexForSpecificBait(Item bait)
        {
            // example: "(O)SpecificBait/704"
            const string prefix = "(O)SpecificBait/";
            string qid = bait.QualifiedItemId;
            if (qid != null && qid.StartsWith(prefix, StringComparison.Ordinal))
            {
                string tail = qid.Substring(prefix.Length);
                if (int.TryParse(tail, out int fishIndex))
                    return fishIndex;
            }
            return null;
        }

        private static bool TryGetSprite(string qualifiedItemId, out Texture2D tex, out Rectangle src)
        {
            tex = null!;
            src = Rectangle.Empty;

            if (string.IsNullOrWhiteSpace(qualifiedItemId))
                return false;

            if (SpriteCache.TryGetValue(qualifiedItemId, out var cached))
            {
                tex = cached.Tex;
                src = cached.Src;
                return tex != null;
            }

            try
            {
                ParsedItemData data = ItemRegistry.GetDataOrErrorItem(qualifiedItemId);
                tex = data.GetTexture();
                src = data.GetSourceRect();

                if (tex != null)
                {
                    SpriteCache[qualifiedItemId] = (tex, src);
                    return true;
                }
            }
            catch (Exception ex)
            {
                ModEntry.Log?.Log($"Failed to resolve sprite for '{qualifiedItemId}': {ex.Message}", LogLevel.Trace);
            }

            return false;
        }
    }
}
