"""Plot aggregate results with Matplotlib; no generated or patient-level data."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

root=Path(__file__).resolve().parents[1]
result=json.loads((root/"research/results.json").read_text())
out=root/"research/figures"
out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":14,"axes.spines.top":False,
    "axes.spines.right":False,"axes.labelcolor":"#526b81","text.color":"#19354f",
    "xtick.color":"#526b81","ytick.color":"#526b81","axes.edgecolor":"#d4e1ec",
    "svg.fonttype":"none","pdf.fonttype":42})
navy="#19354f";blue="#176bbd";teal="#0d8b84";soft="#c3d9eb";amber="#a76920"

def finish(fig,name):
    fig.tight_layout(pad=1.3)
    fig.savefig(out/(name+".svg"),bbox_inches="tight",facecolor="white")
    vector=out/(name+".svg")
    vector.write_text("\n".join(line.rstrip() for line in vector.read_text().splitlines())+"\n")
    fig.savefig(out/(name+".png"),dpi=240,bbox_inches="tight",facecolor="white")
    fig.savefig(out/(name+".pdf"),bbox_inches="tight",facecolor="white")
    plt.close(fig)

fig,ax=plt.subplots(figsize=(9,5.1))
keys=["mean","ols_anatomy","ols_axis","ridge_orientation","random_forest","xgboost"]
labels=["Training mean","Horizontal STS OLS","Axis-matched OLS","Orientation Ridge","Random forest","XGBoost"]
values=[result["models"][k]["mae"] for k in keys]
for index,(key,label,value) in enumerate(zip(keys,labels,values)):
    color=teal if key=="ridge_orientation" else soft
    ax.barh(index,value,color=color,height=.56)
    ci=result["models"][key]["mae_ci95"]
    ax.errorbar(value,index,xerr=np.array([[value-ci[0]],[ci[1]-value]]),color=navy,capsize=3,lw=1.2)
    ax.text(157,index,f"{value:.1f}",ha="right",va="center",fontweight="bold" if key=="ridge_orientation" else "normal")
ax.set_yticks(range(len(labels)),labels);ax.invert_yaxis();ax.set_xlim(0,165)
ax.set_xlabel("Mean absolute error (μm); patient-bootstrap 95% CI")
ax.text(.01,-.22,"341 eyes / 173 patients · repeated nested patient-grouped validation",transform=ax.transAxes,fontsize=11,color="#687c90")
finish(fig,"model_comparison")

comparison=result["inference"]["formula_comparison_common_cohort"]
fig,ax=plt.subplots(figsize=(8,4.5))
keys=["KS_horizontal_STS_proxy","KS_binary_STS_proxy","KS_ellipse_STS_proxy"]
labels=["Horizontal STS","Binary H/V STS","Axis-matched ellipse"]
vals=[comparison[k]["mae"] for k in keys]
bars=ax.bar(labels,vals,color=[soft,blue,teal],width=.55)
for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+5,f"{v:.1f}",ha="center",fontsize=20,fontweight="bold")
ax.set_ylim(0,280);ax.set_ylabel("Mean absolute error (μm)")
ax.text(.01,-.24,"394 paired eyes · KS modified with STS proxies; ATA was not measured",transform=ax.transAxes,fontsize=10,color="#687c90")
finish(fig,"axis_matching")

follow=result["longitudinal"]["six_month_comparison"]
fig,ax=plt.subplots(figsize=(8,4.5))
keys=["preoperative_only","plus_observed_early","plus_observed_month1"]
labels=["Preoperative\nmeasurements","+ Observed\nearly vault","+ Observed\n1-month vault"]
vals=[follow[k]["mae"] for k in keys]
bars=ax.bar(labels,vals,color=[soft,blue,teal],width=.55)
for index,(b,v,key) in enumerate(zip(bars,vals,keys)):
    ci=follow[key]["mae_ci95"]
    ax.errorbar(index,v,yerr=np.array([[v-ci[0]],[ci[1]-v]]),capsize=4,color=navy,lw=1.2)
    ax.text(index,ci[1]+6,f"{v:.1f}",ha="center",fontsize=21,fontweight="bold")
ax.set_ylim(0,135);ax.set_ylabel("6-month prediction MAE (μm)")
ax.text(.01,-.27,"Same 281 eyes / 142 patients · nested grouped 5-fold CV · exploratory",transform=ax.transAxes,fontsize=10,color="#687c90")
finish(fig,"followup_comparison")

fig,ax=plt.subplots(figsize=(8,4.5))
cv=result["models"]["ridge_orientation"];temporal=result["temporal"]["ridge_orientation"]
x=np.arange(2);width=.28
ax.bar(x-width/2,[cv["coverage80"]*100,cv["coverage95"]*100],width,label="Grouped CV",color=soft)
ax.bar(x+width/2,[temporal["coverage80"]*100,temporal["coverage95"]*100],width,label="2025 temporal test",color=teal)
for index,target in enumerate([80,95]):
    ax.hlines(target,index-.4,index+.4,color=amber,ls="--",lw=1.3)
    ax.text(index+width/2,temporal[f"coverage{target}"]*100+2,f'{temporal[f"coverage{target}"]*100:.1f}%',ha="center",fontsize=16)
ax.set_xticks(x,["Nominal 80% PI","Nominal 95% PI"]);ax.set_ylim(0,108);ax.set_ylabel("Observed coverage (%)");ax.legend(frameon=False,loc="lower left",fontsize=11)
ax.text(.01,-.2,"Temporal test: 29 eyes / 15 patients; same centre, not external validation",transform=ax.transAxes,fontsize=10,color="#687c90")
finish(fig,"interval_coverage")
print("Generated four aggregate figures (SVG / PDF / PNG).")

# Wide, larger-label versions for a large-format poster; same source values.
plt.rcParams.update({"font.size":18})
fig,ax=plt.subplots(figsize=(8,3.15))
keys=["mean","ols_anatomy","ols_axis","ridge_orientation","random_forest","xgboost"]
labels=["Mean baseline","Horizontal OLS","Axis-matched OLS","Orientation Ridge","Random forest","XGBoost"]
for index,(key,label) in enumerate(zip(keys,labels)):
    value=result["models"][key]["mae"];ci=result["models"][key]["mae_ci95"]
    ax.barh(index,value,color=teal if key=="ridge_orientation" else soft,height=.64)
    ax.errorbar(value,index,xerr=np.array([[value-ci[0]],[ci[1]-value]]),color=navy,capsize=3,lw=1.3)
    ax.text(164,index,f"{value:.1f}",ha="right",va="center",fontsize=18)
ax.set_yticks(range(len(labels)),labels);ax.invert_yaxis();ax.set_xlim(0,170);ax.set_xlabel("MAE (μm)",fontsize=18);ax.tick_params(axis="y",length=0)
finish(fig,"poster_model")

fig,ax=plt.subplots(figsize=(8,2.45))
keys=["preoperative_only","plus_observed_early","plus_observed_month1"]
labels=["Preoperative only","+ observed early","+ observed 1 month"]
for index,(key,label) in enumerate(zip(keys,labels)):
    value=follow[key]["mae"];ci=follow[key]["mae_ci95"]
    ax.barh(index,value,color=teal if key=="plus_observed_month1" else soft,height=.57)
    ax.errorbar(value,index,xerr=np.array([[value-ci[0]],[ci[1]-value]]),color=navy,capsize=3,lw=1.3)
    ax.text(126,index,f"{value:.1f}",ha="right",va="center",fontsize=20)
ax.set_yticks(range(3),labels);ax.invert_yaxis();ax.set_xlim(0,130);ax.set_xlabel("6-month MAE (μm)",fontsize=18);ax.tick_params(axis="y",length=0)
finish(fig,"poster_followup")

fig,ax=plt.subplots(figsize=(8,3.1))
x=np.arange(2);width=.27
ax.bar(x-width/2,[cv["coverage80"]*100,cv["coverage95"]*100],width,label="Grouped CV",color=soft)
ax.bar(x+width/2,[temporal["coverage80"]*100,temporal["coverage95"]*100],width,label="2025 test",color=teal)
for index,target in enumerate([80,95]):
    ax.hlines(target,index-.4,index+.4,color=amber,ls="--",lw=1.4)
    ax.text(index+width/2,temporal[f"coverage{target}"]*100+3,f'{temporal[f"coverage{target}"]*100:.1f}%',ha="center",fontsize=20)
ax.set_xticks(x,["80% PI","95% PI"]);ax.set_ylim(0,112);ax.set_ylabel("Coverage (%)");ax.legend(frameon=False,loc="lower left",fontsize=16)
finish(fig,"poster_coverage")
