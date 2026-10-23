// Real Chromium review against the running Streamlit preview.
const {chromium}=require(process.env.C1V1C_NODE_MODULES+'/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1440,height:1050},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const top=async()=>{await page.locator('[data-testid="stMain"]').evaluate(e=>e.scrollTop=0);await page.waitForTimeout(500)};
 await page.goto('http://127.0.0.1:8501');
 await page.getByRole('heading',{name:'Read the city. Locate the gaps.'}).waitFor();
 await page.locator('.js-plotly-plot').waitFor();
 await page.waitForTimeout(2500);await top();
 await page.screenshot({path:'../../outputs/city-desktop.png',fullPage:true});
 await page.getByText('Investment Optimiser',{exact:true}).click();
 await page.getByRole('button',{name:'Preview allocation',exact:true}).click();
 await page.getByText('Projects in preview',{exact:true}).waitFor();
 await top();
 await page.screenshot({path:'../../outputs/investment-desktop.png',fullPage:true});
 await page.getByText('Climate Shock Lab',{exact:true}).click();
 await page.getByRole('button',{name:'Preview shock comparison',exact:true}).click();
 await page.getByRole('heading',{name:'Extreme rainfall · comparison'}).waitFor();
 await top();
 await page.screenshot({path:'../../outputs/shock-desktop.png',fullPage:true});
 await page.getByText('Decision Intelligence',{exact:true}).click();
 await page.getByRole('heading',{name:'Decision summary',exact:true}).waitFor();
 const dl=page.waitForEvent('download');
 await page.getByRole('button',{name:'Export preview snapshot · JSON'}).click();
 const download=await dl;await download.saveAs('../../outputs/review-snapshot.json');
 await top();
 await page.screenshot({path:'../../outputs/decision-desktop.png',fullPage:true});
 const widths=[];
 for(const width of [320,375,768]){
   await page.setViewportSize({width,height:900});
   await top();
   widths.push(await page.evaluate(()=>({width:innerWidth,body:document.body.scrollWidth,main:document.querySelector('[data-testid="stMain"]').scrollWidth})));
   await page.screenshot({path:`../../outputs/decision-${width}.png`,fullPage:true});
 }
 await page.setViewportSize({width:1440,height:1050});await top();
 const caption=await page.locator('[data-testid="stCaptionContainer"] p').first().evaluate(e=>({color:getComputedStyle(e).color,fontSize:getComputedStyle(e).fontSize}));
 const controls=await page.getByRole('button',{name:'Export preview snapshot · JSON'}).boundingBox();
 fs.writeFileSync('../../outputs/browser-review.json',JSON.stringify({errors,widths,caption,exportControl:controls},null,2));
 await browser.close();
 if(errors.length||widths.some(x=>x.body>x.width))process.exitCode=1;
})();
