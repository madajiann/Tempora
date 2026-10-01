//go:build windows

package serve

import (
	"context"
	"errors"

	"github.com/sqweek/dialog"
)

// pickLocalFolder opens the native Windows folder picker and returns the chosen
// directory. The previous implementation shelled out to PowerShell with the
// console hidden (-WindowStyle Hidden + HideWindow), which left the modal
// FolderBrowserDialog owned by an invisible window — it never appeared, so the
// "+" in the sidebar looked dead. sqweek/dialog drives SHBrowseForFolder
// directly with no hidden parent, so the dialog shows and receives focus.
func pickLocalFolder(ctx context.Context, startIn string) (string, error) {
	b := dialog.Directory().Title("选择 Tempora Studio 工作区")
	if startIn != "" {
		b = b.SetStartDir(startIn)
	}
	dir, err := b.Browse()
	if errors.Is(err, dialog.ErrCancelled) {
		// A cancellation is an answer, not a failure: the frontend treats the
		// empty path as "user dismissed the picker", which asks nothing again.
		return "", nil
	}
	if err != nil {
		return "", err
	}
	return dir, nil
}
