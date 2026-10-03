// Tempora 轻壳入口。
// 官方 React SPA 只与 127.0.0.1 内核通信，因此壳只负责窗口、托盘、菜单、更新。
// 行为约定：
//   - 点关闭 = 隐藏到托盘（不退出，内核常驻）
//   - 托盘左键 = 显示/隐藏 切换
//   - 托盘右键菜单 = 显示主窗口 / 检查更新 / 退出
//   - 启动 5 秒后静默检查更新，发现新版自动弹出右上角更新窗口
//   - 更新窗口(updater.html)负责下载进度条与安装，endpoint 见 tauri.conf.json
//   - 内核由壳托管：8787 无人监听时按候选路径拉起 tempora.exe，退出时回收
//   - 主窗口先加载壳自带的 boot.html（启动屏），它自己探到 8787 再跳过去，
//     用户永远不会看见内核没起来时 WebView2 的那张「无法访问此网站」
use std::net::{SocketAddr, TcpStream};
use std::path::PathBuf;
use std::process::{Child, Command};
use std::sync::Mutex;
use std::time::{Duration, Instant};
#[cfg(windows)]
use std::os::windows::process::CommandExt;
use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Manager,
};
use tauri_plugin_updater::UpdaterExt;
use rfd::FileDialog;

const KERNEL_PORT: u16 = 8787;

/// 内核进程持有者；托盘退出时回收，避免留下没人管的 tempora.exe
struct Kernel(Mutex<Option<Child>>);

fn port_up(port: u16) -> bool {
    TcpStream::connect_timeout(
        &SocketAddr::from(([127, 0, 0, 1], port)),
        Duration::from_millis(250),
    )
    .is_ok()
}

/// 内核位置候选：环境变量 > 壳同目录 > 壳目录下 frontend-next > 用户安装目录
fn kernel_candidates() -> Vec<PathBuf> {
    let mut v = Vec::new();
    if let Ok(p) = std::env::var("TEMPORA_KERNEL") {
        if !p.trim().is_empty() {
            v.push(PathBuf::from(p.trim()));
        }
    }
    if let Some(dir) = std::env::current_exe().ok().and_then(|p| p.parent().map(PathBuf::from)) {
        v.push(dir.join("tempora.exe"));
        v.push(dir.join("frontend-next").join("tempora.exe"));
    }
    if let Ok(la) = std::env::var("LOCALAPPDATA") {
        let base = PathBuf::from(la);
        v.push(base.join("Tempora").join("tempora.exe"));
        v.push(base.join("Programs").join("Tempora").join("tempora.exe"));
    }
    v.retain(|p| p.exists());
    v
}

/// 拉起内核并等它把 8787 顶起来；没找到内核就给个说清楚的提示窗口
fn ensure_kernel() -> Option<Child> {
    if port_up(KERNEL_PORT) {
        return None; // 已经有一个在跑，别抢
    }
    let path = kernel_candidates().into_iter().next()?;
    // 某些启动路径（运行对话框、安装器完成后重启）会把壳的 cwd 落在
    // C:\Windows\System32，内核会继承它并把默认工作区设在那里 ——
    // 显式指到用户主目录，别让侧栏出现「system32」。
    let cwd = std::env::var("USERPROFILE").ok().map(std::path::PathBuf::from)
        .or_else(|| std::env::current_dir().ok());
    // 内核是 CLI：不带子命令会去跑 TUI 然后退出，必须显式 serve 到 8787
    // 内核若在 8787 顶起来之前就自己退出（配置坏、端口被别的进程占着、二进制损坏），
    // 原来的写法会傻等到 30 秒超时，用户只能对着启动页发呆 —— 这正是「打开像卡死」的
    // 一种真因。这里改为盯着子进程：它提前没了就立刻再试一次（最多两轮），
    // 于是真正慢的机器能吃满 60 秒，而真崩掉的情况几秒内就有第二次机会。
    // 思路参考上游 studio-v2.24.0 #11479（其实现在 desktop/electron/，与 Tauri 无关，
    // 故按同一语义自研，未移植其代码）。
    for attempt in 0..2 {
        let mut cmd = Command::new(&path);
        // 内核是 CLI：不带子命令会去跑 TUI 然后退出，必须显式 serve 到 8787
        cmd.args(["serve", "--addr", "127.0.0.1:8787"])
            .creation_flags(0x0800_0000); // CREATE_NO_WINDOW：内核是控制台程序，别让它弹黑窗
        if let Some(dir) = &cwd {
            let _ = cmd.current_dir(dir);
        }
        let mut child = match cmd.spawn() {
            Ok(c) => c,
            Err(_) => return None,
        };
        let deadline = Instant::now() + Duration::from_secs(30);
        let mut exited_early = false;
        while Instant::now() < deadline {
            if port_up(KERNEL_PORT) {
                return Some(child);
            }
            if let Ok(Some(_)) = child.try_wait() {
                exited_early = true;
                break;
            }
            std::thread::sleep(Duration::from_millis(400));
        }
        if !exited_early {
            // 到点还没起来：交给启动页继续探，不在这里干耗
            return Some(child);
        }
        if attempt == 0 {
            eprintln!("tempora: kernel exited before 8787 came up; retrying once");
        }
    }
    None
}


