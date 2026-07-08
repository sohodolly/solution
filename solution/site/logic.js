let user = JSON.parse(localStorage.getItem('sol_u') || 'null');
renderNav();

// ──────── CURSOR ────────
const $cur=document.getElementById('cur'),ring=document.getElementById('curring');
let mx=-200,my=-200,rx=-200,ry=-200;
document.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY;$cur.style.left=mx+'px';$cur.style.top=my+'px'});
(function loop(){rx+=(mx-rx)*.11;ry+=(my-ry)*.11;ring.style.left=rx+'px';ring.style.top=ry+'px';requestAnimationFrame(loop)})();
document.querySelectorAll('a,button,.hstep,.rcard,.pplan,.plan').forEach(el=>{
  el.addEventListener('mouseenter',()=>{ring.style.width='44px';ring.style.height='44px';ring.style.borderColor='rgba(0,212,255,.7)'});
  el.addEventListener('mouseleave',()=>{ring.style.width='28px';ring.style.height='28px';ring.style.borderColor='rgba(0,212,255,.35)'});
});

// ──────── TOAST ────────
let tt;
function toast(msg,type='b'){
  const el=document.getElementById('toast');
  document.getElementById('tmsg').textContent=msg;
  document.getElementById('tdot').className='tdot '+type;
  el.classList.add('on');clearTimeout(tt);
  tt=setTimeout(()=>el.classList.remove('on'),3200);
}

// ──────── MODALS ────────
function openM(id){document.getElementById(id).classList.add('open');document.body.classList.add('no-scroll')}
function closeM(id){
  document.getElementById(id).classList.remove('open');document.body.classList.remove('no-scroll');
  if(id==='auth-bd'){resetAuth()}
}
document.querySelectorAll('.backdrop').forEach(b=>b.addEventListener('click',e=>{if(e.target===b)closeM(b.id)}));

function resetAuth(){
  document.getElementById('asuc').classList.remove('on');
  document.getElementById('lform').style.display='';document.getElementById('rform').style.display='none';
  document.getElementById('atabs').style.display='';
  clearErrs();
}
function clearErrs(){document.querySelectorAll('.ferr').forEach(e=>e.classList.remove('on'));document.querySelectorAll('.fi').forEach(e=>e.classList.remove('err'))}

// ──────── AUTH TABS ────────
function setTab(t){
  const isL=t==='login';
  document.getElementById('tlogin').classList.toggle('on',isL);
  document.getElementById('treg').classList.toggle('on',!isL);
  document.getElementById('lform').style.display=isL?'':'none';
  document.getElementById('rform').style.display=isL?'none':'';
  document.getElementById('albl').textContent=isL?'АВТОРИЗАЦИЯ':'РЕГИСТРАЦИЯ';
  document.getElementById('atitle').textContent=isL?'Войти в систему':'Создать аккаунт';
  clearErrs();
}

// ──────── LOGIN ────────
function doLogin(){
  clearErrs();
  const e = document.getElementById('le').value.trim();
  const p = document.getElementById('lp').value.trim();
  let ok = true;
  if(!e || !e.includes('@')){ mark('le','le-e'); ok=false; }
  if(!p){ mark('lp','lp-e'); ok=false; }
  if(!ok) return;
  
  const btn = document.getElementById('lbtn');
  btn.disabled = true;
  btn.textContent = 'Проверяем...';
  
  setTimeout(() => {
    const users = JSON.parse(localStorage.getItem('sol_users') || '[]');
    const found = users.find(u => u.email === e && u.pass === p);
    if(!found){
      document.getElementById('lp-e').textContent = 'Неверный email или пароль';
      mark('lp','lp-e');
      btn.disabled = false;
      btn.textContent = 'Войти';
      return;
    }
    user = { name: found.name, email: found.email, premium: found.premium || false };
    localStorage.setItem('sol_u', JSON.stringify(user));
    showAuthSuc('Добро пожаловать, ' + found.name + '!', 'Сеанс активирован.');
    renderNav();
    btn.disabled = false;
    btn.textContent = 'Войти';
  }, 800);
}

