package main

import "strings"

func (a *App) trayLocale() string {
	cfg, _, err := a.loadDesktopUserConfigForView()
	if err != nil {
		return ""
	}
	return cfg.DesktopLanguage()
}

func (a *App) showFromTray() {
	a.showMainWindowFrom("tray")
}

func (a *App) quitFromTray() {
	a.quitApp()
}

type trayLabels struct {
	openTitle   string
	openTooltip string
	quitTitle   string
	quitTooltip string
}

func trayMenuLabels(locale string) trayLabels {
	// Unset ("") and "auto" mean the user has not picked a language: default
	// the tray menu to Chinese rather than English. An explicit non-zh choice
	// (including unknown values) keeps the English fallback.
	switch strings.ToLower(strings.TrimSpace(locale)) {
	case "", "auto", "zh":
		return trayLabels{
			openTitle:   "打开",
			openTooltip: "打开 Tempora 窗口",
			quitTitle:   "退出",
			quitTooltip: "退出 Tempora",
		}
	}
	return trayLabels{
		openTitle:   "Open",
		openTooltip: "Open the Tempora window",
		quitTitle:   "Quit",
		quitTooltip: "Quit Tempora",
	}
}