/// 等内核把 8787 顶起来（最多 limit），返回是否就绪
fn wait_kernel(limit: Duration) -> bool {
    let deadline = Instant::now() + limit;
    while Instant::now() < deadline {
        if port_up(KERNEL_PORT) {
            return true;
        }
        std::thread::sleep(Duration::from_millis(300));
    }
    false
}

/// 主窗口出场。
///
/// 窗口的 url 是壳自带的 boot.html（见 tauri.conf.json），本地资源、不依赖
/// 任何进程，第一帧就画得出来；它在后台探内核端口，通了再 replace 过去。
/// 所以这里不用等内核，越早显示越好 —— 0.1.7 之前窗口 url 直接写着
/// 127.0.0.1:8787，内核还没监听时先渲染出一张 WebView2 的「无法访问此
/// 网站」，等端口就绪再 location.reload() 把它换掉，用户每次启动都能看见
/// 那张错误页闪一下。
fn boot_main_window(app: &tauri::AppHandle) {
    if let Some(w) = app.get_webview_window("main") {
        let _ = w.show();
        let _ = w.unminimize();
        let _ = w.set_focus();
    }
}

fn show_main(app: &tauri::AppHandle) {
    if let Some(w) = app.get_webview_window("main") {
        if !port_up(KERNEL_PORT) {
            // 用户主动唤出但内核不在：先试着救回来
            let owned = ensure_kernel();
            if app.try_state::<Kernel>().is_none() {
                app.manage(Kernel(Mutex::new(owned)));
            }
            wait_kernel(Duration::from_secs(30));
        }
        let _ = w.show();
        let _ = w.unminimize();
        let _ = w.set_focus();
    }
}

/// 托盘图标按当前 DPI 选帧。
/// 之前直接用 default_window_icon()（256x256），CreateIcon 按原尺寸建位图后
/// 系统再缩到 16/24/32 显示——这就是托盘图标发糊的根因。
/// Windows 托盘槽位 = 16 逻辑 px * scale，所以 16*scale 就是要喂的尺寸。
fn tray_icon_for_scale(scale: f64) -> tauri::image::Image<'static> {
    let px = (16.0 * scale).round().clamp(16.0, 64.0) as u32;
    let bytes: &[u8] = match px {
        0..=17 => include_bytes!("../icons/tray/t16.png"),
        18..=21 => include_bytes!("../icons/tray/t20.png"),
        22..=27 => include_bytes!("../icons/tray/t24.png"),
        28..=35 => include_bytes!("../icons/tray/t32.png"),
        36..=43 => include_bytes!("../icons/tray/t40.png"),
        44..=55 => include_bytes!("../icons/tray/t48.png"),
        _ => include_bytes!("../icons/tray/t64.png"),
    };
    tauri::image::Image::from_bytes(bytes).expect("embedded tray png must decode")
}