// ──────── REGISTER ────────
function doReg(){
  clearErrs();
  const n = document.getElementById('rn').value.trim();
  const e = document.getElementById('re').value.trim();
  const p = document.getElementById('rp').value.trim();
  const p2 = document.getElementById('rp2').value.trim();
  let ok = true;
  if(n.length < 3){ mark('rn','rn-e'); ok=false; }
  if(!e || !e.includes('@')){ mark('re','re-e'); ok=false; }
  if(p.length < 6){ mark('rp','rp-e'); ok=false; }
  if(p !== p2){ mark('rp2','rp2-e'); ok=false; }
  if(!ok) return;
  
  const btn = document.getElementById('rbtn');
  btn.disabled = true;
  btn.textContent = 'Создаём...';
  
  setTimeout(() => {
    const users = JSON.parse(localStorage.getItem('sol_users') || '[]');
    if(users.find(u => u.email === e)){
      document.getElementById('re-e').textContent = 'Email уже используется';
      mark('re','re-e');
      btn.disabled = false;
      btn.textContent = 'Создать аккаунт';
      return;
    }
    users.push({ name: n, email: e, pass: p, premium: false });
    localStorage.setItem('sol_users', JSON.stringify(users));
    user = { name: n, email: e, premium: false };
    localStorage.setItem('sol_u', JSON.stringify(user));
    showAuthSuc('Аккаунт создан, ' + n + '!', 'Добро пожаловать в SOLUTION.');
    renderNav();
    btn.disabled = false;
    btn.textContent = 'Создать аккаунт';
  }, 900);
}

function mark(inpId,errId){document.getElementById(inpId).classList.add('err');document.getElementById(errId).classList.add('on')}

function showAuthSuc(h,s){
  document.getElementById('lform').style.display='none';document.getElementById('rform').style.display='none';
  document.getElementById('atabs').style.display='none';
  document.getElementById('asuc-h').textContent=h;document.getElementById('asuc-s').textContent=s;
  document.getElementById('asuc').classList.add('on');
  setTimeout(()=>{closeM('auth-bd');toast('Вы вошли в аккаунт','b')},1800);
}

// ──────── LOGOUT ────────
function doLogout(){user=null;localStorage.removeItem('sol_u');renderNav();closeDrop();toast('Выход выполнен','b')}

// ──────── NAV RENDER ────────
function renderNav(){
  const g=document.getElementById('nav-guest'),u=document.getElementById('nav-user');
  if(user){
    g.style.display='none';u.style.display='';
    const init=(user.name||'?').slice(0,2).toUpperCase();
    document.getElementById('navav').textContent=init;
    document.getElementById('navun').textContent=user.name;
    document.getElementById('dname').textContent=user.name;
    document.getElementById('demail').textContent=user.email;
    const badge=document.getElementById('navbadge'),pb=document.getElementById('dprem'),mb=document.getElementById('dmanage');
    if(user.premium){badge.style.display='';pb.style.display='none';mb.style.display=''}
    else{badge.style.display='none';pb.style.display='';mb.style.display='none'}
  }else{g.style.display='';u.style.display='none'}
}

// ──────── DROPDOWN ────────
function toggleDrop(){document.getElementById('userwrap').classList.toggle('open')}
function closeDrop(){document.getElementById('userwrap').classList.remove('open')}
document.addEventListener('click',e=>{const w=document.getElementById('userwrap');if(w&&!w.contains(e.target))closeDrop()});

// ──────── PREMIUM / PRO ────────
function openPrem(){
  if(!user){openM('auth-bd');toast('Войдите чтобы оформить Premium','b');return}
  closeDrop();showPlans();openM('prem-bd');
}
function openPremPro(){
  if(!user){openM('auth-bd');toast('Войдите чтобы оформить PRO','b');return}
  closeDrop();showPlans();openM('prem-bd');
}
function showPay(){document.getElementById('plans-view').style.display='none';document.getElementById('payform').classList.add('on');document.getElementById('payform-pro').classList.remove('on')}
function showPayPro(){document.getElementById('plans-view').style.display='none';document.getElementById('payform-pro').classList.add('on');document.getElementById('payform').classList.remove('on')}
function showPlans(){document.getElementById('plans-view').style.display='';document.getElementById('payform').classList.remove('on');document.getElementById('payform-pro').classList.remove('on')}

