// Trusted application shell. Profile text is inserted with textContent, never HTML.
export default function({parentElement,data,setTriggerValue,setStateValue}) {
 window.__civicCleanup?.();
 // Portal keeps the fixed rail outside Streamlit's scrolling/containment wrappers.
 const root=document.createElement('div');root.id='civic-shell-portal';document.body.appendChild(root);
 const doc=document.documentElement;
 const read=(k,f)=>{try{return localStorage.getItem(k)||f}catch{return f}};
 const save=(k,v)=>{try{localStorage.setItem(k,v)}catch{/* Private browser: in-memory preference. */}};
 const media=matchMedia('(prefers-color-scheme: dark)');
 let choice=read('c1v1c-theme','system');
 if(!['light','dark','system'].includes(choice))choice='system';
 let compact=read('c1v1c-compact','false')==='true';
 const mobile=()=>matchMedia('(max-width: 799px)').matches;
 const icon=(paths)=>`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths}</svg>`;
 const icons=[
 '<path d="m3 10 9-7 9 7v10H3Z"/><path d="M9 20v-7h6v7"/>',
 '<path d="m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2Z"/><path d="M9 3v16M15 5v16"/>',
 '<path d="M4 20V10m8 10V4m8 16v-7M2 20h20"/>',
 '<path d="M7 16a5 5 0 1 1 2-9 6 6 0 0 1 11 5 4 4 0 0 1-2 4M9 14l-2 4h5l-2 4"/>',
 '<path d="M5 3h10l4 4v14H5Z"/><path d="M14 3v5h5M8 12h8M8 16h5"/>'
 ];
 const panel=icon('<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/>');
 root.innerHTML=`<button class="mobile-open" aria-label="Open navigation" aria-expanded="false" aria-controls="civic-nav">${panel}<span>C1V1C</span></button>
 <button class="nav-backdrop" aria-label="Close navigation backdrop" tabindex="-1" hidden></button>
 <aside id="civic-nav" class="civic-nav" aria-label="Workspace navigation">
 <div class="brand-row"><button class="brand-home" aria-label="C1V1C — Home" title="C1V1C — Home"><img class="logo-light" src="/app/static/brand/logo-light.png" alt="C1V1C — Tulabhara AI"><img class="logo-dark" src="/app/static/brand/logo-dark.png" alt="C1V1C — Tulabhara AI"><span class="compact-brand">${icon(icons[0])}</span></button></div>
 <div class="rail-tools"><button class="collapse-toggle" aria-label="Collapse navigation" title="Collapse navigation">${panel}<span class="nav-label">Collapse navigation</span></button><button class="mobile-close" aria-label="Close navigation">${icon('<path d="m6 6 12 12M6 18 18 6"/>')}</button></div>
 <nav class="nav-links" aria-label="Planning workspace"><p class="nav-section nav-label">Planning workspace</p></nav>
 <div class="nav-footer"><label class="theme-control" title="Appearance">${icon('<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1"/>')}<span class="nav-label">Appearance</span><select aria-label="Appearance"><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></label>
 <button class="profile-toggle" aria-expanded="false" aria-controls="profile-panel" title="Guest workspace"><span class="avatar"></span><span class="nav-label profile-copy"><strong></strong><small></small></span><span class="nav-label">···</span></button>
 <section id="profile-panel" class="profile-panel" aria-label="Guest profile" hidden><h2>Guest workspace</h2><p>No account is connected. This is a local frontend preview.</p><p>Your appearance preference stays in this browser. Plan previews last for this session; export them to keep a copy.</p><button class="profile-close">Close profile</button></section></div></aside>`;
 const aside=root.querySelector('aside'),backdrop=root.querySelector('.nav-backdrop'),openButton=root.querySelector('.mobile-open');
 const nav=root.querySelector('nav');
 data.pages.forEach((page,i)=>{
   const b=document.createElement('button');b.className='nav-link';b.title=page;b.setAttribute('aria-label',page);
   b.innerHTML=icon(icons[i])+'<span class="nav-label"></span><span class="nav-tooltip" role="tooltip"></span>';
   b.querySelector('.nav-label').textContent=page;b.querySelector('.nav-tooltip').textContent=page;
   if(page===data.page)b.setAttribute('aria-current','page');
   b.onclick=()=>go(page);nav.append(b);
 });
 root.querySelector('.avatar').textContent=data.profile.initials;
 root.querySelector('.profile-copy strong').textContent=data.profile.display_name;
 root.querySelector('.profile-copy small').textContent=data.profile.detail;
 function go(page){closeDrawer(false);window.__civicRouteFocus=true;setTriggerValue('action',page)}
 root.querySelector('.brand-home').onclick=()=>go('Home');
 function setCompact(){doc.dataset.compact=String(compact);const b=root.querySelector('.collapse-toggle');b.setAttribute('aria-label',compact?'Expand navigation':'Collapse navigation');b.title=b.getAttribute('aria-label');b.setAttribute('aria-expanded',String(!compact))}
 setCompact();root.querySelector('.collapse-toggle').onclick=()=>{compact=!compact;save('c1v1c-compact',String(compact));setCompact()};
 function appearance(){const resolved=choice==='system'?(media.matches?'dark':'light'):choice;doc.dataset.theme=resolved;doc.style.colorScheme=resolved;
  if(resolved!==data.theme)setStateValue('appearance',{choice,resolved});}
 root.querySelector('select').value=choice;
 root.querySelector('select').onchange=e=>{choice=e.target.value;save('c1v1c-theme',choice);appearance()};appearance();
 media.addEventListener('change',appearance);
 function closeDrawer(focus=true){doc.dataset.drawer='closed';backdrop.hidden=true;openButton.setAttribute('aria-expanded','false');if(mobile())aside.inert=true;document.querySelector('[data-testid="stMain"]')?.removeAttribute('inert');if(focus)openButton.focus()}
 function openDrawer(){doc.dataset.drawer='open';backdrop.hidden=false;aside.inert=false;openButton.setAttribute('aria-expanded','true');document.querySelector('[data-testid="stMainBlockContainer"]')?.setAttribute('data-drawer-open','true');root.querySelector('.brand-home').focus()}
 // Main content cannot receive pointer input behind the backdrop; key focus is trapped below.
 openButton.onclick=openDrawer;root.querySelector('.mobile-close').onclick=()=>closeDrawer();backdrop.onclick=()=>closeDrawer();
 const resize=()=>{aside.inert=mobile()&&doc.dataset.drawer!=='open';if(!mobile()){backdrop.hidden=true;doc.dataset.drawer='closed'}};resize();window.addEventListener('resize',resize);
 const profile=root.querySelector('#profile-panel'),profileButton=root.querySelector('.profile-toggle');
 function closeProfile(){profile.hidden=true;profileButton.setAttribute('aria-expanded','false')}
 profileButton.onclick=()=>{profile.hidden=!profile.hidden;profileButton.setAttribute('aria-expanded',String(!profile.hidden));if(!profile.hidden)profile.querySelector('button').focus()};
 root.querySelector('.profile-close').onclick=()=>{closeProfile();profileButton.focus()};
 const outside=e=>{if(!profile.hidden&&!profile.contains(e.target)&&!profileButton.contains(e.target))closeProfile()};
 const keys=e=>{if(e.key==='Escape'){if(!profile.hidden){closeProfile();profileButton.focus()}else if(doc.dataset.drawer==='open')closeDrawer()}
  if(e.key==='Tab'&&mobile()&&doc.dataset.drawer==='open'){const items=[...aside.querySelectorAll('button,select,a')].filter(e=>e.getClientRects().length&&!e.closest('[hidden]'));const first=items[0],last=items.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}};
 document.addEventListener('keydown',keys);document.addEventListener('pointerdown',outside);
 // Move focus to the new page's heading only after an intentional route change.
 let timer;if(window.__civicRouteFocus){timer=setTimeout(()=>{const h=document.querySelector('h1');if(h){h.tabIndex=-1;h.focus({preventScroll:true});document.querySelector('[data-testid="stMain"]')?.scrollTo({top:0});}window.__civicRouteFocus=false},250)}
 const cleanup=()=>{root.remove();clearTimeout(timer);media.removeEventListener('change',appearance);window.removeEventListener('resize',resize);document.removeEventListener('keydown',keys);document.removeEventListener('pointerdown',outside)};
 window.__civicCleanup=cleanup;return cleanup;
}