/// 当前主监视器的 DPI 缩放；取不到就用 1.0
fn app_scale(app: &tauri::AppHandle) -> f64 {
    if let Some(w) = app.get_webview_window("main") {
        if let Ok(s) = w.scale_factor() {
            return s;
        }
    }
    if let Ok(Some(m)) = app.primary_monitor() {
        return m.scale_factor();
    }
    1.0
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
    match tauri::WebviewWindowBuilder::new(
        app,
        "updater",
        tauri::WebviewUrl::App("updater.html".into()),
    )
    .title("Tempora 更新")
    // 必须与主窗口的 additionalBrowserArgs 完全一致：WebView2 的 Environment
    // 按 (user-data-dir, args) 缓存，参数不一致会尝试建第二个 Environment，
    // 而同一 user data folder 不允许并存——第二个窗口创建即死，表现为
    // 「点检查更新没反应」。
    .additional_browser_args(
        "--remote-debugging-port=9333 --disable-features=msWebOOUI,msPdfOOUI,msSmartScreenProtection",
    )
    .inner_size(380.0, 210.0)
    .decorations(false)
    .resizable(false)
    .always_on_top(true)
    .skip_taskbar(true)
    .shadow(true)
    .position(x, y)
    .build()
    {
        Ok(w) => {
            // 创建成功也要留现场：可见性、位置、尺寸，供「窗口没出现」类问题定位
            log_updater(
                app,
                &format!(
                    "diag: updater window built: visible={:?} pos={:?} size={:?} url={:?}",
                    w.is_visible(),
                    w.outer_position(),
                    w.inner_size(),
                    w.url()
                ),
            );
            let _ = w.show();
            let _ = w.unminimize();
            let _ = w.set_focus();
        }
        Err(e) => {
            // 创建失败必须留现场，不能吞掉——「点了没反应」这种问题靠它定位
            log_updater(app, &format!("open update window failed: {e}"));
        }
    }
}

async fn silent_check(app: tauri::AppHandle) {
    if let Ok(updater) = app.updater() {
        // 有新版本才弹窗；无网络/已是最新 均静默。失败写一行日志，
        // 不然「为什么没弹更新」这种问题永远查不到现场。
        match updater.check().await {
            // 自动检查一律不弹窗：实测本机 github.com 被墙、updater.html 又曾加载成
            // about:blank，自动弹窗会变成一个 380x210 的空白无响应窗口，用户表现为
            // 「打开就卡死」。有更新只记日志，改由用户手动点「检查更新」触发弹窗。
            Ok(Some(_)) => log_updater(&app, "update available (auto-check silent, no popup)"),
            Ok(None) => {}
            Err(e) => log_updater(&app, &format!("check failed: {e}")),
        }
    }
}

/// 版本号与更新状态，给左上角品牌区的状态点用。
#[tauri::command]
async fn update_status(app: tauri::AppHandle) -> Result<serde_json::Value, String> {
    let current = app.package_info().version.to_string();
    let mut out = serde_json::json!({ "current": current, "available": false, "latest": null });
    if let Ok(updater) = app.updater() {
        match updater.check().await {
            Ok(Some(u)) => {
                out["available"] = serde_json::Value::Bool(true);
                out["latest"] = serde_json::Value::String(u.version.clone());
            }
            Ok(None) => {}
            Err(e) => log_updater(&app, &format!("status check failed: {e}")),
        }
    }
    Ok(out)
}

/// 触发更新：有新版就直接下载安装，一个窗口都不弹。
/// 这里刻意不走 open_update_window —— 它历史上把 updater.html 加载成
/// about:blank，变成一扇无边框、置顶、没有关闭按钮的空白窗，用户看到的就是
/// 「卡死」。直接装掉，把结果回报给状态点即可。
#[tauri::command]
async fn open_updater(app: tauri::AppHandle) -> Result<serde_json::Value, String> {
    let updater = app.updater().map_err(|e| e.to_string())?;
    match updater.check().await {
        Ok(Some(update)) => {
            let version = update.version.clone();
            update
                .download_and_install(|_chunk: usize, _len: Option<u64>| {}, || {})
                .await
                .map(|()| serde_json::json!({ "updated": true, "version": version }))
                .map_err(|e| e.to_string())
        }
        Ok(None) => Ok(serde_json::json!({ "updated": false, "reason": "up-to-date" })),
        Err(e) => Err(e.to_string()),
    }
}

// 更新检查日志落在 exe 旁，出问题时用户把这一行发来就能定位
fn log_updater(app: &tauri::AppHandle, msg: &str) {
    use std::io::Write;
    let Ok(dir) = app.path().resource_dir().or_else(|_| app.path().executable_dir().map(|p| p.to_path_buf())) else {
        return;
    };
    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);
    if let Ok(mut f) = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(dir.join("updater.log"))
    {
        let _ = writeln!(f, "[{stamp}] {msg}");
    }
}

