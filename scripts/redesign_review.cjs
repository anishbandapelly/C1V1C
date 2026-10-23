// Run against the local app. Real browser tests; no service or solver is mocked.
const {chromium}=require(process.env.C1V1C_NODE_MODULES+'/playwright');
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const out=path.resolve('../../outputs/redesign');fs.mkdirSync(out,{recursive:true});
const report={checks:[],screenshots:[],accessibility:[],errors:[],widths:[]};
const headers={'Home':'Every investment has a trade-off.','City Intelligence':'Where does the city need attention?',
'Investment Optimiser':'What can your investment include?','Climate Shock Lab':'Will the plan hold under pressure?','Decision Intelligence':'What supports this decision?'};
(async()=>{
const browser=await chromium.launch({headless:true,channel:'msedge'});
try{
 const ctx=await browser.newContext({viewport:{width:1440,height:1000},colorScheme:'light'});
 const p=await ctx.newPage();p.on('pageerror',e=>report.errors.push(e.message));
 const check=(name,condition)=>{assert.ok(condition,name);report.checks.push(name)};
 const settle=async()=>{await p.waitForTimeout(350);assert.equal(await p.locator('.civic-nav').count(),1,'one sidebar only')};
 const top=async()=>{await p.locator('[data-testid=stMain]').evaluate(e=>e.scrollTop=0);await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(100)};
 const nav=async name=>{if((p.viewportSize().width)<800)await p.getByRole('button',{name:'Open navigation',exact:true}).click();await p.getByRole('button',{name,exact:true}).click();await p.getByRole('heading',{name:headers[name],exact:true}).waitFor();await settle();await top();check('active route '+name,await p.getByRole('button',{name,exact:true}).getAttribute('aria-current')==='page')};
 const shot=async name=>{await top();await p.screenshot({path:path.join(out,name+'.png')});report.screenshots.push(name);const sizes=await p.evaluate(()=>({width:innerWidth,body:document.body.scrollWidth,main:document.querySelector('[data-testid=stMain]').scrollWidth,mainWidth:document.querySelector('[data-testid=stMain]').clientWidth}));report.widths.push({name,...sizes});check(name+' no page overflow',sizes.body<=sizes.width&&sizes.main<=sizes.mainWidth+1)};
 const theme=async value=>{if(p.viewportSize().width<800)await p.getByRole('button',{name:'Open navigation',exact:true}).click();await p.getByRole('combobox',{name:'Appearance',exact:true}).selectOption(value);await p.waitForFunction(t=>document.documentElement.dataset.theme===t,value);await settle();if(p.viewportSize().width<800)await p.getByRole('button',{name:'Close navigation',exact:true}).click()};
 const axe=async name=>{if(!process.env.C1V1C_AXE_PATH)return;await p.addScriptTag({path:process.env.C1V1C_AXE_PATH});const result=await p.evaluate(async()=>axe.run({runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}));report.accessibility.push({name,version:result.testEngine.version,violations:result.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})),incomplete:result.incomplete.map(v=>v.id)});};
 await p.goto('http://127.0.0.1:8503');await p.getByRole('heading',{name:headers.Home}).waitFor();await settle();
 check('Guest is explicitly unauthenticated',(await p.locator('.profile-toggle').innerText()).includes('Not signed in'));
 await p.locator('.profile-toggle').click();check('Guest menu opens',await p.locator('#profile-panel').isVisible());await p.keyboard.press('Escape');check('Guest menu Escape closes',await p.locator('#profile-panel').isHidden());
 await p.getByRole('button',{name:'Collapse navigation',exact:true}).click();await p.waitForTimeout(250);
 check('Compact rail is 76px',Math.round((await p.locator('.civic-nav').boundingBox()).width)===76);
 await p.getByRole('button',{name:'City Intelligence',exact:true}).hover();check('Collapsed tooltip visible',await p.locator('.nav-link[aria-label="City Intelligence"] .nav-tooltip').isVisible());
 await shot('rail-compact');await p.getByRole('button',{name:'Expand navigation',exact:true}).click();
 await theme('dark');await p.reload();await p.getByRole('heading',{name:headers.Home}).waitFor();await settle();check('Theme persists after reload',await p.locator('html').getAttribute('data-theme')==='dark');
 for(const t of ['light','dark']){
   await theme(t);
   for(const page of Object.keys(headers)){await nav(page);if(page==='City Intelligence')await p.waitForTimeout(1500);await shot(page.split(' ')[0].toLowerCase()+'-initial-'+t);await axe(page+' initial '+t)}
 }
 await p.getByRole('button',{name:'C1V1C — Home',exact:true}).click();await p.getByRole('heading',{name:headers.Home}).waitFor();check('Brand returns Home',await p.getByRole('button',{name:'Home',exact:true}).getAttribute('aria-current')==='page');
 await p.getByRole('button',{name:'Build an investment preview',exact:true}).click();await p.getByRole('button',{name:'Preview allocation',exact:true}).click();await p.getByText('Projects in preview',{exact:true}).waitFor();await settle();
 await nav('Climate Shock Lab');await p.getByRole('button',{name:'Preview shock comparison',exact:true}).click();await p.getByRole('heading',{name:'Extreme rainfall · comparison'}).waitFor();
 await nav('Decision Intelligence');const download=p.waitForEvent('download');await p.getByRole('button',{name:'Export preview snapshot · JSON'}).click();await(await download).saveAs(path.join(out,'preview.json'));check('Download preserves not_run status',JSON.parse(fs.readFileSync(path.join(out,'preview.json'))).solver_status==='not_run');
 for(const t of ['light','dark']){await theme(t);for(const page of ['Investment Optimiser','Climate Shock Lab','Decision Intelligence']){await nav(page);await shot(page.split(' ')[0].toLowerCase()+'-results-'+t);await axe(page+' results '+t)}}
 for(const width of [1280,1024,768,375,320]){
   await p.setViewportSize({width,height:900});await settle();
   for(const t of ['light','dark']){await theme(t);for(const page of ['Home','City Intelligence','Investment Optimiser','Decision Intelligence']){await nav(page);await shot(page.split(' ')[0].toLowerCase()+'-'+width+'-'+t)}}
 }
 await p.getByRole('button',{name:'Open navigation',exact:true}).click();await p.waitForTimeout(250);check('Mobile drawer settled width',Math.round((await p.locator('.civic-nav').boundingBox()).x)===0);await shot('mobile-drawer');
 await p.locator('.brand-home').focus();await p.keyboard.press('Shift+Tab');check('Drawer traps reverse tab',await p.evaluate(()=>!!document.activeElement.closest('#civic-nav')));
 await p.keyboard.press('Escape');check('Drawer closes with Escape',await p.locator('html').getAttribute('data-drawer')==='closed');check('Drawer restores opener focus',await p.getByRole('button',{name:'Open navigation',exact:true}).evaluate(e=>e===document.activeElement));
 await p.getByRole('button',{name:'Open navigation',exact:true}).click();await p.getByRole('button',{name:'Close navigation backdrop'}).click({position:{x:310,y:400}});check('Backdrop dismisses drawer',await p.locator('html').getAttribute('data-drawer')==='closed');
 await axe('mobile dark');
 await p.emulateMedia({reducedMotion:'reduce'});check('Reduced motion disables rail transition',await p.locator('.civic-nav').evaluate(e=>getComputedStyle(e).transitionDuration)==='0s');
 const sys=await browser.newContext({colorScheme:'dark'});const s=await sys.newPage();await s.goto('http://127.0.0.1:8503');await s.getByRole('heading',{name:headers.Home}).waitFor();await s.waitForTimeout(400);check('First visit respects dark system preference',await s.locator('html').getAttribute('data-theme')==='dark');await sys.close();
 check('No automated WCAG violations',report.accessibility.every(scan=>scan.violations.length===0));
 check('No JavaScript page errors',report.errors.length===0);
}catch(e){report.failure=e.stack;throw e}finally{fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify(report,null,2));await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});

