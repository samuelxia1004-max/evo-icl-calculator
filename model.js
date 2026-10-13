/* Pure numerical helpers shared by the browser and regression tests. */
(function (root) {
  const finite = value => (typeof value === 'number' || typeof value === 'string' && value.trim() !== '') && Number.isFinite(Number(value));
  const clamp = (value, low, high) => Math.min(high, Math.max(low, value));
  const sizes = [12.1, 12.6, 13.2, 13.7];
  const ranges = {acd:[2.3,4.5], lt:[2.5,5.5], stsh:[9,15], stsv:[10.5,14], wtw:[9.5,14], angle:[0,180]};
  function effectiveSTS(h, v, angle) {
    const radians = angle * Math.PI / 180;
    return 1 / Math.sqrt(Math.cos(radians)**2 / h**2 + Math.sin(radians)**2 / v**2);
  }
  function features(eye, model) {
    const values = {};
    const errors = [];
    for (const key of ['acd','lt','size','toric','angle']) {
      if (!finite(eye[key])) errors.push(key);
      values[key] = Number(eye[key]);
    }
    if (!sizes.includes(values.size)) errors.push('size');
    if (![0,1].includes(values.toric)) errors.push('toric');
    const fallback = eye.source === 'wtw';
    for (const key of fallback ? ['wtw'] : ['stsh','stsv']) {
      if (!finite(eye[key])) errors.push(key);
      values[key] = Number(eye[key]);
    }
    for (const key of Object.keys(ranges)) {
      if (finite(values[key]) && (values[key] < ranges[key][0] || values[key] > ranges[key][1])) errors.push(key);
    }
    if (errors.length) return {errors:[...new Set(errors)]};
    if (fallback) {
      for (const key of ['stsh','stsv']) {
        const formula = model.wtw_fallback[key];
        values[key] = formula.intercept + formula.slope * values.wtw;
      }
      if (values.stsh < ranges.stsh[0] || values.stsh > ranges.stsh[1] || values.stsv < ranges.stsv[0] || values.stsv > ranges.stsv[1]) return {errors:['wtw']};
    }
    values.sts_eff = effectiveSTS(values.stsh, values.stsv, values.angle);
    values.sin2 = Math.sin(values.angle * Math.PI/180)**2;
    return {values,fallback,errors:[]};
  }
  function linear(model, values) {
    return model.intercept + model.features.reduce((sum,key) => sum + model.coefficients[key] * (finite(values[key]) ? Number(values[key]) : model.imputation[key]), 0);
  }
  function quantile(values, probability) {
    if (!values.length) return NaN;
    const array = [...values].sort((a,b)=>a-b);
    const index = probability*(array.length-1), lo=Math.floor(index), hi=Math.ceil(index);
    return array[lo]*(hi-index || (hi===lo?1:0)) + (hi===lo?0:array[hi]*(index-lo));
  }
  function histogramCDF(hist, x) {
    const edges=hist.edges, counts=hist.counts;
    const total=counts.reduce((sum,c)=>sum+c,0)+(hist.tail_low||0)+(hist.tail_high||0);
    if (!total) return NaN;
    if (x < edges[0]) return 0;
    if (x >= edges[edges.length-1]) return 1;
    let sum=hist.tail_low||0;
    for(let index=0;index<counts.length;index++) {
      if (x >= edges[index+1]) sum+=counts[index];
      else if(x >= edges[index]) {sum+=counts[index]*(x-edges[index])/(edges[index+1]-edges[index]);break;}
      else break;
    }
    return clamp(sum/total,0,1);
  }
  function probabilities(y, histogram, low=250, high=750) {
    const a=Math.min(low,high), b=Math.max(low,high);
    const lowP=histogramCDF(histogram,250-y), highP=1-histogramCDF(histogram,750-y);
    return {low:lowP, middle:clamp(1-lowP-highP,0,1), high:highP,
            target:clamp(histogramCDF(histogram,b-y)-histogramCDF(histogram,a-y),0,1)};
  }
  function predict(eye, model, options={}) {
    const resolved=features(eye,model);
    if(resolved.errors.length) return {valid:false,errors:resolved.errors};
    const y=linear(model,resolved.values), q=model.residual_quantiles;
    const level=options.level===80?80:95;
    const band=level===80?[y+q[0],y+q[1]]:[y+q[2],y+q[3]];
    const boot=(model.bootstrap_coefficients||[]).map(coef=>coef[0]+model.features.reduce((sum,key,index)=>sum+coef[index+1]*resolved.values[key],0));
    const centerBand=boot.length?[quantile(boot,.025),quantile(boot,.975)]:[y,y];
    const tails=[];
    for(const key of ['acd','lt','stsh','stsv','size']) {
      const ref=model.reference[key].quantiles;
      if(resolved.values[key] < ref[1] || resolved.values[key] > ref[ref.length-2]) tails.push(key);
    }
    if(resolved.values.angle!==0 && resolved.values.angle!==90 && resolved.values.angle!==180) tails.push('angle');
    return {valid:true,y,band,centerBand,level,resolved:resolved.values,fallback:resolved.fallback,tails,
            probabilities:probabilities(y,model.residual_histogram,options.low??250,options.high??750),
            contributions:model.features.map(key=>({key,value:model.coefficients[key]*resolved.values[key]}))};
  }
  function percentile(value, reference) {
    const qs=reference.quantiles;
    if(value<=qs[0]) return 0;
    if(value>=qs[qs.length-1]) return 100;
    for(let index=1;index<qs.length;index++) if(value<=qs[index]) return ((index-1)+(value-qs[index-1])/(qs[index]-qs[index-1]||1))*100/(qs.length-1);
    return 100;
  }
  function parseCSV(text) {
    const delimiter=text.split(/\r?\n/)[0].includes('\t')?'\t':',';
    const rows=[];let row=[],cell='',quoted=false;
    for(let index=0;index<text.length;index++) {
      const character=text[index];
      if(character==='"') {if(quoted&&text[index+1]==='"'){cell+='"';index++;}else quoted=!quoted;}
      else if(character===delimiter&&!quoted){row.push(cell.trim());cell='';}
      else if((character==='\n'||character==='\r')&&!quoted) {if(character==='\r'&&text[index+1]==='\n')index++;row.push(cell.trim());if(row.some(Boolean))rows.push(row);row=[];cell='';}
      else cell+=character;
    }
    if(quoted)throw new Error('Unclosed CSV quote');
    row.push(cell.trim());if(row.some(Boolean))rows.push(row);
    if(rows.length<2)return [];
    if(rows.length>5001)throw new Error('Maximum 5000 rows');
    const headers=rows.shift().map(header=>header.replace(/^\uFEFF/,'').toLowerCase());
    if(headers.length!==new Set(headers).size)throw new Error('Duplicate CSV column');
    return rows.map((record,index)=>({...Object.fromEntries(headers.map((header,column)=>[header,record[column]??''])),row:index+2}));
  }
  function evaluate(pairs) {
    if(pairs.length<2)return null;
    const observed=pairs.map(pair=>pair[1]), prediction=pairs.map(pair=>pair[0]);
    const mean=observed.reduce((a,b)=>a+b,0)/pairs.length;
    const errors=pairs.map(([p,y])=>p-y), sse=errors.reduce((sum,e)=>sum+e*e,0), sst=observed.reduce((sum,y)=>sum+(y-mean)**2,0);
    return {n:pairs.length,mae:errors.reduce((sum,e)=>sum+Math.abs(e),0)/pairs.length,rmse:Math.sqrt(sse/pairs.length),
      bias:errors.reduce((sum,e)=>sum+e,0)/pairs.length,r2:sst?1-sse/sst:null,within200:errors.filter(e=>Math.abs(e)<=200).length/pairs.length};
  }
  const api={sizes,ranges,finite,clamp,effectiveSTS,features,linear,quantile,histogramCDF,probabilities,predict,percentile,parseCSV,evaluate};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  else root.VaultMath=api;
})(typeof window!=='undefined'?window:globalThis);
