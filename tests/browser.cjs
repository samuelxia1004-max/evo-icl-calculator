/* E2E regression + screenshots. Install playwright or set PLAYWRIGHT_MODULE. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const base=process.env.VAULT_BASE_URL||'http://127.0.0.1:8765/';
const output=process.env.VAULT_QA_DIR||path.resolve('test-results');
fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:1440,height:1050}});
 const errors=[],failures=[];page.on('pageerror',e=>errors.push(e.message));
 page.on('response',response=>{if(response.url().startsWith(base)&&response.status()>=400)failures.push(response.url()+':'+response.status());});
 await page.goto(base+'#overview');await page.locator('#content .metric-card').first().waitFor();
 await page.screenshot({path:path.join(output,'overview-desktop.png'),fullPage:true});
 for(const language of ['zh','en']){
  if(language==='en')await page.click('#languageToggle');
  for(const section of ['overview','experiment','scenarios','followup','import','evidence','poster']){
   await page.evaluate(section=>{location.hash=section;},section);
   await page.waitForFunction(section=>VaultApp.getState().page===section,section);
   assert.ok((await page.locator('#content').innerText()).length>100);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Desktop overflow '+section);
  }
 }
 await page.click('#languageToggle');
 await page.evaluate(()=>{location.hash='experiment'});await page.locator('#num-acd').waitFor();
 assert.ok((await page.locator('#pointPrediction').innerText()).includes('409'));
 await page.locator('#num-acd').fill('3.5');await page.locator('#num-acd').dispatchEvent('input');
 assert.ok((await page.locator('#pointPrediction').innerText()).includes('457'));
 await page.locator('#num-acd').fill('');await page.locator('#num-acd').dispatchEvent('input');
 assert.equal(await page.locator('#resultPanel .error-message').count(),1);
 await page.locator('#num-acd').fill('3.2');await page.locator('#num-acd').dispatchEvent('input');
 await page.click('[data-eye="OS"]');assert.ok((await page.locator('#pointPrediction').innerText()).includes('282'));
 await page.click('[data-eye="OD"]');
 await page.selectOption('#level','80');assert.ok((await page.locator('#resultPanel').innerText()).includes('65.5%'));
 await page.selectOption('#level','95');
 await page.click('[data-action="pin"]');assert.equal((await page.evaluate(()=>VaultApp.getState())).pinned.length,1);
 const session=await page.evaluate(()=>({schema:'vault-lab-3',...VaultApp.getState()}));
 await page.evaluate(v=>VaultApp.importSession(v),session);
 assert.equal((await page.evaluate(()=>VaultApp.getState())).pinned.length,1,'Pinned scenarios survive JSON roundtrip');
 await page.evaluate(()=>{location.hash='scenarios'});await page.locator('#targetLow').waitFor();
 await page.locator('#targetLow').fill('600');await page.locator('#targetHigh').fill('400');await page.locator('#targetHigh').dispatchEvent('change');
 assert.deepEqual((await page.evaluate(()=>VaultApp.getState())).target,[400,600]);
 await page.click('[data-scenario="13.2,90"]');
 if(process.env.VAULT_DEBUG)console.log('Scenario state',await page.evaluate(()=>VaultApp.getState()),'Errors',errors,'Content',await page.locator('#content').innerText());
 await page.locator('#pointPrediction').waitFor();
 assert.equal((await page.evaluate(()=>VaultApp.getState())).eyes.OD.size,13.2);
 await page.evaluate(()=>{location.hash='followup'});await page.locator('#obs-month1').waitFor();
 await page.locator('#obs-month1').fill('400');await page.locator('#obs-month1').dispatchEvent('input');
 assert.ok((await page.locator('#followupResult').innerText()).includes('95% PI'));
 await page.evaluate(()=>{location.hash='import'});await page.locator('#measurementText').waitFor();
 await page.click('[data-action="sample-text"]');assert.ok((await page.evaluate(()=>VaultApp.getState())).parsed.acd===3.2);
 await page.click('[data-apply="OD"]');await page.locator('#pointPrediction').waitFor();
 assert.ok((await page.locator('#pointPrediction').innerText()).includes('409'));
 await page.evaluate(()=>{location.hash='import'});await page.locator('#batchText').waitFor();
 await page.click('[data-action="sample-csv"]');await page.click('[data-action="batch-run"]');
 assert.equal((await page.evaluate(()=>VaultApp.getState())).batchOutput.length,3);
 await page.locator('#measurementText').fill('ACD: 3.2\n<img src=x onerror="window.xss=1">');await page.click('[data-action="parse"]');
 assert.equal(await page.evaluate(()=>window.xss),undefined);
 await page.click('[data-action="share"]');assert.equal(await page.locator('#createShare').isDisabled(),true);
 await page.check('#shareConsent');await page.click('#createShare');
 const link=await page.locator('#shareResult textarea').inputValue();await page.click('#modalClose');
 const shared=await browser.newPage();await shared.goto(link);await shared.locator('#pointPrediction').waitFor();
 assert.equal((await shared.evaluate(()=>VaultApp.getState())).eyes.OD.acd,3.2);await shared.close();
 await page.evaluate(()=>{location.hash='experiment'});await page.locator('#pointPrediction').waitFor();
 await page.evaluate(()=>{window.scrollTo({top:0,behavior:'instant'});document.activeElement.blur();document.getElementById('toast').classList.remove('visible');});
 await page.screenshot({path:path.join(output,'experiment-desktop.png'),fullPage:true});
 await page.click('#modelCardButton');assert.equal(await page.locator('#modal').evaluate(e=>e.open),true);await page.click('#modalClose');
 await page.click('#exportButton');assert.ok((await page.locator('#modalBody').innerText()).includes('65.5%'));await page.click('#modalClose');
 await page.evaluate(()=>document.getElementById('printReport').innerHTML=VaultApp.reportHTML());
 await page.emulateMedia({media:'print'});
 await page.pdf({path:path.join(output,'synthetic-summary.pdf'),printBackground:true,preferCSSPageSize:true});
 await page.emulateMedia({media:'screen'});
 const checks=await page.evaluate(()=>VaultApp.selfchecks());assert.ok(checks.every(x=>x[1]));
 const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,deviceScaleFactor:1});
 for(const section of ['overview','experiment','scenarios','followup','import','evidence','poster']){
  await mobile.goto(base+'#'+section);await mobile.locator('#content .panel').first().waitFor();
  assert.equal(await mobile.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Mobile overflow '+section);
 }
 await mobile.goto(base+'#experiment');await mobile.locator('#num-acd').waitFor();
 await mobile.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));
 await mobile.screenshot({path:path.join(output,'experiment-mobile.png'),fullPage:true});
 await mobile.click('#menuToggle');assert.equal(await mobile.locator('#menuToggle').getAttribute('aria-expanded'),'true');
 await mobile.click('#navigation [href="#evidence"]');assert.equal(await mobile.locator('.rail').evaluate(e=>e.classList.contains('open')),false);
 assert.deepEqual(errors,[]);assert.deepEqual(failures,[]);
 const summary={status:'passed',date:'2026-10-14',pages:7,languages:2,desktop:[1440,1050],mobile:[390,844],numerical_checks:checks.length,console_errors:errors,failed_local_requests:failures};
 fs.writeFileSync(path.join(output,'browser-results.json'),JSON.stringify(summary,null,2));
 console.log(JSON.stringify(summary));await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
