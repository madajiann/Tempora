// Per-model effort vocabulary. A gateway that serves several vendors' models
// behind one address and key does not share one ladder between them — a relay
// may accept "high" for one backend and "xhigh" for another — so a model may
// declare its own; a blank field inherits the connection's.
// Ported from DeepSeek-Reasonix (MIT) — Tempora fork.
import { t } from "../i18n";
import type { ModelEffort } from "../port/port";
import { parseEffortLevels } from "./provider_compat";
import { shortId } from "./ModelLimits";

export interface EffortText {
  levels: string;
  def: string;
}

export function effortTextOf(own: ModelEffort | undefined): EffortText {
  return { levels: (own?.supportedEfforts ?? []).join(", "), def: own?.defaultEffort ?? "" };
}

// The default is only sent when it names one of the model's own levels: the
// kernel refuses a default outside the vocabulary rather than storing a
// contradiction that resolves to the first level later.
export function effortsToSend(
  picked: string[],
  text: Record<string, EffortText>,
  stored: Record<string, ModelEffort>,
): Record<string, ModelEffort> {
  const out: Record<string, ModelEffort> = {};
  for (const model of picked) {
    const cur = text[model];
    if (!cur) continue;
    const was = stored[model];
    // An untouched field is sent back as stored, so a level typed by hand and
    // one loaded from the file are indistinguishable to the kernel.
    const same = cur.levels === (was?.supportedEfforts ?? []).join(", ") && cur.def === (was?.defaultEffort ?? "");
    const levels = same ? (was?.supportedEfforts ?? []) : parseEffortLevels(cur.levels);
    const def = levels.includes(cur.def) ? cur.def : "";
    if (levels.length || def) {
      out[model] = {
        ...(levels.length ? { supportedEfforts: levels } : {}),
        ...(def ? { defaultEffort: def } : {}),
      };
    }
  }
  return out;
}

export function ModelEfforts({
  models, value, onChange, inherited, dormant,
}: {
  models: string[];
  value: Record<string, EffortText>;
  onChange: (next: Record<string, EffortText>) => void;
  inherited: (model: string) => ModelEffort | null | undefined;
  // A protocol with a fixed vocabulary has no ladder to override, so the
  // fields stay visible but inert rather than offering a choice nothing honours.
  dormant?: boolean;
}) {
  const set = (model: string, patch: Partial<EffortText>) =>
    onChange({ ...value, [model]: { ...(value[model] ?? { levels: "", def: "" }), ...patch } });
  return (
    <div className="ml-group" role="group" aria-label={t("按模型设置推理档位")}>
      <div className="ml-head">
        <strong>{t("按模型设置推理档位")}</strong>
        <span>{t("留空的模型沿用上面的档位，灰字是它当前继承到的值；填写后只对该模型生效。")}</span>
      </div>
      <ul className="me-list ml-list">
        {models.map((model) => {
          const cur = value[model] ?? { levels: "", def: "" };
          const own = parseEffortLevels(cur.levels);
          const from = inherited(model);
          // While a model declares nothing the menu offers what it inherits,
          // so the choice the connection already makes stays visible.
          const menu = own.length ? own : (from?.supportedEfforts ?? []);
          return (
            <li key={model} className="ml-row ml-row-efforts" data-model={model} data-own={cur.levels.trim() !== "" || undefined}>
              <span className="me-name" title={model}>{shortId(model)}</span>
              <input
                data-action="provider.draft" data-value="model-efforts"
                aria-label={t("{model} 的推理档位", { model })} value={cur.levels} spellCheck={false}
                placeholder={from?.supportedEfforts?.length
                  ? t("继承 {n}", { n: from.supportedEfforts.join(", ") })
                  : t("继承：未声明")}
                disabled={dormant}
                onChange={(e) => set(model, { levels: e.target.value })}
              />
              <select
                data-action="provider.draft" data-value="model-default-effort"
                aria-label={t("{model} 的默认档位", { model })}
                value={own.includes(cur.def) ? cur.def : ""}
                disabled={dormant || menu.length === 0}
                onChange={(e) => set(model, { def: e.target.value })}
              >
                <option value="">{from?.defaultEffort ? t("继承 {n}", { n: from.defaultEffort }) : t("第一个档位")}</option>
                {menu.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