function fmtCard(el){let v=el.value.replace(/\D/g,'').slice(0,16);el.value=v.replace(/(.{4})/g,'$1 ').trim()}
function fmtExp(el){let v=el.value.replace(/\D/g,'');if(v.length>2)v=v.slice(0,2)+'/'+v.slice(2,4);el.value=v}

function doPay(){
  document.querySelectorAll('.payform .ferr').forEach(e=>e.classList.remove('on'));
  document.querySelectorAll('.payform .fi').forEach(e=>e.classList.remove('err'));
  const c=document.getElementById('pc').value.replace(/\s/g,''),e=document.getElementById('pe').value,v=document.getElementById('pv').value;
  let ok=true;
  if(c.length!==16){mark('pc','pc-e');ok=false}
  if(!e.match(/^\d{2}\/\d{2}$/)){mark('pe','pe-e');ok=false}
  if(v.length!==3){mark('pv','pv-e');ok=false}
  if(!ok)return;
  const btn=document.getElementById('paybtn');btn.disabled=true;btn.textContent='Обрабатываем...';
  setTimeout(()=>{
    user.premium=true;localStorage.setItem('sol_u',JSON.stringify(user));
    const users=JSON.parse(localStorage.getItem('sol_users')||'[]');
    const uu=users.find(u=>u.email===user.email);if(uu)uu.premium=true;
    localStorage.setItem('sol_users',JSON.stringify(users));
    renderNav();closeM('prem-bd');
    toast('🎉 Premium активирован!','g');
    btn.disabled=false;btn.textContent='Оплатить · $100 / мес';
    ['pn','pc','pe','pv'].forEach(id=>{const el=document.getElementById(id);if(el)el.value=''});
  },1400);
}

function doPayPro(){
  document.querySelectorAll('#payform-pro .ferr').forEach(e=>e.classList.remove('on'));
  document.querySelectorAll('#payform-pro .fi').forEach(e=>e.classList.remove('err'));
  const c=document.getElementById('pc-pro').value.replace(/\s/g,'');
  const e=document.getElementById('pe-pro').value;
  const v=document.getElementById('pv-pro').value;
  let ok=true;
  if(c.length!==16){mark('pc-pro','pc-pro-e');ok=false}
  if(!e.match(/^\d{2}\/\d{2}$/)){mark('pe-pro','pe-pro-e');ok=false}
  if(v.length!==3){mark('pv-pro','pv-pro-e');ok=false}
  if(!ok)return;
  const btn=document.getElementById('paybtn-pro');btn.disabled=true;btn.textContent='Обрабатываем...';
  setTimeout(()=>{
    user.premium=true; // PRO даёт те же права, что и Premium (можно расширить)
    localStorage.setItem('sol_u',JSON.stringify(user));
    const users=JSON.parse(localStorage.getItem('sol_users')||'[]');
    const uu=users.find(u=>u.email===user.email);if(uu)uu.premium=true;
    localStorage.setItem('sol_users',JSON.stringify(users));
    renderNav();closeM('prem-bd');
    toast('🎉 PRO активирован!','g');
    btn.disabled=false;btn.textContent='Оплатить · $50 / мес';
    ['pn-pro','pc-pro','pe-pro','pv-pro'].forEach(id=>{const el=document.getElementById(id);if(el)el.value=''});
  },1400);
}

