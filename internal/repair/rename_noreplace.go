package repair

import "tempora/internal/fileutil"

func renameRepairNodeNoReplace(oldPath, newPath string) error {
	return fileutil.RenameNoReplace(oldPath, newPath)
}
