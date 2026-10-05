# ICL 术后拱高预测 · 决策支持（研究版）

在线地址：https://calculator.evo-icl.cn （单文件前端 `index.html`，全部计算在浏览器内完成）

> ⚠ **医疗免责声明**：本工具仅供科研与临床参考，不构成医疗建议或自动选片。ICL 尺寸、植入方位与是否手术由手术医生结合完整术前检查最终决定。本工具不是医疗器械。
>
> **Disclaimer:** For research and clinical reference only. Not medical advice, not a medical device, and not autonomous lens sizing. The operating surgeon makes the final decision.

## 计算内容

主模型（单中心回顾性队列，术后 1 个月拱高，内置 373 眼）：

```
Vault_1m (μm) = −959.81 + 198.85×ACD + 189.40×ICL尺寸 + 45.99×Toric − 114.99×STS_eff − 99.38×LT
STS_eff = 1 / √(cos²θ / STS-H² + sin²θ / STS-V²)     θ：水平 = 0°，垂直 = 90°
WTW 回退（无 UBM 沟径时）：STS-H ≈ 2.627 + 0.789×WTW；STS-V ≈ 2.780 + 0.815×WTW
```

- ICL 尺寸：12.1 / 12.6 / 13.2 / 13.7 mm；目标区默认 250–750 μm（可改为 400–600 或自定义）。
- 不确定度：正态区间（σ = 151 或 192 μm）与经验区间（锁定模型在内置队列上的**样本内**残差分位数）；系数不确定带来自 300 次患者级 bootstrap（偏差平移到锁定模型点预测上）。
- 可靠性等级 A–D：队列范围、Mahalanobis 距离、WTW 回退与缺失。
- 早期（第 1 天）>750 μm logistic 交叉提示（不同终点，仅参考）。

### 交叉参考公式（已发表，固定系数）

Zhu 2021（UBM STS + LT，水平植入，ICL V4c，Pentacam 1 个月拱高）：

```
Vault (μm) = −1369.05 + 657.121×ICL尺寸 − 287.408×STS-H − 432.497×LT − 137.33×STS-V
```

仅作对照显示，不参与主预测；非水平植入时标注“不适用”。“科研验证 → 模型对照”中给出该公式在内置队列水平植入眼上的外部表现。

未加入 NK（Nakamura）与 KS（Igarashi/Shimizu）公式：两者依赖 CASIA2 AS-OCT 的 ACW/CLR/ATA，本工具未采集这些输入，且公式与设备绑定。

## 安全提示规则（仅提示，不改变预测）

| 规则 | 来源 |
| --- | --- |
| ACD < 2.80 mm：低于一般要求，需综合评估并充分知情同意 | 国家卫健委《有晶状体眼后房型人工晶状体植入术操作规范（2024年版）》 |
| ACD < 3.00 mm：FDA 标签以 true ACD（角膜内皮至晶状体前表面）< 3.00 mm 为禁忌 | FDA EVO/EVO+ Visian ICL 标签 P030016/S035（2022） |
| 内皮计数 < 2000/mm² | 国家卫健委 2024 规范 |
| 按年龄/ACD 的最低 ECD（填写年龄与内皮计数时） | FDA EVO 标签 Table 3 |
| 年龄 < 18（卫健委）；超出 21–45（FDA 适应证） | 同上 |
| 接近垂直植入：同一患者随机对照中垂直较水平拱高约低 150 μm | Ouchi M. Sci Rep 2025 |

输入合理性限制（超出即视为单位/小数点错误并停止预测）：ACD 2.3–4.5、LT 2.5–5.5、STS 9.5–14.5、WTW 9.5–14.0 mm，方位 0–180°。

## 局限

- 单中心回顾性模型；内置队列上的性能为表观（样本内）性能。锁定系数与在内置数据上 OLS 重拟合的系数不同（尺寸 189 vs 271 μm/mm；STS_eff −115 vs −196 μm/mm），来源队列需作者说明。
- 内置队列中水平植入眼平均偏差（实测−预测）约 +25 μm，垂直植入眼约 −35 μm（见“科研验证 → 亚组分析”）。
- 跨中心使用前需外部验证与本地再校准。

## 参考文献

1. 国家卫生健康委. 有晶状体眼后房型人工晶状体植入术操作规范（2024年版）. https://www.nhc.gov.cn/yzygj/c100068/202412/72d6714239dd440291623eab397819dc/files/1736385429410_38008.pdf
2. FDA. EVO/EVO+ Visian ICL, PMA P030016/S035, Professional Use Information (2022). https://www.accessdata.fda.gov/cdrh_docs/pdf3/P030016S035C.pdf
3. Zhu QJ, Chen WJ, Zhu WJ, et al. Short-term changes in and preoperative factors affecting vaulting after posterior chamber phakic Implantable Collamer Lens implantation. BMC Ophthalmol. 2021;21:199. https://pubmed.ncbi.nlm.nih.gov/33957891/
4. Zhu QJ, Xing XY, Zhu MH, Ma L. Validation of the vault prediction model based on the sulcus-to-sulcus diameter and lens thickness: a 925-eye prospective study. BMC Ophthalmol. 2022. https://doi.org/10.1186/s12886-022-02698-z
5. Ouchi M. Vault of the phakic intraocular lens during vertical and horizontal fixation within patient comparison. Sci Rep. 2025. https://www.nature.com/articles/s41598-025-95077-9
6. Li X, Lin H, et al. EVO-ICL vault prediction: a data wrangling framework integrating multicenter big data and machine learning. Ophthalmol Ther. 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12882899/
7. Shen Y, Wang L, Jian W, et al. Big-data and artificial-intelligence-assisted vault prediction and EVO-ICL size selection for myopia correction. Br J Ophthalmol. 2023;107:201–206. https://pmc.ncbi.nlm.nih.gov/articles/PMC9887372/
8. Packer M. Meta-analysis and review: effectiveness, safety, and central port design of the intraocular collamer lens. Clin Ophthalmol. 2016;10:1059–1077. https://doi.org/10.2147/OPTH.S111620
