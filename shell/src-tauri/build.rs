// Tempora 轻壳构建脚本。
//
// Windows 下 rustc 默认链接成 CONSOLE 子系统，双击启动会先弹出一个黑色控制台
// 窗口。这里在 Windows 宿主上把子系统改成 WINDOWS，并指定 GUI 程序的入口点，
// 彻底去掉那个黑窗口。其他平台保持默认不动。

#[cfg(target_os = "windows")]
fn drop_console_subsystem() {
    for arg in ["/SUBSYSTEM:WINDOWS", "/ENTRY:mainCRTStartup"] {
        println!("cargo:rustc-link-arg={arg}");
    }
}

#[cfg(not(target_os = "windows"))]
fn drop_console_subsystem() {}

fn main() {
    drop_console_subsystem();
    // 应用自有命令必须在这里登记，tauri-build 才会为它们自动生成
    // allow-/deny- 权限文件（否则 capability 里写 allow-pick-folder 会
    // 报 "Permission allow-pick-folder not found"，运行期则报
    // "Command pick_folder not allowed by ACL"）。
    tauri_build::try_build(
        tauri_build::Attributes::new()
            .app_manifest(tauri_build::AppManifest::new().commands(&["pick_folder", "update_status", "open_updater"])),
    )
    .expect("failed to run tauri-build");
}
