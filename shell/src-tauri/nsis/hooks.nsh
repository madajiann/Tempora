; Tempora NSIS hooks
; 目标：安装/卸载完成后直接跳到"完成"页，不再让用户多点一次"下一步"

!include "WinMessages.nsh"

!macro NSIS_HOOK_PREINSTALL
  ; 壳（tempora-shell.exe）退出时用裸 std::process::Command 拉起的内核子进程
  ; tempora.exe 不会被 tauri 的 cleanup_before_exit 回收（它只管自己追踪的
  ; 子进程），会一直锁着安装目录里的 tempora.exe，导致 NSIS 静默覆盖失败、
  ; 装了个寂寞、重启后版本没变又提示更新。装之前先杀掉内核，留 300ms
  ; 让句柄彻底释放。
  nsExec::Exec 'taskkill /F /IM tempora.exe'
  Pop $0
  Sleep 300
!macroend

!macro NSIS_HOOK_POSTINSTALL
  ; tauri 模板 Section 末尾只在 passive/silent 模式才 SetAutoClose true，
  ; 普通模式下 INSTFILES 完成后会停在"下一步"按钮 —— 这里无条件打开自动跳转，
  ; 安装完直接进 MUI 完成页。
  SetAutoClose true
!macroend

!macro NSIS_HOOK_POSTUNINSTALL
  ; 卸载完成同样自动跳到完成页
  SetAutoClose true
!macroend
