// Ported from DeepSeek-Reasonix (MIT)
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { JobEntry } from "../port/port";
import { t } from "../i18n";
import { StudioIcon } from "./StudioIcon";
import { agentsIn } from "./panels/derive";
import { Agents } from "./panels/Agents";
import { AgentTranscript } from "./panels/AgentTranscript";
import { Jobs } from "./panels/Jobs";
import type { Task } from "./panels/Agents";
import { useDismiss } from "./dismiss";

export type Deck = "" | "agents" | "jobs";

/** What is running on this session's behalf but is not in the transcript: work
 *  handed to a sub-agent, and processes left running in the background. The
 *  readings sit at the right end of the run rail, beside the other numbers
 *  about this turn, and each opens on hover the way the context reading does —
 *  one gesture for every summary on this row. */
export function DeckChips({ tasks, jobs, open, onOpen, onCancelJob }: { tasks: Task[]; jobs: JobEntry[]; open: Deck; onOpen: (next: (was: Deck) => Deck) => void; onCancelJob?: (id: string) => Promise<void> }) {
  const agentsBox = useRef<HTMLDivElement>(null);
  const jobsBox = useRef<HTMLDivElement>(null);
  const [viewing, setViewing] = useState("");
  const viewed = viewing ? tasks.find((x) => x.id === viewing) : undefined;
  // The transcript is drawn from the task in hand, so a delegate that has left
  // the list — it was capped off the rail, or the session moved — takes the
  // overlay with it rather than leaving a record nothing can close.
  useEffect(() => {
    if (viewing && !viewed) setViewing("");
  }, [viewing, viewed]);
  const closeView = useCallback(() => {
    setViewing("");
    // Focus goes back to the chip that opened it: closing an overlay onto the
    // page behind it is how a keyboard reader ends up at the top of the window.
    agentsBox.current?.querySelector<HTMLElement>('[data-action="deck.agents"]')?.focus();
  }, []);
  const shut = useCallback(() => onOpen(() => ""), [onOpen]);
  useDismiss(open === "agents", agentsBox, shut);
  useDismiss(open === "jobs", jobsBox, shut);
  const liveAgents = useMemo(() => agentsIn(tasks.filter((x) => x.running)), [tasks]);
  const liveJobs = useMemo(() => jobs.filter((j) => j.status === "running").length, [jobs]);
  if (tasks.length === 0 && jobs.length === 0) return null;

  // A delegate that finished is still here, because its record is still here:
  // this is where a sub-agent's own steps are read. Only the live reading
  // animates — a count that kept ticking after the work stopped would read as
  // work still going.
  return (
    <>
      {tasks.length > 0 && (
        <div ref={agentsBox} className="studio-deck-anchor" data-open={open === "agents" ? "" : undefined}>
          <button
            type="button"
            className="studio-deckchip"
            data-action="deck.agents"
            data-live={liveAgents ? "" : undefined}
            aria-expanded={open === "agents"}
            aria-haspopup="dialog"
            onClick={() => onOpen((was) => (was === "agents" ? "" : "agents"))}
          >
            <StudioIcon name="branch" />
            <b>{agentsIn(tasks)}</b>
            <span>{t("子代理")}</span>
          </button>
          <div className="studio-deck-pop" role="dialog" aria-label={t("子代理")}>
            <Agents tasks={tasks} onOpen={(id) => { shut(); setViewing(id); }} />
          </div>
        </div>
      )}
      {viewed && <AgentTranscript task={viewed} onClose={closeView} />}
      {jobs.length > 0 && (
        <div ref={jobsBox} className="studio-deck-anchor" data-open={open === "jobs" ? "" : undefined}>
          <button
            type="button"
            className="studio-deckchip"
            data-action="deck.jobs"
            data-live={liveJobs ? "" : undefined}
            aria-expanded={open === "jobs"}
            aria-haspopup="dialog"
            onClick={() => onOpen((was) => (was === "jobs" ? "" : "jobs"))}
          >
            <StudioIcon name="play" />
            <b>{liveJobs || jobs.length}</b>
            <span>{t("后台任务")}</span>
          </button>
          <div className="studio-deck-pop" role="dialog" aria-label={t("后台任务")}>
            <Jobs jobs={jobs} onCancel={onCancelJob} />
          </div>
        </div>
      )}
    </>
  );
}
