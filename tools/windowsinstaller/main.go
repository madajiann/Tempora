// Command windowsinstaller builds the Tempora Windows setup executable.
//
// The built exe embeds the CLI payload (payload/tempora.exe). Running it
// installs Tempora for the current user without admin rights: it writes the
// binary to %LOCALAPPDATA%\Programs\tempora, appends that directory to the
// user PATH in the registry, and broadcasts WM_SETTINGCHANGE so new terminals
// pick the change up. It is a nested module (like sdk/go) so the root module's
// `go build ./...` never requires the payload to exist.
package main

import (
	"bufio"
	"embed"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"syscall"
	"unsafe"

	"golang.org/x/sys/windows/registry"
)

//go:embed payload/tempora.exe
var payload embed.FS

var (
	flagDir    string
	flagSilent bool
)

const (
	payloadName     = "tempora.exe"
	appDirName      = "tempora"
	wndBroadcast    = 0xFFFF // HWND_BROADCAST
	msgSettingChg   = 0x001A // WM_SETTINGCHANGE
	smtoAbortIfHung = 0x0002
)

func main() {
	if err := run(); err != nil {
		fmt.Printf("安装失败: %v\n", err)
		fmt.Println("\n按回车键退出...")
		waitEnter()
		os.Exit(1)
	}
	if !flagSilent {
		fmt.Println("\n按回车键退出...")
		waitEnter()
	}
}

func run() error {
	setConsoleUTF8()

	flag.StringVar(&flagDir, "dir", "", `自定义安装目录，例如 -dir D:\Tools\Tempora`)
	flag.BoolVar(&flagSilent, "silent", false, "静默模式：不询问、完成后不等待按键")
	flag.Usage = func() {
		fmt.Println("Tempora Windows 安装器")
		fmt.Println("用法: TemporaSetup.exe [-dir 安装目录] [--silent]")
		fmt.Println("  -dir D:\\Tools\\Tempora   安装到指定目录（默认 %LOCALAPPDATA%\\Programs\\tempora）")
		fmt.Println("  --silent                静默安装，不询问、完成后不等待按键")
	}
	flag.Parse()

	localAppData := os.Getenv("LOCALAPPDATA")
	if localAppData == "" {
		return fmt.Errorf("未找到 LOCALAPPDATA 环境变量")
	}
	destDir := filepath.Join(localAppData, "Programs", appDirName)
	if flagDir != "" {
		abs, err := filepath.Abs(flagDir)
		if err != nil {
			return fmt.Errorf("解析目录 %s: %w", flagDir, err)
		}
		destDir = abs
	} else if !flagSilent {
		fmt.Println("Tempora v0.1.0 安装器")
		fmt.Printf("默认安装目录: %s\n", destDir)
		fmt.Print("直接回车使用默认目录，或输入其他目录（如 D:\\Tools\\Tempora）后回车: ")
		if line := readLine(); strings.TrimSpace(line) != "" {
			abs, err := filepath.Abs(strings.TrimSpace(line))
			if err != nil {
				return fmt.Errorf("解析目录 %s: %w", line, err)
			}
			destDir = abs
		}
	}
	destExe := filepath.Join(destDir, payloadName)

	bin, err := payload.ReadFile("payload/" + payloadName)
	if err != nil {
		return fmt.Errorf("安装包缺少内嵌的 %s（请用 make windows-installer 构建）: %w", payloadName, err)
	}

	if err := os.MkdirAll(destDir, 0o755); err != nil {
		return fmt.Errorf("创建目录 %s: %w", destDir, err)
	}
	if err := os.WriteFile(destExe, bin, 0o755); err != nil {
		return fmt.Errorf("写入 %s: %w", destExe, err)
	}
	fmt.Printf("已安装: %s\n", destExe)

	added, err := ensureUserPath(destDir)
	if err != nil {
		fmt.Printf("警告: PATH 写入失败（可手动把 %s 加入用户 PATH）: %v\n", destDir, err)
	} else if added {
		fmt.Printf("已加入用户 PATH\n")
		broadcastEnvChange()
	} else {
		fmt.Printf("用户 PATH 已包含安装目录，无需修改\n")
	}

	fmt.Println("\n安装完成! 打开一个新的终端窗口，然后:")
	fmt.Println("  tempora doctor            环境自检")
	fmt.Println("  tempora setup             配置向导 (DEEPSEEK_API_KEY / GLM_API_KEY)")
	fmt.Println("  tempora                   交互式会话")
	fmt.Println("  tempora --model glm-flash 使用智谱 GLM-5.3-Flash")
	fmt.Println("\n卸载: 删除上述目录，并从用户 PATH 中移除该目录即可。")
	return nil
}

// ensureUserPath appends dir to the user PATH (HKCU\Environment) when missing,
// preserving the value's registry type. Reports whether the value changed.
func ensureUserPath(dir string) (bool, error) {
	key, err := registry.OpenKey(registry.CURRENT_USER, `Environment`, registry.QUERY_VALUE|registry.SET_VALUE)
	if err != nil {
		return false, err
	}
	defer key.Close()

	val, valType, err := key.GetStringValue("Path")
	if err != nil && err != registry.ErrNotExist {
		return false, err
	}
	for _, part := range strings.Split(val, ";") {
		if strings.EqualFold(strings.TrimSpace(part), dir) {
			return false, nil
		}
	}
	newVal := strings.TrimSpace(val)
	if newVal == "" {
		newVal = dir
	} else {
		newVal = newVal + ";" + dir
	}
	if valType == registry.EXPAND_SZ {
		err = key.SetExpandStringValue("Path", newVal)
	} else {
		err = key.SetStringValue("Path", newVal)
	}
	return err == nil, err
}

// broadcastEnvChange asks running Explorer instances to reload the
// environment so newly opened terminals see the updated PATH.
func broadcastEnvChange() {
	user32 := syscall.NewLazyDLL("user32.dll")
	proc := user32.NewProc("SendMessageTimeoutW")
	envPtr, err := syscall.UTF16PtrFromString("Environment")
	if err != nil {
		return
	}
	var result uintptr
	proc.Call(
		uintptr(wndBroadcast),
		uintptr(msgSettingChg),
		0,
		uintptr(unsafe.Pointer(envPtr)),
		uintptr(smtoAbortIfHung),
		2000,
		uintptr(unsafe.Pointer(&result)),
	)
}

func setConsoleUTF8() {
	kernel32 := syscall.NewLazyDLL("kernel32.dll")
	if p := kernel32.NewProc("SetConsoleOutputCP"); p.Find() == nil {
		p.Call(65001)
	}
}

func waitEnter() {
	var buf [1]byte
	_, _ = os.Stdin.Read(buf[:])
}

// readLine reads one line from stdin; on EOF or error returns "" (use default).
func readLine() string {
	sc := bufio.NewScanner(os.Stdin)
	if !sc.Scan() {
		return ""
	}
	return sc.Text()
}
