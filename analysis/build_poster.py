"""Build an editable, data-backed A0 draft. Render with Chromium, inspect PDF.

No conference acceptance, authorship, institution or ethics approval is invented.
"""
from pathlib import Path
import json, os
from reportlab.graphics import renderSVG
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget

root=Path(__file__).resolve().parents[1]
out=root/"poster";out.mkdir(parents=True,exist_ok=True)
result=json.loads((root/"research/results.json").read_text())
cv=result["models"]["ridge_orientation"];t=result["temporal"]["ridge_orientation"]
axis=result["inference"]["KS_axis_improvement"]
follow=result["longitudinal"]["six_month_comparison"]
widget=QrCodeWidget("https://calculator.evo-icl.cn",barLevel="M")
bounds=widget.getBounds();size=150
drawing=Drawing(size,size,transform=[size/(bounds[2]-bounds[0]),0,0,size/(bounds[3]-bounds[1]),0,0]);drawing.add(widget)
(root/"assets/site-qr.svg").write_text(renderSVG.drawToString(drawing))

html=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ICL 壁报草稿 · A0</title>
<style>
@page{{size:841mm 1189mm;margin:0}}*{{box-sizing:border-box}}html,body{{margin:0;background:#e6edf3;color:#19354f}}body{{font-family:"PosterSans","PingFang SC","Microsoft YaHei",sans-serif}}@font-face{{font-family:PosterSans;src:url('./poster-font.ttf') format('truetype');font-weight:100 900;font-display:block}}
.poster{{width:841mm;height:1189mm;background:#fff;padding:26mm;display:grid;grid-template-rows:184mm 86mm 1fr 118mm 43mm;gap:13mm;overflow:hidden;margin:0 auto}}
.header{{background:#10283f;color:#fff;padding:25mm 23mm;display:flex;justify-content:space-between;gap:30mm;align-items:flex-start}}.kicker{{font-size:32px;letter-spacing:4px;color:#8ecdd4;margin-bottom:10mm}}h1{{font-size:102px;line-height:1.22;letter-spacing:-2px;margin:0 0 11mm;font-weight:680}}.subtitle{{font-size:41px;color:#b9d0e0;margin-bottom:11mm}}.author{{font-size:34px;color:#91b1c8}}.draft{{font-size:27px;border:1px solid #507089;padding:4mm 6mm;white-space:nowrap;color:#c3d6e4}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:16mm;align-items:center}}.metric{{border-right:1px solid #dbe6ef}}.metric:last-child{{border:0}}.metric b{{display:block;font-size:154px;font-weight:620;letter-spacing:-4px;line-height:1.1}}.metric b small{{font-size:45px;color:#8298a9;letter-spacing:0}}.metric span{{font-size:34px;display:block;color:#6d8497;margin-top:4mm}}.metric em{{display:block;font-size:27px;color:#7f93a4;font-style:normal;margin-top:2mm}}
.body-grid{{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:198mm 224mm 198mm;gap:15mm 18mm}}.block{{border:1px solid #d9e5ef;padding:14mm 14mm 11mm;border-radius:6mm;overflow:hidden}}h2{{font-size:45px;font-weight:650;line-height:1.25;margin:0 0 9mm;display:flex;align-items:center;gap:6mm}}.section-mark{{display:inline-block;width:4mm;height:11mm;background:#0d8b84}}p{{font-size:36px;line-height:1.8;margin:0 0 7mm}}.caption{{font-size:29px;line-height:1.65;color:#688198;margin:4mm 0 0}}.figure{{width:91%;display:block;margin:2mm auto 0}}.main-figure{{width:95%}}.flow{{display:grid;grid-template-columns:repeat(3,1fr);gap:6mm;margin:9mm 0}}.flow>div{{background:#f1f6fa;padding:7mm 5mm;border-radius:4mm;font-size:30px;line-height:1.7}}.flow b{{display:block;font-size:40px;color:#176bbd}}.flow small{{font-size:25px;color:#70869a}}.takeaway{{background:#eef8f5;border-left:3mm solid #0d8b84;padding:8mm 9mm;font-size:33px;line-height:1.75;margin-top:7mm}}.warning{{background:#fff7e9;border-left:3mm solid #a76920;padding:7mm 9mm;font-size:32px;line-height:1.75;margin-top:7mm}}.findings{{display:grid;gap:7mm}}.findings b{{font-size:41px;font-weight:650;display:block}}.findings p{{font-size:32px;color:#688198;margin:2mm 0 0}}.section-label{{font-size:27px;letter-spacing:3px;color:#176bbd;margin-bottom:4mm}}
.conclusion{{background:#10283f;color:#fff;padding:16mm 19mm;display:grid;grid-template-columns:1.5fr 1fr;gap:22mm;align-items:start}}.conclusion h2{{font-size:48px;margin-bottom:5mm}}.conclusion p{{font-size:36px;line-height:1.65;color:#d4e2ec;margin:0}}.conclusion .limitations{{font-size:29px;color:#a2bfce;line-height:1.8}}.footer{{display:flex;justify-content:space-between;gap:16mm;align-items:center;border-top:1px solid #dbe6ef;padding-top:7mm}}.footer p{{font-size:24px;color:#7d91a3;line-height:1.7;margin:0}}.qr{{display:flex;align-items:center;gap:6mm;flex:none}}.qr img{{width:32mm;height:32mm}}.qr span{{font-size:25px;color:#688198;line-height:1.7}}.screen-tools{{padding:15px;font:14px sans-serif;text-align:center;background:#10283f;color:#fff}}.screen-tools button{{margin-left:15px;padding:8px 20px;cursor:pointer}}@media print{{.screen-tools{{display:none}}body{{background:#fff}}.poster{{margin:0}}}}
</style></head><body><div class="screen-tools">研究方审阅稿 · A0 841 × 1189 mm · 会议尺寸、作者、机构与伦理信息待补<button onclick="window.print()">打印 / PDF</button></div>
<article class="poster">
<header class="header"><div><div class="kicker">EVO ICL · REPRODUCIBLE OPHTHALMIC RESEARCH</div><h1>ICL 术后拱高：<br>从术前预测到随访更新</h1><div class="subtitle">患者分组验证、植入轴匹配与时间泛化的回顾性研究</div><div class="author">作者与医院单位待研究方确认　｜　伦理批准与数据授权待确认</div></div><div class="draft">壁报草稿<br>2026.10.14</div></header>
<div class="metrics"><div class="metric"><b>399<small> 眼</small></b><span>201 名患者记录</span><em>原始登记队列</em></div><div class="metric"><b>{cv['mae']:.0f}<small> μm</small></b><span>1 月模型内部 CV MAE</span><em>341 眼 / 173 人</em></div><div class="metric"><b>{t['mae']:.0f}<small> μm</small></b><span>2025 年时间测试 MAE</span><em>29 眼 / 15 人</em></div><div class="metric"><b>{follow['plus_observed_month1']['mae']:.0f}<small> μm</small></b><span>实测 1 月 → 6 月 MAE</span><em>281 眼内部验证</em></div></div>
<div class="body-grid">
<section class="block"><h2><span class="section-mark"></span>研究问题与方法</h2><p>复核原始数据并优化术后 1 个月拱高预测；量化植入轴匹配的误差改善，探索实测随访的增量信息。</p><div class="flow"><div><b>379 眼</b>有 1 月终点<br><small>370 眼参数完整</small></div><div><b>341 眼</b>2022–2024 开发<br><small>内 4 / 外 5 折，重复 3 次</small></div><div><b>29 眼</b>2025 时间测试<br><small>模型选择完成后评分</small></div></div><p class="caption">同一患者双眼始终同组。异常 STS/LT 有明确规则；缺失柱镜不填 0。11 个候选模型在同一开发队列比较。</p></section>
<section class="block"><h2><span class="section-mark"></span>解剖与轴向匹配</h2><div class="findings"><div><b>垂直沟径比水平大 0.45 mm</b><p>患者聚类 95% CI 0.42–0.48 mm；398 眼。</p></div><div><b>轴向匹配降低 MAE {axis['mae_reduction']:.1f} μm</b><p>95% CI {axis['ci95'][0]:.1f}–{axis['ci95'][1]:.1f} μm；同批 394 眼。</p></div></div><div class="takeaway">改善来自更准确的输入轴匹配，而不是单纯增加算法复杂度。</div><p class="caption">未测 ATA：比较的是以 STS 代入的改写 KS 实现；不等同于原 KS 公式验证。方位关联不证明旋转的因果效果。</p></section>
<section class="block"><h2><span class="section-mark"></span>术前模型：透明方法更稳健</h2><img class="figure main-figure" src="../research/figures/poster_model.svg" alt="候选模型患者分组验证 MAE"><p class="caption">6 变量 Ridge：ACD、ICL 尺寸、Toric、LT、轴向 STS 与 sin²θ 联合拟合。CV R²={cv['r2']:.3f}。条形上的区间为患者聚类 bootstrap 95% CI。</p></section>
<section class="block"><h2><span class="section-mark"></span>区间：跨年份覆盖会变化</h2><img class="figure" src="../research/figures/poster_coverage.svg" alt="内部验证与2025时间测试预测区间覆盖"><div class="warning">80% 标称区间在时间测试仅覆盖 {t['coverage80']*100:.1f}%；95% 区间覆盖 {t['coverage95']*100:.1f}%。默认展示 95%，仍需独立中心校准。</div></section>
<section class="block"><h2><span class="section-mark"></span>从术前模型走向随访模型</h2><img class="figure" src="../research/figures/poster_followup.svg" alt="相同281眼中6个月预测的误差比较"><p class="caption">同一批 281 眼 / 142 人；患者分组嵌套 5 折。加入实测 1 个月拱高后 R²={follow['plus_observed_month1']['r2']:.3f}，MAE {follow['plus_observed_month1']['mae']:.1f} μm；属于术后预测。</p></section>
<section class="block"><h2><span class="section-mark"></span>结论边界与后续研究</h2><p>保留可复现的轴匹配发现和患者分组验证；将未稳健复现的“尺寸×方位”交互降级为探索性。</p><p>随访信息有更高预测价值，但当前仅研究解剖终点。下一步需明确视力量表，并加入真实视觉功能与安全结局。</p><div class="takeaway">研究原型与开放代码用于科学讨论；不自动选择 ICL 尺寸或方位。</div></section>
</div>
<section class="conclusion"><div><h2>核心结论</h2><p>轴向匹配与透明建模改善内部预测；跨年份泛化和区间覆盖必须单独验证。实测随访信息值得作为下一步主线。</p></div><div class="limitations">单中心回顾性研究；时间测试仅 15 人；CLR/STSL 未测；记录角度的光学轴/物理长轴对应关系待术者确认；无独立中心验证；未证明视觉康复获益。</div></section>
<footer class="footer"><p>参考：ESCRS 2025 PO1048（DOI:10.82333/92y3-r013）；ASCRS 2025 electronic poster 107137；TRIPOD+AI（BMJ 2024;385:e078378）。<br>图表与数字由 2026-10-13 原表重算生成。科研数据保留本地，仅公开代码、模型与汇总。<br>通用 A0 审阅稿，尚未按江苏目标会议通知定稿或提交。</p><div class="qr"><img src="../assets/site-qr.svg" alt="研究网站二维码"><span>模型、代码与证据<br>calculator.evo-icl.cn</span></div></footer>
</article></body></html>'''
(out/"poster.html").write_text(html)
# Subset a pre-existing, OFL-licensed Noto font for portable Chinese rendering.
font=Path(os.environ.get("POSTER_FONT", ""))
if font.is_file():
    from fontTools.ttLib import TTFont
    from fontTools import subset
    face=TTFont(font)
    options=subset.Options()
    sub=subset.Subsetter(options=options);sub.populate(text=html);sub.subset(face)
    face.flavor=None;face.save(out/"poster-font.ttf")
    # The complete OFL notice is separately distributed beside the subset.
print("Editable poster and public website QR generated.")
