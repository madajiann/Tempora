// Tempora 轻壳入口。
// 官方 React SPA 只与 127.0.0.1 内核通信，因此壳只负责窗口、托盘、菜单、更新。
// 行为约定：
//   - 点关闭 = 隐藏到托盘（不退出，内核常驻）
//   - 托盘左键 = 显示/隐藏 切换
//   - 托盘右键菜单 = 显示主窗口 / 检查更新 / 退出
//   - 启动 5 秒后静默检查更新，发现新版自动弹出右上角更新窗口
//   - 更新窗口(updater.html)负责下载进度条与安装，endpoint 见 tauri.conf.json
use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Manager,
};
use tauri_plugin_updater::UpdaterExt;

fn show_main(app: &tauri::AppHandle) {
    if let Some(w) = app.get_webview_window("main") {
        let _ = w.show();
        let _ = w.unminimize();
        let _ = w.set_focus();
    }
}

fn open_update_window(app: &tauri::AppHandle) {
    if let Some(w) = app.get_webview_window("updater") {
        let _ = w.show();
        let _ = w.set_focus();
        return;
    }
    // 位置：主窗口右上角内侧弹出（物理像素 -> 逻辑像素换算）
    let (mut x, mut y) = (100.0, 100.0);
    if let Some(m) = app.get_webview_window("main") {
        if let (Ok(p), Ok(s)) = (m.outer_position(), m.outer_size()) {
            let scale = m.scale_factor().unwrap_or(1.0).max(0.5);
            x = (p.x as f64 + s.width as f64) / scale - 404.0;
            y = p.y as f64 / scale + 24.0;
        }
    }
    let _ = tauri::WebviewWindowBuilder::new(
        app,
        "updater",
        tauri::WebviewUrl::App("updater.html".into()),
    )
    .title("Tempora 更新")
    .inner_size(380.0, 210.0)
    .decorations(false)
    .resizable(false)
    .always_on_top(true)
    .skip_taskbar(true)
    .shadow(true)
    .position(x, y)
    .build();
}

async fn silent_check(app: tauri::AppHandle) {
    if let Ok(updater) = app.updater() {
        // 有新版本才弹窗；无网络/已是最新 均静默
        if let Ok(Some(_)) = updater.check().await {
            open_update_window(&app);
        }
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_process::init())
        .setup(|app| {
            let show = MenuItem::with_id(app, "show", "显示主窗口", true, None::<&str>)?;
            let update = MenuItem::with_id(app, "update", "检查更新", true, None::<&str>)?;
            let quit = MenuItem::with_id(app, "quit", "退出 Tempora", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&show, &update, &quit])?;

            TrayIconBuilder::with_id("main")
                .icon(app.default_window_icon().expect("no default icon").clone())
                .tooltip("Tempora")
                .menu(&menu)
                .show_menu_on_left_click(false)
                .on_menu_event(|app, event| match event.id().as_ref() {
                    "show" => show_main(app),
                    "update" => open_update_window(app),
                    "quit" => app.exit(0),
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        let app = tray.app_handle();
                        if let Some(w) = app.get_webview_window("main") {
                            if w.is_visible().unwrap_or(false) {
                                let _ = w.hide();
                            } else {
                                show_main(app);
                            }
                        }
                    }
                })
                .build(app)?;

            // 启动 5 秒后静默检查更新（给内核留启动时间）
            let handle = app.handle().clone();
            std::thread::spawn(move || {
                std::thread::sleep(std::time::Duration::from_secs(5));
                tauri::async_runtime::block_on(silent_check(handle));
            });
            Ok(())
        })
        .on_window_event(|window, event| {
            // 点关闭：主窗口隐藏到托盘；更新窗口直接关闭
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                if window.label() == "main" {
                    api.prevent_close();
                    let _ = window.hide();
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("Tempora shell failed to start");
}
