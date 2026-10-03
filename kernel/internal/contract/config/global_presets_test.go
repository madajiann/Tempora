// Ported from DeepSeek-Reasonix (MIT) — upstream PR #11193.
// 上游版权声明按 MIT 要求保留：Copyright (c) Reasonix Contributors.
// 本地改动：归属头期望值跟随 global_presets.go 改为 Tempora。
package config

import "testing"

func TestGlobalProviderPresetsAreOffered(t *testing.T) {
	offered := map[string]ProviderPreset{}
	for _, preset := range CuratedProviderPresets() {
		offered[preset.ID] = preset
	}
	for _, id := range []string{"openrouter", "openai", "gemini", "volcengine-coding-plan"} {
		preset, ok := offered[id]
		if !ok {
			t.Fatalf("preset %q is not offered", id)
		}
		if preset.KeyEnv == "" || len(preset.Entries) != 1 || preset.Entries[0].APIKeyEnv != preset.KeyEnv {
			t.Fatalf("preset %q key wiring = %q / %+v", id, preset.KeyEnv, preset.Entries)
		}
	}
}

func TestOpenRouterPresetAttributesTrafficToTempora(t *testing.T) {
	preset, ok := CuratedProviderPreset("openrouter")
	if !ok {
		t.Fatal("openrouter preset missing")
	}
	var cfg Config
	if err := cfg.UpsertProvider(preset.Entries[0]); err != nil {
		t.Fatalf("upsert: %v", err)
	}
	entry, ok := cfg.Provider("openrouter")
	if !ok {
		t.Fatal("openrouter provider missing after upsert")
	}
	if entry.Headers["HTTP-Referer"] != "https://tempora.yomm.cc" || entry.Headers["X-OpenRouter-Title"] != "Tempora" {
		t.Fatalf("attribution headers = %v", entry.Headers)
	}
	if entry.DefaultModel() != "deepseek/deepseek-v4-flash" {
		t.Fatalf("default model = %q", entry.DefaultModel())
	}
	if entry.HasVisionModel("deepseek/deepseek-v4-pro") || !entry.HasVisionModel("openai/gpt-6-sol") {
		t.Fatalf("vision declaration = %v", entry.VisionModels)
	}
}

func TestOpenAIPresetDeclaresTheGPT6EffortLadder(t *testing.T) {
	preset, ok := CuratedProviderPreset("openai")
	if !ok {
		t.Fatal("openai preset missing")
	}
	var cfg Config
	if err := cfg.UpsertProvider(preset.Entries[0]); err != nil {
		t.Fatalf("upsert: %v", err)
	}
	resolved, ok := cfg.ResolveModel("openai/gpt-6-sol")
	if !ok {
		t.Fatal("openai/gpt-6-sol did not resolve")
	}
	capability := EffortCapabilityForEntry(resolved)
	if !stringSlicesEqual(capability.Levels, []string{"auto", "low", "medium", "high", "xhigh", "max"}) || capability.Default != "medium" {
		t.Fatalf("effort capability = %+v", capability)
	}
	if !EffectiveVision(resolved) {
		t.Fatal("gpt-6-sol should read images")
	}
}
