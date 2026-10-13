/* Exercise the actual optional PDF.js and Tesseract engines with synthetic data. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const base=process.env.VAULT_BASE_URL||'http://127.0.0.1:8765/';
const output=process.env.VAULT_QA_DIR||path.resolve('test-results');
fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage();await page.goto(base+'#import');await page.locator('#ocrFile').waitFor({state:'attached'});
  const producer=await browser.newPage();
  await producer.setContent('<html><body><h1>SYNTHETIC RESEARCH TEST</h1><p>ACD: 3.20 mm</p><p>LT: 3.63 mm</p><p>STS-H: 11.80 mm</p><p>STS-V: 12.20 mm</p></body></html>');
  const pdf=await producer.pdf({format:'A4'});await producer.close();
  await page.locator('#ocrFile').setInputFiles({name:'synthetic.pdf',mimeType:'application/pdf',buffer:pdf});
  await page.waitForFunction(()=>VaultApp.getState().parsed.acd===3.2,{},{timeout:120000});
  assert.equal((await page.evaluate(()=>VaultApp.getState())).parsed.stsh,11.8);
  console.log('Native-text PDF extraction passed');
  const image=await page.evaluate(()=>{const canvas=document.createElement('canvas');canvas.width=1100;canvas.height=420;const c=canvas.getContext('2d');c.fillStyle='#fff';c.fillRect(0,0,1100,420);c.fillStyle='#000';c.font='42px monospace';['SYNTHETIC RESEARCH TEST','ACD: 3.20 mm','LT: 3.63 mm','STS-H: 11.80 mm','STS-V: 12.20 mm'].forEach((line,i)=>c.fillText(line,40,60+i*70));return canvas.toDataURL('image/png').split(',')[1];});
  await page.locator('#ocrFile').setInputFiles({name:'synthetic.png',mimeType:'image/png',buffer:Buffer.from(image,'base64')});
  await page.waitForFunction(()=>!VaultApp.getState().importBusy&&document.querySelector('#ocrPreview img'),{},{timeout:180000});
  const parsed=(await page.evaluate(()=>VaultApp.getState())).parsed;
  assert.equal(parsed.acd,3.2);assert.equal(parsed.lt,3.63);assert.equal(parsed.stsh,11.8);assert.equal(parsed.stsv,12.2);
  console.log('Real image OCR extraction passed');
  await page.screenshot({path:path.join(output,'import-desktop.png'),fullPage:true});
  fs.writeFileSync(path.join(output,'import-results.json'),JSON.stringify({status:'passed',pdf_engine:'PDF.js 4.10.38',ocr_engine:'Tesseract.js 6.0.1',data:'synthetic only',parsed},null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