// ──────── NEURAL CANVAS (оптимизирован) ────────
const canvas=document.getElementById('nc'),ctx=canvas.getContext('2d');
let W,H,nodes=[];
function rsz(){W=canvas.width=canvas.offsetWidth;H=canvas.height=canvas.offsetHeight}
rsz();window.addEventListener('resize',rsz);
// Уменьшено количество узлов с 55 до 22 для экономии ресурсов
for(let i=0;i<22;i++)nodes.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.4,vy:(Math.random()-.5)*.4,r:Math.random()*2+1});
(function draw(){
  ctx.clearRect(0,0,W,H);
  for(let i=0;i<nodes.length;i++){
    const n=nodes[i];n.x+=n.vx;n.y+=n.vy;
    if(n.x<0||n.x>W)n.vx*=-1;if(n.y<0||n.y>H)n.vy*=-1;
    // Уменьшена дистанция для связей с 130 до 100 для снижения нагрузки
    for(let j=i+1;j<nodes.length;j++){const m=nodes[j],d=Math.hypot(n.x-m.x,n.y-m.y);if(d<100){ctx.beginPath();ctx.strokeStyle=`rgba(61,139,255,${.10*(1-d/100)})`;ctx.lineWidth=.5;ctx.moveTo(n.x,n.y);ctx.lineTo(m.x,m.y);ctx.stroke()}}
    ctx.beginPath();ctx.arc(n.x,n.y,n.r,0,Math.PI*2);ctx.fillStyle='rgba(61,139,255,.4)';ctx.fill();
  }
  requestAnimationFrame(draw);
})();

// ──────── SCROLL REVEAL ────────
const obs=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('on');obs.unobserve(e.target)}}),{threshold:.1,rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.rv,.rvl,.rvr,.rvs').forEach(el=>obs.observe(el));

// ──────── NAV BLUR ────────
const nav=document.getElementById('mainnav');
window.addEventListener('scroll',()=>{
  if(window.scrollY>60){nav.style.backdropFilter='blur(16px)';nav.style.background='rgba(5,5,7,.92)'}
  else{nav.style.backdropFilter='none';nav.style.background='var(--black)'}
});

// ──────── PHONE ANIM ────────
const msgs=['Я думаю о тебе каждый день.','Ты изменился. Это хорошо.','Помню, как мы смеялись тогда...','Не вини себя. Я не виню.'];
let mi=0;const amsg=document.getElementById('amsg');
setInterval(()=>{mi=(mi+1)%msgs.length;amsg.style.opacity='0';amsg.style.transition='opacity .4s';setTimeout(()=>{amsg.textContent=msgs[mi];amsg.style.opacity='1'},400)},3500);

// ===== МОБИЛЬНОЕ МЕНЮ =====
const burger = document.getElementById('burgerBtn');
const navLinks = document.querySelector('.nav-links');
if (burger && navLinks) {
  burger.addEventListener('click', (e) => {
    e.stopPropagation();
    navLinks.classList.toggle('open');
    burger.classList.toggle('open');
  });
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
      burger.classList.remove('open');
    });
  });
  document.addEventListener('click', (e) => {
    if (!navLinks.contains(e.target) && !burger.contains(e.target)) {
      navLinks.classList.remove('open');
      burger.classList.remove('open');
    }
  });
}

// ===== ПЕРЕКЛЮЧЕНИЕ ТАБОВ ЗАГРУЗКИ =====
const tabs = document.querySelectorAll('.dl-tab');
const btns = {
  win: document.getElementById('dl-btn-win'),
  mac: document.getElementById('dl-btn-mac'),
  linux: document.getElementById('dl-btn-linux')
};
tabs.forEach(tab => {
  tab.addEventListener('click', function() {
    tabs.forEach(t => t.classList.remove('active'));
    this.classList.add('active');
    const os = this.dataset.os;
    // Скрыть все кнопки
    Object.values(btns).forEach(b => b.style.display = 'none');
    // Показать нужную
    if (os === 'win') btns.win.style.display = 'inline-flex';
    else if (os === 'mac') btns.mac.style.display = 'inline-flex';
    else if (os === 'linux') btns.linux.style.display = 'inline-flex';
  });
});
// По умолчанию активна Windows
document.querySelector('.dl-tab[data-os="win"]')?.classList.add('active');
btns.win.style.display = 'inline-flex';
btns.mac.style.display = 'none';
btns.linux.style.display = 'none';
