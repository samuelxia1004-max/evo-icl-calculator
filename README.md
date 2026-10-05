# EVO ICL 术后拱高计算器 / EVO ICL vault calculator

公开研究版 v1.0 · Public research release v1.0

在线打开：[https://calculator.evo-icl.cn](https://calculator.evo-icl.cn)

> **免责声明。** 本工具是研究原型，供阅读、教学和科研讨论。它没有经过临床验证，不是医疗器械，不构成医疗建议，也不会自动选择 ICL 尺寸或植入方位。预测带有很大的个体不确定度。是否手术、用哪一档尺寸、植入角度，由手术医生结合完整术前检查决定。
>
> **Disclaimer.** This tool is a research prototype for reading, teaching, and scientific discussion. It is not clinically validated, it is not a medical device, it is not medical advice, and it does not select an ICL size or orientation. Predictions carry large individual uncertainty. The operating surgeon decides whether to operate, which size to use, and at what angle, after a complete preoperative examination.

页面内的模型版本号是 `2.0.2 (1-month, locked coef + orient adj)`（构建日期 2026-07-15）。仓库的 **v1.0** 是这次面向公开阅读的文档与许可发布，计算系数和预测逻辑没有改动。

The in-page model label is `2.0.2 (1-month, locked coef + orient adj)` (build date 2026-07-15). Repository **v1.0** is this public documentation and licensing release. The coefficients and the prediction logic are unchanged.

---

## 中文

### 这个工具做什么

ICL（Implantable Collamer Lens，有晶状体眼后房型人工晶状体）植入后，晶状体与自身晶体之间会留下一段间隙，称为**拱高（vault）**，单位是微米（μm）。拱高过低或过高都是临床关心的问题。本仓库是一个**单页 HTML 计算器**（`index.html`）：在浏览器里输入术前测量和拟用的 ICL 参数，估计**术后 1 个月拱高**，并给出区间、一个目标区概率、可靠性分级，以及只作提示、不改预测的安全注意。

全部预测在浏览器内完成。内置队列是去标识化的数值，用于页面上的“科研验证”和样本内区间；打开页面不会把这些数值或用户输入上传到本项目的服务器。OCR 与 PDF 首次使用时会从公共 CDN 下载运行文件。

页面有中英切换。主要分页：预测、决策支持、随访、识别（OCR）、科研验证、报告、设置 / 自检。

### 怎么打开

GitHub Pages 已对本仓库启用：从 `main` 分支的根目录发布，自定义域名为 `calculator.evo-icl.cn`（见仓库根目录的 `CNAME`）。证书状态为已批准。请使用：

**[https://calculator.evo-icl.cn](https://calculator.evo-icl.cn)**

`https://samuelxia1004-max.github.io/evo-icl-calculator/` 会跳转到上述自定义域名。Pages 当前没有强制 HTTPS，所以 `http://` 也能打开；阅读和演示时用上面的 `https://` 地址。

在本机打开：克隆仓库后，用浏览器直接打开 `index.html`（无需构建步骤）。

```bash
git clone https://github.com/samuelxia1004-max/evo-icl-calculator.git
# 用浏览器打开该目录中的 index.html
```

使用时：

1. 确认 **ACD** 是内前房深度（角膜内皮到晶状体前表面，internal / true ACD）。国家卫健委 2.80 mm 与 FDA 3.00 mm 都按这个定义理解。
2. 填写晶状体厚度 LT、水平/垂直沟径 STS-H / STS-V。没有 UBM 沟径时，可改用 WTW 回退（回退会进入预测，并在可靠性等级里被标出）。
3. 选择 ICL 尺寸（12.1 / 12.6 / 13.2 / 13.7 mm）、是否散光型（Toric）、植入方位角 θ（0° 为水平，90° 为垂直）。
4. 阅读结果时同时看三行：锁定模型点预测、方位修正 Δθ、二者之和。旁边还有正态或经验区间、bootstrap 系数带、安全提示，以及 Zhu 2021 已发表公式的对照值（对照值不进入主预测）。
5. 目标区默认 250–750 μm，也可改为 400–600 μm 或自定义。三类概率（低 / 理想 / 高）仍按 250 与 750 μm 划分。
6. 自检：打开「设置 / 自检」，点击「运行全部自检」。页面会写出通过条数。本发布没有改这些测试，也没有改预测代码。

超出下列范围的输入会被视为单位或小数点错误，预测停止：ACD 2.3–4.5、LT 2.5–5.5、STS 9.5–14.5、WTW 9.5–14.0 mm，方位 0–180°。

### 模型与锁定系数

主终点是术后 1 个月拱高（μm）。默认预测使用下列**锁定系数**。系数存在 `index.html` 的 `EMBED.coef` 与 `VERT_COEF` 中；界面显示到两位小数。v1.0 没有改这些数，也没有改用下面的样本内重拟合。

显示形式：

```text
Vault_1m (μm) = −959.81 + 198.85×ACD + 189.40×ICL尺寸 + 45.99×Toric − 114.99×STS_eff − 99.38×LT + Δθ
Δθ = −58.99 × sin²θ
STS_eff = 1 / √(cos²θ / STS-H² + sin²θ / STS-V²)     θ：水平 = 0°，垂直 = 90°
WTW 回退：STS-H ≈ 2.627 + 0.789×WTW；STS-V ≈ 2.780 + 0.815×WTW
```

代码中的全精度锁定值为：截距 −959.8149，ACD 198.8547，尺寸 189.3997，Toric 45.9887，STS_eff −114.9899，LT −99.3845，方位系数 −58.9862。WTW 回退在代码中是 STS-H = 2.6272317706 + 0.7887754050×WTW，STS-V = 2.7803584299 + 0.8145421548×WTW。

变量单位：ACD、LT、STS、WTW、ICL 尺寸为毫米；Toric 为 0 或 1；拱高为微米。Δθ 加在锁定预测之上，不替换锁定系数。θ = 0° 或 180° 时 Δθ = 0；θ = 90° 时 Δθ = −58.99 μm；中间角度按 sin²θ 连续变化。界面分开显示锁定预测和这一加项。

方位系数来自计算器源码中的记录：在可计算的 1 个月拱高眼上，对锁定模型残差（实测 − 锁定预测）按眼做 sin²θ 的普通最小二乘。源码记录水平眼平均残差 +24.073 μm、垂直眼 −34.913 μm，系数 −58.986 μm（显示 −58.99，存储 −58.9862）。队列里有记录的方位只有 0° 和 90°，因此 sin²θ 在这些眼上相当于垂直指示变量。把全部斜率与 sin²θ 一起重拟合得到 −56.59 μm，**未采用**。按患者等权的敏感分析约为 −46.9 μm，也未采用。该系数只抹平本嵌入数据里垂直相对水平的样本内均值差，并保留了水平眼上约 +24 μm 的共同偏移。它需要外部验证，源码没有把它写成已经确认的临床效应量。Ouchi 2025 报告同一患者中垂直固定较水平约低 150 μm，页面只把它作为另一条文献提示。

同一文件里还存有一组样本内 OLS 重拟合系数（`EMBED.betaRefit`）：截距 −995.6236，ACD 201.2389，尺寸 270.5329，Toric 38.3079，STS_eff −195.887，LT −108.2903。作者决定默认仍用锁定系数。页面模型卡写明：锁定系数来自哪一个拟合队列，仍需作者另行说明；本仓库没有另附那份拟合说明。

不确定度（不改变点预测公式）：

- 正态区间的可选 σ 为 151 μm（内部）或 192 μm（保守）。嵌入对象里的残差标准差 `EMBED.sd1` 是 144.25 μm。
- 经验区间使用锁定模型在内置可计算眼上的**样本内**残差分位数，没有按方位修正重新估计。
- 系数带来自 300 次患者级 bootstrap：抽样围绕重拟合系数，显示时把偏差平移到锁定点预测上，再叠加同一个 Δθ。
- 可靠性等级 A–D 综合队列范围、Mahalanobis 距离、WTW 回退和缺失。
- 另有一个早期（第 1 天）拱高 >750 μm 的 logistic 交叉提示。它是另一个终点，页面标注 AUROC 约 0.81，只供参考。

### 交叉参考（不进入主预测）

Zhu 等，BMC Ophthalmology 2021;21:199（UBM 沟径 + LT，水平植入，ICL V4c，Pentacam 1 个月拱高），系数按发表值固定：

```text
Vault (μm) = −1369.05 + 657.121×ICL尺寸 − 287.408×STS-H − 432.497×LT − 137.33×STS-V
```

非水平植入时页面会标明该公式不适用。「科研验证 → 模型对照」给出它在内置数据水平眼上的外部表现。NK（Nakamura）与 KS（Igarashi/Shimizu）公式依赖 CASIA2 的 ACW/CLR/ATA，本工具没有这些输入，因此没有加入。

### 安全提示（只提示，不改变预测）

| 规则 | 来源 |
| --- | --- |
| ACD < 2.80 mm（内皮起算）：低于一般要求，需综合评估并充分知情同意 | 国家卫健委《有晶状体眼后房型人工晶状体植入术操作规范（2024年版）》 |
| ACD < 3.00 mm：录入值按内皮起算的 true ACD 理解，FDA 禁忌直接适用 | FDA EVO/EVO+ Visian ICL 标签 P030016/S035（2022） |
| 内皮计数 < 2000/mm² | 国家卫健委 2024 规范 |
| 填写年龄与内皮计数时，按年龄/ACD 的最低 ECD | FDA EVO 标签 Table 3 |
| 年龄 < 18（卫健委）；超出 21–45（FDA 适应证） | 同上两份文件 |
| 接近垂直植入时显示 Δθ，并提示 Ouchi 2025 中垂直较水平约低 150 μm | 本工具源码中的残差拟合；Ouchi M. Sci Rep 2025 |

### 数据从哪里来，文件里实际有什么

计算器把这一系列描述为**单中心回顾性**队列。本仓库没有写出医院或机构名称。嵌入数据在应用中被描述为去标识化研究数据：匿名编号、临床数值、年份、眼别、年龄和性别；页面说明其中没有姓名、电话或身份证号。

眼别记录在 `index.html` 的 `DATASET` 数组里。下面的数目是直接数这个数组和旁边的 `EMBED` 对象得到的，不是对稿件措辞的推测。

`DATASET` 共 **399** 条眼记录，编号 `C001`–`C399`。字段为：`pg`、`year`、`eye`、`age`、`sex`、`acd`、`lt`、`stsh`、`stsv`、`wtw`、`size`、`cyl`、`toric`、`orient`、`vEarly`、`v1m`、`v3m`、`v6m`、`id`。

应用把 `pg` 当作患者簇（患者级 bootstrap 将同一 `pg` 的双眼一起重抽样）。同一 `pg` 内年份、年龄、性别一致。共 **201** 个 `pg`：198 个同时有右眼（OD）和左眼（OS），3 个只有 OS。性别标记为女 148 人（294 眼）、男 53 人（105 眼）。年龄 17–48 岁。登记年份：2022 年 54 眼（27 个 `pg`），2023 年 152 眼（76），2024 年 157 眼（80），2025 年 36 眼（18）。有记录的植入方位只有 0° 或 90°；3 条记录的方位为空，代码在计算时把空方位当作 0°。

各随访字段的非空条数：

| 字段 | 非空条数 | 所在 `pg` 数 |
| --- | ---: | ---: |
| 早期拱高 `vEarly` | 397 | 200 |
| 1 个月拱高 `v1m` | 379 | 191 |
| 3 个月拱高 `v3m` | 330 | — |
| 6 个月拱高 `v6m` | 304 | — |
| 同时有 `vEarly` 和 `v1m` | 377 | 190 |
| 有 `v1m` 且有晶状体厚度 `lt` | 373 | — |

没有早期拱高的是同一个 `pg` 的两只眼（2023 年）；这两只眼有 1 个月拱高。因此「有早期拱高」比全表少 2 眼、少 1 个 `pg`。379 条有 1 个月拱高的记录里，6 条缺少 `lt`；缺少 `lt` 时计算器拒绝给出预测，所以能被当前公式评分的 1 个月记录是 373 条。`EMBED.nfit`、`EMBED.n1` 和残差数组 `resid1m` 的长度都是 373。`EMBED.ratios.n` 是 377，与「同时有早期拱高和 1 个月拱高」的条数相同。这 373 条里，方位记录为 0° 的 249 条、90° 的 121 条、缺失的 3 条；缺失按 0° 计入后，是源码注释里的水平 252、垂直 121。

设置页的「内置队列」显示 `DATASET.length`，即 **399** 眼。模型卡和「内置 373 眼」的验证提示显示的是可评分的 1 个月子集。两个数字指的不是同一个分母。

**稿件口径需要统一。** 背景说明写的是 **377 眼**。一份稿件写的是 **200 例患者 / 397 眼**。这两个说法都不是上面的全表（399 眼、201 个 `pg`）。本文件里与这两个数字相同的子集是：377 条记录同时有早期拱高和 1 个月拱高，且 `EMBED.ratios.n` 也是 377；397 条有早期拱高的记录落在 200 个 `pg` 中。373 是另外一个数：有 1 个月拱高且有 `lt`、因而能被当前公式评分，页面上的 `nfit` 用的就是它。数值相同只说明文件里存在这些子集，并不能单独证明稿件那句话指的就是该子集。作者应在稿件里写明每一个数目对应哪一个终点、哪一个缺失规则。在那之前，不要把 377、397 或 373 互相替换。

### 验证状态

这是**研究原型**。页面上用内置队列算出的 MAE、R²、覆盖率和校准，是开发数据上的**表观（样本内）**性能，会偏乐观。它不是独立外部验证，不是前瞻性临床验证，也没有证明换一家医院后仍然适用。跨中心使用前需要外部验证和本地再校准。方位修正同样需要外部验证：修正后水平眼与垂直眼的样本内均值靠近，是因为系数就是用这个差值拟合的。

Zhu 2021 公式的系数来自另一篇已发表研究，在本嵌入数据的水平眼上属于外部对照；它与在同一批数据上拟合的模型不是对等比较。

### 参考文献

1. 国家卫生健康委. 有晶状体眼后房型人工晶状体植入术操作规范（2024年版）. https://www.nhc.gov.cn/yzygj/c100068/202412/72d6714239dd440291623eab397819dc/files/1736385429410_38008.pdf
2. FDA. EVO/EVO+ Visian ICL, PMA P030016/S035, Professional Use Information (2022). https://www.accessdata.fda.gov/cdrh_docs/pdf3/P030016S035C.pdf
3. Zhu QJ, Chen WJ, Zhu WJ, et al. Short-term changes in and preoperative factors affecting vaulting after posterior chamber phakic Implantable Collamer Lens implantation. BMC Ophthalmol. 2021;21:199. https://pubmed.ncbi.nlm.nih.gov/33957891/
4. Zhu QJ, Xing XY, Zhu MH, Ma L. Validation of the vault prediction model based on the sulcus-to-sulcus diameter and lens thickness: a 925-eye prospective study. BMC Ophthalmol. 2022. https://doi.org/10.1186/s12886-022-02698-z
5. Ouchi M. Vault of the phakic intraocular lens during vertical and horizontal fixation within patient comparison. Sci Rep. 2025. https://www.nature.com/articles/s41598-025-95077-9
6. Li X, Lin H, et al. EVO-ICL vault prediction: a data wrangling framework integrating multicenter big data and machine learning. Ophthalmol Ther. 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12882899/
7. Shen Y, Wang L, Jian W, et al. Big-data and artificial-intelligence-assisted vault prediction and EVO-ICL size selection for myopia correction. Br J Ophthalmol. 2023;107:201–206. https://pmc.ncbi.nlm.nih.gov/articles/PMC9887372/
8. Packer M. Meta-analysis and review: effectiveness, safety, and central port design of the intraocular collamer lens. Clin Ophthalmol. 2016;10:1059–1077. https://doi.org/10.2147/OPTH.S111620

第 6、7 条是其他已发表的拱高预测工作，供背景阅读。它们的系数没有进入本计算器。

### 如何引用

规范的软件元数据在 [`CITATION.cff`](CITATION.cff)。建议写法：

> Xia S. EVO ICL postoperative vault calculator. Version 1.0.0. 2026. https://github.com/samuelxia1004-max/evo-icl-calculator

```bibtex
@software{xia2026evoicl,
  author  = {Xia, Samuel},
  title   = {EVO ICL postoperative vault calculator},
  year    = {2026},
  version = {1.0.0},
  url     = {https://calculator.evo-icl.cn},
  license = {MIT}
}
```

中文可写：Xia S. EVO ICL 术后拱高计算器. 版本 1.0.0. 2026. https://github.com/samuelxia1004-max/evo-icl-calculator

引用时请同时说明：这是研究原型，未经临床验证，不是医疗器械；主预测是锁定系数加 Δθ。样本内重拟合保存在文件中，默认不使用。

### 更新记录

#### v1.0.0 — 2026-10-05

面向公开阅读的第一次仓库发布。

- 增加 MIT 许可证，版权人 Samuel Xia，2026。
- 用中英双语写明用途、锁定系数、数据来源、嵌入文件的实际条数，以及稿件中 377 眼与 200 例/397 眼两种口径需要统一。
- 写明验证状态：研究原型，未经临床验证，不是医疗器械。
- 增加 `CITATION.cff`。
- 预测公式、锁定系数、方位修正、安全规则和内置自检均保持合并后的 `main` 原样（该计算更新来自已合并的 PR #1）。页面模型标签仍为 2.0.2。

页面「设置」里还有更早的应用内变更记录（1.0、2.0、2.0.1、2.0.2），那是模型实现的版本，不是本仓库的 v1.0 标签。

### 许可

[MIT License](LICENSE)。Copyright (c) 2026 Samuel Xia。

许可覆盖软件代码与本说明。它不把本工具变成医疗器械，也不提供正确性、临床适用性或特定用途的保证。嵌入的去标识化队列只随这个研究计算器分发，用于复现页面上的样本内说明。

---

## English

### What this tool does

An Implantable Collamer Lens (ICL) is a phakic posterior-chamber lens. After implantation, a gap remains between the lens and the crystalline lens. That gap is the **vault**, measured in micrometres (μm). Vaults that are too low or too high matter clinically. This repository is a **single-page HTML calculator** (`index.html`). Enter preoperative measurements and a proposed ICL plan; it estimates **vault at 1 month** and shows an interval, a target-zone probability, a reliability grade, and safety notices. The notices do not change the number.

Prediction runs in the browser. The embedded cohort is de-identified numbers used for the in-page research checks and the in-sample intervals. Opening the page does not upload those numbers, or what you type, to a server for this project. The first time OCR or PDF features run, the page downloads runtime files from a public CDN.

The interface switches between Chinese and English. Tabs: Prediction, Decision, Follow-up, OCR, Research, Reports, and Settings / self-tests.

### How to open it

GitHub Pages is enabled for this repository. It publishes the root of the `main` branch, with the custom domain `calculator.evo-icl.cn` (the `CNAME` file). The HTTPS certificate is approved. Use:

**[https://calculator.evo-icl.cn](https://calculator.evo-icl.cn)**

`https://samuelxia1004-max.github.io/evo-icl-calculator/` redirects to that custom domain. Pages is not set to enforce HTTPS, so the `http://` URL also answers. For reading and demonstration, use the `https://` address above.

Local use: clone the repository and open `index.html` in a browser. There is no build step.

```bash
git clone https://github.com/samuelxia1004-max/evo-icl-calculator.git
# open index.html from that directory in a browser
```

To use it:

1. Treat **ACD** as internal anterior chamber depth, from the corneal endothelium to the anterior lens surface (true ACD). The China NHC 2.80 mm figure and the FDA 3.00 mm figure both use that definition.
2. Enter lens thickness (LT) and horizontal and vertical sulcus diameters (STS-H / STS-V). If UBM sulcus diameters are absent, the WTW fallback can be selected. Fallback enters the prediction and is flagged in the reliability grade.
3. Choose ICL size (12.1 / 12.6 / 13.2 / 13.7 mm), toric or not, and orientation θ (0° horizontal, 90° vertical).
4. Read three quantities together: the locked-model point prediction, the orientation term Δθ, and their sum. The page also shows a normal or empirical interval, a bootstrap coefficient band, safety notices, and the Zhu 2021 published formula as a cross-check. The cross-check does not enter the main prediction.
5. The default target zone is 250–750 μm. It can be changed to 400–600 μm or to custom limits. The three class probabilities (low / ideal / high) stay split at 250 and 750 μm.
6. Self-tests: open Settings and click “Run all self-tests” (运行全部自检). The page prints how many passed. This release does not change those tests or the prediction code.

Inputs outside these bounds are treated as unit or decimal errors and block prediction: ACD 2.3–4.5, LT 2.5–5.5, STS 9.5–14.5, WTW 9.5–14.0 mm, orientation 0–180°.

### Model and locked coefficients

The endpoint is vault at 1 month, in μm. The default prediction uses the **locked coefficients** below. They live in `EMBED.coef` and `VERT_COEF` inside `index.html`. The screen rounds them to two decimals. v1.0 does not change them and does not switch to the in-sample refit.

Displayed form:

```text
Vault_1m (μm) = −959.81 + 198.85×ACD + 189.40×ICL size + 45.99×Toric − 114.99×STS_eff − 99.38×LT + Δθ
Δθ = −58.99 × sin²θ
STS_eff = 1 / √(cos²θ / STS-H² + sin²θ / STS-V²)     θ: horizontal = 0°, vertical = 90°
WTW fallback: STS-H ≈ 2.627 + 0.789×WTW; STS-V ≈ 2.780 + 0.815×WTW
```

Full-precision locked values in code: intercept −959.8149, ACD 198.8547, size 189.3997, toric 45.9887, STS_eff −114.9899, LT −99.3845, orientation coefficient −58.9862. The WTW fallback in code is STS-H = 2.6272317706 + 0.7887754050×WTW and STS-V = 2.7803584299 + 0.8145421548×WTW.

Units: ACD, LT, STS, WTW, and ICL size in millimetres; toric is 0 or 1; vault is in micrometres. Δθ is added on top of the locked prediction. It does not replace the locked coefficients. Δθ is 0 at θ = 0° or 180°, and −58.99 μm at θ = 90°. Intermediate angles follow sin²θ. The screen shows the locked prediction and the add-on separately.

The orientation coefficient is the one recorded in the calculator source: eye-level ordinary least squares of the locked-model residual (observed minus locked prediction) on sin²θ, among embedded eyes with a scorable 1-month vault. The source records a mean residual of +24.073 μm in horizontal eyes and −34.913 μm in vertical eyes, and a coefficient of −58.986 μm (displayed −58.99, stored −58.9862). Recorded orientations in the cohort are only 0° and 90°, so sin²θ acts as a vertical indicator on those eyes. A joint refit of every slope together with sin²θ gave −56.59 μm and is **not** used. A patient-equal sensitivity analysis gave about −46.9 μm and is not used. The term only removes this embedded sample’s in-sample vertical-versus-horizontal mean gap. It leaves the shared horizontal offset of about +24 μm in place. It needs external validation. The source does not present it as a confirmed clinical effect size. Ouchi 2025 reported about 150 μm lower vault with vertical fixation in a within-patient comparison; the page keeps that as a separate literature notice.

The same file stores an in-sample OLS refit (`EMBED.betaRefit`): intercept −995.6236, ACD 201.2389, size 270.5329, toric 38.3079, STS_eff −195.887, LT −108.2903. The author kept the locked coefficients as the default. The in-page model card states that the cohort on which the locked coefficients were fit still needs to be documented by the author. This repository does not add that fitting note.

Uncertainty, which does not change the point-prediction formula:

- The selectable σ for the normal interval is 151 μm (internal) or 192 μm (conservative). The residual standard deviation stored as `EMBED.sd1` is 144.25 μm.
- Empirical intervals use the locked model’s **in-sample** residual quantiles on the scorable embedded eyes. They were not re-estimated after the orientation term.
- The coefficient band is 300 patient-level bootstrap draws. The draws scatter around the refit; the screen shifts those deviations onto the locked point prediction and then adds the same Δθ.
- Reliability grades A–D combine cohort range, Mahalanobis distance, WTW fallback, and missingness.
- A separate early (day-1) logistic flags vault >750 μm. That is a different endpoint. The page labels its AUROC as about 0.81 and treats it as a cross-check only.

### Cross-check (does not enter the main prediction)

Zhu et al., BMC Ophthalmology 2021;21:199 (UBM sulcus plus LT, horizontal fixation, ICL V4c, Pentacam vault at 1 month), with the published coefficients held fixed:

```text
Vault (μm) = −1369.05 + 657.121×ICL size − 287.408×STS-H − 432.497×LT − 137.33×STS-V
```

The page marks the formula as not applicable when fixation is not horizontal. Research → model comparison shows how it behaves on horizontal eyes in the embedded data. The NK (Nakamura) and KS (Igarashi/Shimizu) formulas need CASIA2 ACW/CLR/ATA, which this tool does not collect, so they are omitted.

### Safety notices (advisory only; they do not change the prediction)

| Rule | Source |
| --- | --- |
| ACD < 2.80 mm (from the endothelium): below the general requirement; needs comprehensive evaluation and informed consent | China NHC standard for phakic posterior-chamber IOL implantation (2024) |
| ACD < 3.00 mm: the entered value is true ACD from the endothelium, so the FDA contraindication applies directly | FDA EVO/EVO+ Visian ICL labeling, P030016/S035 (2022) |
| Endothelial cell density < 2000/mm² | China NHC 2024 standard |
| Minimum ECD by age and ACD, when age and endothelial count are filled in | FDA EVO labeling, Table 3 |
| Age < 18 (NHC); outside 21–45 (FDA indication) | The same two documents |
| Near-vertical fixation shows Δθ and notes that Ouchi 2025 found about 150 μm lower vault with vertical fixation | Residual fit recorded in this tool; Ouchi M. Sci Rep 2025 |

### Where the data come from, and what the file contains

The calculator describes the series as a **single-centre retrospective** cohort. This repository does not name the hospital or institution. The app describes the embedded rows as de-identified research data: an anonymous id, clinical numbers, year, laterality, age, and sex. The page states that names, phone numbers, and national ID numbers are absent.

Eye-level rows are the `DATASET` array in `index.html`. The counts below were obtained by counting that array and the adjacent `EMBED` object. They are not an interpretation of manuscript prose.

`DATASET` has **399** eye records, ids `C001`–`C399`. Fields: `pg`, `year`, `eye`, `age`, `sex`, `acd`, `lt`, `stsh`, `stsv`, `wtw`, `size`, `cyl`, `toric`, `orient`, `vEarly`, `v1m`, `v3m`, `v6m`, `id`.

The app treats `pg` as the patient cluster (the patient-level bootstrap resamples both eyes of a `pg` together). Year, age, and sex match within a `pg`. There are **201** `pg` values: 198 with both OD and OS, and 3 with OS only. Sex is marked female for 148 people (294 eyes) and male for 53 people (105 eyes). Age ranges from 17 to 48 years. Registration year: 2022, 54 eyes (27 `pg` values); 2023, 152 eyes (76); 2024, 157 eyes (80); 2025, 36 eyes (18). Recorded orientation is only 0° or 90°. Three records have no orientation; the code treats a missing angle as 0° when it calculates.

Non-null follow-up fields:

| Field | Non-null rows | Distinct `pg` values |
| --- | ---: | ---: |
| Early vault `vEarly` | 397 | 200 |
| 1-month vault `v1m` | 379 | 191 |
| 3-month vault `v3m` | 330 | — |
| 6-month vault `v6m` | 304 | — |
| Both `vEarly` and `v1m` | 377 | 190 |
| `v1m` and lens thickness `lt` | 373 | — |

The only records without an early vault are both eyes of one 2023 `pg`; those two eyes do have a 1-month vault. The early-vault subset is therefore 2 eyes and 1 `pg` smaller than the full table. Of the 379 records with a 1-month vault, 6 have no `lt`. The calculator withholds a prediction when `lt` is missing, so 373 one-month records are scorable with the current formula. `EMBED.nfit`, `EMBED.n1`, and the length of the residual array `resid1m` are all 373. `EMBED.ratios.n` is 377, the same count as records that have both an early vault and a 1-month vault. Among those 373, recorded orientation is 0° in 249, 90° in 121, and missing in 3. Counting the missing values as 0°, as the code does, gives the 252 horizontal and 121 vertical eyes named in the source comment.

The Settings panel’s cohort figure is `DATASET.length`, **399** eyes. The model card and the “embedded 373 eyes” validation hint are the scorable 1-month subset. Those two figures are different denominators.

**Cohort-size wording in the manuscript should be reconciled.** Background notes say **377 eyes**. A manuscript says **200 patients / 397 eyes**. Neither wording is the full embedded table (399 eyes, 201 `pg` values). The subsets in this file with those same numbers are: 377 records have both an early vault and a 1-month vault, and `EMBED.ratios.n` is also 377; 397 records with an early vault fall in 200 `pg` groups. The 373 figure is a third count: 1-month records that also have `lt` and can therefore be scored, which is the `nfit` value the page uses. A matching count shows that the subset exists in the file. It does not, by itself, establish that the manuscript sentence was defining that subset. The manuscript should state which endpoint and which missingness rule each number uses. Until then, 377, 397, and 373 should not be substituted for one another.

### Validation status

This is a **research prototype**. MAE, R², coverage, and calibration computed on the embedded cohort are **apparent (in-sample)** performance on the development data, and they are optimistic. They are not independent external validation, not a prospective clinical validation, and not evidence that the model transports to another centre. External validation and local recalibration are required before cross-centre use. The orientation term needs external validation as well: after it is applied, the in-sample means of the horizontal and vertical subgroups move together because the coefficient was fit to that gap.

The Zhu 2021 coefficients come from a separate published study, so on horizontal eyes in this embedded table the formula is an external cross-check. That comparison is not like-for-like with models fit on the same rows.

### References

1. National Health Commission of the People’s Republic of China. Standard for phakic posterior-chamber intraocular lens implantation (2024 edition). https://www.nhc.gov.cn/yzygj/c100068/202412/72d6714239dd440291623eab397819dc/files/1736385429410_38008.pdf
2. FDA. EVO/EVO+ Visian ICL, PMA P030016/S035, Professional Use Information (2022). https://www.accessdata.fda.gov/cdrh_docs/pdf3/P030016S035C.pdf
3. Zhu QJ, Chen WJ, Zhu WJ, et al. Short-term changes in and preoperative factors affecting vaulting after posterior chamber phakic Implantable Collamer Lens implantation. BMC Ophthalmol. 2021;21:199. https://pubmed.ncbi.nlm.nih.gov/33957891/
4. Zhu QJ, Xing XY, Zhu MH, Ma L. Validation of the vault prediction model based on the sulcus-to-sulcus diameter and lens thickness: a 925-eye prospective study. BMC Ophthalmol. 2022. https://doi.org/10.1186/s12886-022-02698-z
5. Ouchi M. Vault of the phakic intraocular lens during vertical and horizontal fixation within patient comparison. Sci Rep. 2025. https://www.nature.com/articles/s41598-025-95077-9
6. Li X, Lin H, et al. EVO-ICL vault prediction: a data wrangling framework integrating multicenter big data and machine learning. Ophthalmol Ther. 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12882899/
7. Shen Y, Wang L, Jian W, et al. Big-data and artificial-intelligence-assisted vault prediction and EVO-ICL size selection for myopia correction. Br J Ophthalmol. 2023;107:201–206. https://pmc.ncbi.nlm.nih.gov/articles/PMC9887372/
8. Packer M. Meta-analysis and review: effectiveness, safety, and central port design of the intraocular collamer lens. Clin Ophthalmol. 2016;10:1059–1077. https://doi.org/10.2147/OPTH.S111620

Items 6 and 7 are other published vault-prediction papers, listed as background. Their coefficients are not used in this calculator.

### How to cite

Canonical software metadata is in [`CITATION.cff`](CITATION.cff). Suggested citation:

> Xia S. EVO ICL postoperative vault calculator. Version 1.0.0. 2026. https://github.com/samuelxia1004-max/evo-icl-calculator

```bibtex
@software{xia2026evoicl,
  author  = {Xia, Samuel},
  title   = {EVO ICL postoperative vault calculator},
  year    = {2026},
  version = {1.0.0},
  url     = {https://calculator.evo-icl.cn},
  license = {MIT}
}
```

Please state, when citing, that this is a research prototype, that it is not clinically validated, and that it is not a medical device. The main prediction is the locked coefficients plus Δθ. The in-sample refit is stored in the file and is not the default.

### Changelog

#### v1.0.0 — 2026-10-05

First repository release intended for public reading.

- Added the MIT License, copyright Samuel Xia, 2026.
- Documented, in Chinese and English, what the tool does, the locked coefficients, data provenance, the counts actually present in the embedded file, and the cohort-size wording that still needs to be reconciled (377 eyes in the background notes; 200 patients / 397 eyes in a manuscript).
- Stated the validation status: research prototype, not clinically validated, not a medical device.
- Added `CITATION.cff`.
- Left the prediction formula, locked coefficients, orientation term, safety rules, and built-in self-tests as they are on `main` after the merged calculation update (PR #1). The in-page model label remains 2.0.2.

Settings in the page also lists earlier in-app notes (1.0, 2.0, 2.0.1, 2.0.2). Those are model-implementation versions, not this repository’s v1.0 tag.

### License

[MIT License](LICENSE). Copyright (c) 2026 Samuel Xia.

The license covers the software and this documentation. It does not make the tool a medical device, and it does not warrant correctness, clinical fitness, or fitness for a particular purpose. The embedded de-identified cohort is distributed with this research calculator so the in-page, in-sample descriptions can be reproduced.
