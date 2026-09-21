import type { TabMeta } from "./types";

export function tabWorkspaceTitle(tab?: TabMeta): string {
  if (!tab) return "全局（Global）";
  if (tab.scope === "project") return tab.workspaceName || tab.workspaceRoot || "项目（Project）";
  if (tab.scope === "global") return tab.workspaceName || "全局（Global）";
  return tab.workspaceName || tab.workspaceRoot || "全局（Global）";
}

export function topicTitle(tab?: TabMeta): string {
  if (!tab) return "全局（Global）";
  const workspaceTitle = tabWorkspaceTitle(tab);
  const topic = tab.topicTitle || (tab.scope === "global" ? workspaceTitle : "Untitled");
  return topic === workspaceTitle ? workspaceTitle : `${workspaceTitle} / ${topic}`;
}

export function topicDisplayTitle(tab?: TabMeta): string {
  if (!tab) return "全局（Global）";
  return tab.topicTitle || (tab.scope === "global" ? tabWorkspaceTitle(tab) : "Untitled");
}

export function safeFilename(name: string): string {
  const cleaned = name.trim().replace(/[\\/:*?"<>|]+/g, "-").replace(/\s+/g, " ").slice(0, 80);
  return cleaned || "tempora-session";
}
