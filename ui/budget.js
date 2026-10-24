export default function({parentElement,data,setStateValue}){
 const input=parentElement.querySelector('input'),error=parentElement.querySelector('[role=alert]');
 let committed=data.committed;input.value=data.value;
 const valid=value=>/^\d+(?:\.\d{0,7})?$/.test(value)&&Number(value)<=100;
 const previewButtons=()=>[...document.querySelectorAll('button')].filter(button=>button.textContent.trim()==='Run optimisation');
 const syncButton=()=>previewButtons().forEach(button=>{button.disabled=!valid(input.value.trim())});
 if(!valid(input.value)){error.textContent='Enter 0-100 crore using a period; up to 7 decimal places.';input.setAttribute('aria-invalid','true')}
 const clear=()=>{error.textContent='';input.removeAttribute('aria-invalid')};
 const commit=()=>{const value=input.value.trim();let message='';
 if(!/^\d+(?:\.\d{0,7})?$/.test(value))message='Use a period, with up to 7 decimal places (whole INR).';
 else if(Number(value)>100)message='Enter a budget from 0 to 100 crore.';
 if(message){error.textContent=message;input.setAttribute('aria-invalid','true');syncButton();return}
 clear();if(value!==committed){committed=value;setStateValue('value',value)}};
 const edit=()=>{clear();syncButton()};
 input.addEventListener('blur',commit);input.addEventListener('input',edit);
 input.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();commit()}if(e.key==='Escape'){e.preventDefault();input.value=committed;clear();setStateValue('value',committed)}});
 const observer=new MutationObserver(syncButton);observer.observe(document.body,{childList:true,subtree:true});syncButton();
 return()=>observer.disconnect();
}
