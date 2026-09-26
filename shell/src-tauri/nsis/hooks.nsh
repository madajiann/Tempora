; Tempora NSIS hooks：安装/卸载完成后的下一步自动跳到完成，不再停留等点击

!include "WinMessages.nsh"

!macro NSIS_HOOK_POSTINSTALL
  ; INSTFILES 跑完立即模拟点击"下一步"，直接进完成页
  SendMessage $HWNDPARENT ${WM_COMMAND} 1 0
!macroend

!macro NSIS_HOOK_POSTUNINSTALL
  ; 卸载跑完立即模拟点击"关闭"，直接结束
  SendMessage $HWNDPARENT ${WM_COMMAND} 1 0
!macroend
