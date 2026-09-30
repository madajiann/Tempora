# -*- coding: utf-8 -*-
"""生成壳内置的启动页 app/frontend/public/boot.html。

## 为什么需要它（0.1.8）

主窗口的 url 之前直接写着内核地址 `http://127.0.0.1:8787/`。内核是壳自己
在 setup 里拉起来的，窗口创建时它还没开始监听，WebView2 就先渲染出一张
「无法访问此网站」的错误页；等端口就绪，壳再 `location.reload()` 把它换掉。
结果是用户每次启动都能看见那张错误页闪一下（实测约 1 秒）。

错误页是 WebView2 在内核不可达时的产物，页面里的 JS 根本不会执行，
所以只能在**初始 url** 上解决：换成本文件生成的 boot.html —— 壳自带的
内嵌资源，不依赖任何进程，第一帧就能画出来。页面与内核 index.html 的
启动屏同款（夜空 + Tempora wordmark），并在后台探测内核端口，通了再
`location.replace()` 到内核页，视觉上完全连续。

## 为什么不手抄一份 boot 屏

boot 屏的 markup、样式、主题预判脚本全部从 index.html 抽取，不手写。
两处各存一份必然漂移（改了 index.html 忘了改 boot.html，启动时就会
从金 T 突变到另一个金 T）。这个脚本每次构建前重跑一次即可。

用法：
    python scripts/make_boot_page.py
"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "app", "frontend", "index.html")
OUT = os.path.join(ROOT, "app", "frontend", "public", "boot.html")

# boot.html 与内核页的启动屏是同一个东西的两个瞬间，所以这里**不翻转**
# index.html 的初始态，只补它等不到的那点 JS：
#   .bmark .bl     保持 opacity:0。内核页首帧也藏着字母，由 src/boot/intro.ts
#                  让它们出场；这里若先摆出来，跳过去就会看见 wordmark 消失
#                  一次再重放。3.2s 的 bootfallback 兜底留着 —— 内核起得慢时
#                  它正好把品牌亮出来，那本来就是这个动画的用途。
#   .bline         默认 opacity:0（要 .boot[data-slow] 才显），这里要显：
#                  「正在连接内核…」是这个页面唯一能给的交代。
#   .bsteps        默认 opacity:0（要 .boot[data-wait] 才显），同理要显，
#                  并在 REDIRECT_JS 里给第一个点打上 data-now 让它呼吸。
#   canvas.bfx     流星由 sky.ts 画，这里没有那位 JS，收掉免得留个空层。
PATCH_CSS = (
    "\n"
    "      /* boot.html 专用覆盖，由 scripts/make_boot_page.py 注入：\n"
    "         字母保持隐藏（与内核页首帧一致，出场交给 intro.ts），\n"
    "         提示行与步进点要显出来 —— 它们是这个页面上唯一在动的东西。 */\n"
    "      .bline { opacity: .8 }\n"
    "      .bsteps { opacity: 1 }\n"
    "      .bfx { display: none }\n"
    "    "
)

REDIRECT_JS = """  <script>
    // 内核由壳在后台拉起，端口通了才走。这里只做两件事：
    //   1) 探到 127.0.0.1:8787 有响应就 replace 过去（replace 不压历史，
    //      用户按后退不该退回启动屏再被弹一次）
    //   2) 长时间探不到就把提示行换成一句说人话的，而不是一直演动画
    // 探测用 no-cors：跨 origin 读不到 response，但「内核答上了」会
    // resolve、「连不上」会 reject —— 这正是要区分的那两件事。用 res.ok
    // 判断是错的，opaque response 的 status 恒为 0。
    (function () {
      var KERNEL = "http://127.0.0.1:8787/";
      var SLOW_MS = 12000;
      var started = Date.now();
      var moved = false;
      var warned = false;
      var line = document.querySelector(".bline");
      // 步进点的第一个点常亮呼吸 —— 内核页在等内核时就是这个样子
      // （.boot[data-wait]），这里手工打上，免得等待期间屏幕上没有动静。
      var step = document.querySelector(".bsteps i");
      if (step) step.setAttribute("data-now", "");

      function go() {
        if (moved) return;
        moved = true;
        location.replace(KERNEL);
      }

      function warn() {
        if (warned || !line) return;
        warned = true;
        line.innerHTML = "<span>内核没有起来 —— 安装可能不完整，重新安装 Tempora 即可修复。</span>";
      }

      function probe() {
        if (moved) return;
        fetch(KERNEL, { mode: "no-cors", cache: "no-store" }).then(go, function () {
          if (Date.now() - started > SLOW_MS) warn();
          window.setTimeout(probe, warned ? 800 : 150);
        });
      }

      probe();
    })();
  </script>
"""


def main():
    with io.open(SRC, encoding="utf-8") as f:
        html = f.read()

    # head：doctype / html / head 全部照搬（里面那两段内联脚本负责在首帧前
    # 定下主题与语言，正是启动屏需要的），只改标题并把覆盖样式插在 </style> 前。
    head = html[: html.index("</head>")]
    head = head.replace("<title>Tempora Studio</title>", "<title>Tempora</title>")
    style_end = head.rindex("</style>")
    head = head[:style_end] + PATCH_CSS + head[style_end:]
    head = head.replace("<!doctype html>", "<!doctype html>\n<!-- 由 scripts/make_boot_page.py 生成，勿手改；源是 app/frontend/index.html 的启动屏 -->", 1)

    # body：只要启动屏那一个块。它后面紧跟的 <div id="root"> 是 SPA 挂载点，
    # 启动页不需要 React。
    boot = html[html.index('<div id="boot"') : html.index('<div id="root">')].rstrip()

    page = head + "\n  </head>\n  <body>\n" + boot + "\n" + REDIRECT_JS + "  </body>\n</html>\n"

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    print("已生成 %s (%d bytes)" % (OUT, len(page.encode("utf-8"))))


if __name__ == "__main__":
    main()
