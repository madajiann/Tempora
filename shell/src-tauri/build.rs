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
    tauri_build::build();
}
