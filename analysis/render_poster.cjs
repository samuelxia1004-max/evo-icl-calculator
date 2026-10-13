/* Render editable poster. Install Playwright or set PLAYWRIGHT_MODULE. */
const path=require('node:path'), fs=require('node:fs');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1600,height:1200}});
  await page.goto('file://'+path.join(root,'poster/poster.html'));
  await page.emulateMedia({media:'print'});
  await page.evaluate(()=>document.fonts.ready);
  const blocks=await page.locator('.header,.block,.conclusion,.footer').evaluateAll(elements=>elements.map(e=>({heading:e.querySelector('h1,h2')?.innerText||e.className,height:e.clientHeight,scroll:e.scrollHeight,width:e.clientWidth,scrollWidth:e.scrollWidth})));
  if(blocks.some(b=>b.scroll>b.height+1||b.scrollWidth>b.width+1))throw new Error('Poster overflow: '+JSON.stringify(blocks));
  if(!await page.evaluate(()=>document.fonts.check('36px PosterSans')))throw new Error('Poster font failed to load');
  await page.pdf({path:path.join(root,'poster/ICL_A0_draft.pdf'),printBackground:true,preferCSSPageSize:true});
  fs.writeFileSync(path.join(root,'poster/layout-check.json'),JSON.stringify({status:'passed',page_mm:[841,1189],blocks},null,2));
  console.log(JSON.stringify({status:'passed',blocks}));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
