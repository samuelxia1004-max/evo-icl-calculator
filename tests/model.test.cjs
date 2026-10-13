const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const M=require('../model.js');
const model=require('../assets/model.json');
const research=require('../research/results.json');
const synthetic={acd:3.2,lt:3.63,stsh:11.8,stsv:12.2,wtw:11.6,size:12.6,toric:1,angle:0};
test('independent Python-to-browser numerical reference',()=>{
 assert.ok(Math.abs(M.predict(synthetic,model).y-408.7568959404218)<1e-9);
});
test('orientation geometry satisfies horizontal/vertical/symmetry limits',()=>{
 assert.ok(Math.abs(M.effectiveSTS(11.8,12.2,0)-11.8)<1e-12);
 assert.ok(Math.abs(M.effectiveSTS(11.8,12.2,90)-12.2)<1e-12);
 assert.ok(Math.abs(M.effectiveSTS(11.8,12.2,30)-M.effectiveSTS(11.8,12.2,150))<1e-12);
});
test('missing values never silently become zero',()=>{
 for(const key of ['acd','lt','stsh','stsv','size','toric','angle'])for(const value of ['', '  ',null,undefined,NaN,Infinity,true,false,[]])
 assert.equal(M.predict({...synthetic,[key]:value},model).valid,false,`${key}: ${value}`);
});
test('unsupported size, angle, units and toric coding rejected',()=>{
 for(const [key,value] of [['acd',3200],['lt',11.93],['stsh',1196],['stsv',3.1],['size',13],['toric',2],['angle',-1],['angle',181]])
 assert.equal(M.predict({...synthetic,[key]:value},model).valid,false);
});
test('WTW fallback explicit and measured STS unaffected by WTW',()=>{
 assert.equal(M.predict({...synthetic,wtw:200},model).y,M.predict(synthetic,model).y);
 const p=M.predict({...synthetic,source:'wtw',stsh:'',stsv:''},model);
 assert.equal(p.valid,true);assert.equal(p.fallback,true);
 assert.equal(M.predict({...synthetic,source:'wtw',wtw:''},model).valid,false);
});
test('PI levels and coefficient bands have correct ordering',()=>{
 const a=M.predict(synthetic,model,{level:80}),b=M.predict(synthetic,model,{level:95});
 assert.ok(b.band[0]<a.band[0]);assert.ok(a.band[1]<b.band[1]);
 assert.ok(b.centerBand[0]<b.centerBand[1]);
});
test('probabilities remain a valid distribution over supported inputs',()=>{
 for(const size of M.sizes)for(const angle of [0,30,90,150,180]){
  const p=M.predict({...synthetic,size,angle},model).probabilities;
  assert.ok(Math.abs(p.low+p.middle+p.high-1)<1e-10);
  for(const v of Object.values(p))assert.ok(v>=0&&v<=1);
 }
});
test('inverted and zero target limits are handled consistently',()=>{
 const p=M.predict(synthetic,model,{low:400,high:600}),q=M.predict(synthetic,model,{low:600,high:400});
 assert.equal(p.probabilities.target,q.probabilities.target);
 const z=M.predict(synthetic,model,{low:0,high:600});
 assert.equal(z.probabilities.target,M.probabilities(z.y,model.residual_histogram,0,600).target);
});
test('CSV parser handles quoted commas, escaped quotes, BOM and blanks',()=>{
 const rows=M.parseCSV('\uFEFFacd,note\r\n3.2,"a,b"\r\n,"x""y"\r\n');
 assert.equal(rows[0].acd,'3.2');assert.equal(rows[0].note,'a,b');
 assert.equal(rows[1].acd,'');assert.equal(rows[1].note,'x"y');
 assert.throws(()=>M.parseCSV('acd,acd\n3,4'),/Duplicate/);
 assert.throws(()=>M.parseCSV('acd,note\n3,"unfinished'),/Unclosed/);
});
test('model development and temporal counts are consistent',()=>{
 assert.equal(model.training.eyes,341);assert.equal(model.training.patients,173);
 assert.equal(model.temporal_test.n,29);
 assert.deepEqual(model.training.years,[2022,2023,2024]);
 assert.equal(research.cohort.source.eyes,399);
 assert.equal(research.cohort.endpoints.early.n,397);
 assert.equal(research.cohort.endpoints.month1.n,379);
});
test('release data contains aggregates and no embedded individual rows',()=>{
 const bundle=fs.readFileSync(path.join(__dirname,'../assets/bundle.js'),'utf8');
 for(const pattern of ['"pg":','"vEarly":','"orientation_note":','"patient_record":','const DATASET'])assert.ok(!bundle.includes(pattern));
 assert.ok(!fs.readFileSync(path.join(__dirname,'../index.html'),'utf8').includes('DATASET'));
});
test('browser bundle matches the frozen model and published aggregate results',()=>{
 const vm=require('node:vm'),context={window:{}};
 vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../assets/bundle.js'),'utf8'),context);
 const data=JSON.parse(JSON.stringify(context.window.VaultData));
 assert.deepEqual(data.model,model);
 assert.deepEqual(data.research,JSON.parse(fs.readFileSync(path.join(__dirname,'../assets/research.json'),'utf8')));
 assert.deepEqual(data.followup,require('../assets/followup-model.json'));
});
test('metric identity check',()=>{
 const m=M.evaluate([[100,110],[200,180],[300,330]]);
 assert.equal(m.mae,20);assert.equal(m.bias,-20/3);assert.ok(m.r2>0);
});