/// 「添加项目」用的原生文件夹选择对话框。
///
/// 之前前端走内核的 POST /host/pick-folder，对话框由内核进程(tempora.exe)创建——
/// 与可见的 WebView2 窗口分属两个进程，Windows 前台锁让对话框永远卡在窗口背后，
/// 用户看到的就是「点了没反应」。这里让壳自己在 UI 线程上打开对话框，它天然属于
/// 可见窗口，会正常置顶弹出。返回选中目录的绝对路径；用户取消则返回空串。
#[tauri::command]
fn pick_folder(start_in: String) -> String {
    let mut dlg = FileDialog::new().set_title("选择 Tempora Studio 工作区");
    if !start_in.is_empty() {
        dlg = dlg.set_directory(std::path::Path::new(&start_in));
    }
    match dlg.pick_folder() {
        Some(p) => p.to_string_lossy().into_owned(),
        None => String::new(),
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_process::init())
        .invoke_handler(tauri::generate_handler![pick_folder, update_status, open_updater])
        .setup(|app| {
            let show = MenuItem::with_id(app, "show", "显示主窗口", true, None::<&str>)?;
            let update = MenuItem::with_id(app, "update", "检查更新", true, None::<&str>)?;
            let quit = MenuItem::with_id(app, "quit", "退出 Tempora", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&show, &update, &quit])?;

            // 主窗口先出场：它加载的是壳自带的启动页（本地资源，秒开），
            // 内核在它后面拉。顺序反过来的话，用户要先盯着一片空白等内核。
            let handle = app.handle().clone();
            let loop_handle = handle.clone();
            boot_main_window(&handle);

            // 内核托管：8787 无人监听就拉起内核，否则用户看到的永远是一张白窗
            let owned = ensure_kernel();
            app.manage(Kernel(Mutex::new(owned)));

            TrayIconBuilder::with_id("main")
                .icon(tray_icon_for_scale(app_scale(&handle)))
                .tooltip("Tempora")
                .menu(&menu)
                .show_menu_on_left_click(false)
                .on_menu_event(|app, event| match event.id().as_ref() {
                    "show" => show_main(app),
                    "update" => open_update_window(app),
                    "quit" => {
                        // 退出时把托管的内核一起收掉，别留一个没人管的后台进程
                        if let Some(k) = app.try_state::<Kernel>() {
                            if let Ok(mut g) = k.0.lock() {
                                if let Some(mut c) = g.take() {
                                    let _ = c.kill();
                                }
                            }
                        }
                        app.exit(0);
                    }
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

            // 循环检查更新：应用常年藏在托盘不退出，只在启动时查一次的话，
            // 发新版永远追不上藏在托盘里的旧实例。首查 5 秒，之后每 2 小时一轮。
            std::thread::spawn(move || {
                std::thread::sleep(std::time::Duration::from_secs(5));
                loop {
                    tauri::async_runtime::block_on(silent_check(loop_handle.clone()));
                    std::thread::sleep(std::time::Duration::from_secs(2 * 60 * 60));
                }
            });

            // 内核存活保活：壳只在启动时拉一次内核，若内核中途崩溃，UI 会永远卡在
            // 「连接内核」。这里加常驻探活线程，端口不通就自动重拉并接管进程句柄，
            // 用户再也不会遇到打开软件卡死的情况（也不用手动去点托盘「显示主窗口」）。
            {
                let wh = handle.clone();
                std::thread::spawn(move || {
                    loop {
                        std::thread::sleep(std::time::Duration::from_secs(5));
                        if !port_up(KERNEL_PORT) {
                            if let Some(k) = wh.try_state::<Kernel>() {
                                if let Ok(mut g) = k.0.lock() {
                                    if let Some(mut old) = g.take() {
                                        let _ = old.kill();
                                    }
                                    *g = ensure_kernel();
                                }
                            }
                        }
                    }
                });
            }

            Ok(())
        })
        .on_window_event(|window, event| {
            // 更新窗口的生死留下记录；主窗口的日常焦点抖动不写
            if window.label() == "updater" {
                match event {
                    tauri::WindowEvent::CloseRequested { .. } | tauri::WindowEvent::Destroyed => {
                        log_updater(window.app_handle(), &format!("updater window {event:?}"));
                    }
                    _ => {}
                }
            }
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
