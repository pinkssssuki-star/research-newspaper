'use strict';
let RESEARCH=JSON.parse(document.getElementById('analysisData').textContent);
let workView;
let lastFocus=null;
const el=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const href=u=>{try{const p=new URL(u);return p.protocol==='https:'?esc(p.href):'#'}catch{return '#'}};
const list=a=>`<ul>${a.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`;
const metric=(n,t)=>`<div><strong>${esc(n)}</strong><span>${esc(t)}</span></div>`;
function workLink(id){const w=RESEARCH.catalog.works.find(x=>x.id===id);return w?`<a class="evidence-link" href="statistics.html#${encodeURIComponent(id)}">${esc(w.short)} ↗</a>`:''}
function select(id,values){const previous=el(id).value;el(id).innerHTML='<option value="all">全部</option>'+values.map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join('');if(values.includes(previous))el(id).value=previous}
function initialize(){
 const d=RESEARCH.catalog,t=RESEARCH.taxonomy;
 workView=createWorkView(d,RESEARCH.reviews,()=>d.asOf);
 select('modelFilter',t.model);select('typeFilter',t.workType);select('bodyFilter',t.embodiment);select('topicFilter',[...new Set(d.works.flatMap(w=>w.tags))]);
 el('asof').textContent=`截至 ${d.asOf} / ${d.timezone}`;
 renderStats();renderTrends();
}
function renderBars(id,key,works){const values=RESEARCH.taxonomy[key];el(id).innerHTML=values.map(v=>{const n=works.filter(w=>w.classification[key].includes(v)).length;return `<div class="bar-row"><span>${esc(v)}</span><div class="bar-track"><div class="bar-fill" style="width:${works.length?n/works.length*100:0}%"></div></div><b>${n}</b></div>`}).join('')}
function renderStats(){
 const d=RESEARCH.catalog,q=el('researchSearch').value.trim().toLowerCase(),period=el('periodFilter').value;
 const filters=[['modelFilter','model'],['typeFilter','workType'],['bodyFilter','embodiment']];
 const works=d.works.filter(w=>filters.every(([id,key])=>el(id).value==='all'||w.classification[key].includes(el(id).value))&&(el('topicFilter').value==='all'||w.tags.includes(el('topicFilter').value))&&(period==='all'||(!w.datePrecision&&(Date.parse(d.asOf)-Date.parse(w.date))/86400000<Number(period)))&&[w.short,w.title,w.summary,RESEARCH.reviews[w.id].abstract.translationZh||'',RESEARCH.reviews[w.id].editorialSummaryZh,...w.orgIds.map(id=>d.organizations.find(o=>o.id===id)?.short||''),...RESEARCH.reviews[w.id].baselines.map(b=>b.name)].join(' ').toLowerCase().includes(q)).sort((a,b)=>b.date.localeCompare(a.date)||a.short.localeCompare(b.short));
 const full=works.filter(w=>RESEARCH.reviews[w.id].depth==='全文核验').length;
 el('statsMetrics').innerHTML=metric(works.length,'当前筛选工作')+metric(d.works.length,'累计去重工作')+metric(full,'当前筛选已核全文')+metric(RESEARCH.editions.length,'期历史调研');
 renderBars('modelBars','model',works);renderBars('typeBars','workType',works);
 el('resultCount').textContent=`${works.length} 项结果 · 论文摘要为原文全译 · 评价是有依据的编辑判断`;
 el('reviewList').innerHTML=works.length?works.map(w=>workView.card(w)).join(''):'<div class="empty">没有符合这些条件的已收录工作。</div>';
}
function showWork(id){const html=workView.detail(id);if(!html)return;if(!el('detailDialog').open)lastFocus=document.activeElement;el('detailBody').innerHTML=html;el('dialogLabel').textContent='RESEARCH NOTE / '+RESEARCH.catalog.works.find(w=>w.id===id).short;if(!el('detailDialog').open)el('detailDialog').showModal();el('detailDialog').scrollTop=0}
document.addEventListener('click',e=>{const w=e.target.closest('[data-work]');if(w){showWork(w.dataset.work);return}const p=e.target.closest('[data-profile]');if(p){location.href='index.html#org-'+encodeURIComponent(p.dataset.profile);return}const t=e.target.closest('[data-tech]');if(t)location.href='technologies.html#tech-'+encodeURIComponent(t.dataset.tech)});
el('closeDialog').addEventListener('click',()=>el('detailDialog').close());el('detailDialog').addEventListener('close',()=>lastFocus?.focus());el('detailDialog').addEventListener('click',e=>{if(e.target===el('detailDialog')){const r=el('detailDialog').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)el('detailDialog').close()}});
function renderTrends(){
 const j=RESEARCH.journal;
 const latest=new Map();for(const s of j.statements)latest.set(s.topicId,s);
 el('trendMetrics').innerHTML=metric(latest.size,'当前判断主题')+metric(j.forecasts.length,'提前登记预测')+metric(RESEARCH.memory.snapshots,'已存调研快照')+metric(RESEARCH.catalog.works.length,'累计证据工作');
 el('trendCards').innerHTML=[...latest.values()].map(s=>`<article class="trend-card"><div class="meta">${esc(s.createdOn)} · ${esc(s.confidence)} · 版本 ${esc(s.id)}</div><h2>${esc(s.title)}</h2><div class="support"><strong>观察到什么</strong><p>${esc(s.observation)}</p></div><h3>当前解释 / 编辑判断</h3><p>${esc(s.interpretation)}</p><h3>反证与替代解释</h3><p class="counter">${esc(s.counterEvidence)}</p><h3>什么会改变判断</h3><p>${esc(s.reversal)}</p><h3>与上次相比</h3><p>${esc(s.change)}</p><h3>依据</h3>${s.evidenceIds.map(workLink).join('')}${(s.externalSources||[]).map(x=>`<p><a href="${href(x.url)}" target="_blank" rel="noopener noreferrer">${esc(x.label)} ↗</a> · ${esc(x.note)}</p>`).join('')}</article>`).join('');
 el('labDirections').innerHTML=`<div class="review-table-wrap"><table class="review-table"><thead><tr><th>研究问题</th><th>实验室的切入点</th><th>资源／规模瓶颈</th><th>可检验的优势</th></tr></thead><tbody>${j.labDirections.map(x=>`<tr><td>${esc(x.direction)}</td><td>${esc(x.opportunity)}</td><td>${esc(x.bottleneck)}</td><td>${esc(x.test)}</td></tr>`).join('')}</tbody></table></div>`;
 const evaluations=new Map();for(const e of j.evaluations)evaluations.set(e.forecastId,e);
 const resolved=j.forecasts.filter(p=>['hit','miss'].includes(evaluations.get(p.id)?.status));
 const hit=resolved.filter(p=>evaluations.get(p.id).status==='hit').length;
 const brier=resolved.length?resolved.reduce((sum,p)=>sum+(p.probability-(evaluations.get(p.id).status==='hit'?1:0))**2,0)/resolved.length:null;
 el('forecastMetrics').textContent=`已可判定 ${resolved.length} / ${j.forecasts.length}；命中率 ${resolved.length?(hit/resolved.length*100).toFixed(1)+'%':'尚不可计算'}；Brier 分数 ${brier===null?'尚不可计算':brier.toFixed(3)+'（越低越好）'}。不把待观察和无法判定算作失败或命中；样本少时不宣称预测能力改善。`;
 const labels={pending:'待观察',hit:'命中',miss:'未命中',unresolved:'无法判定',retracted:'已撤回'};
 el('forecastList').innerHTML=j.forecasts.map(p=>{const e=evaluations.get(p.id),overdue=RESEARCH.catalog.asOf>p.deadline;const status=e?labels[e.status]:(overdue?'已到期，待核验':'待观察');return `<article class="forecast"><span class="status">${status}</span><div class="meta">登记 ${esc(p.createdOn)} → 截止 ${esc(p.deadline)} · 主观概率 ${(p.probability*100).toFixed(0)}%</div><h3>${esc(p.claim)}</h3><p><strong>命中条件：</strong>${esc(p.successRule)}</p><p><strong>排除规则：</strong>${esc(p.exclusions)}</p><p><strong>未命中／不可判定：</strong>${esc(p.failureRule)}</p><p><strong>登记时依据：</strong>${p.evidenceIds.map(workLink).join('')}</p><p class="analysis-note">${esc(e?.rationale||'尚无后续新证据用于结算。原有论文不能作为这项新预测的命中证据。')}</p>${e?e.evidenceIds.map(workLink).join(''):''}<details><summary>查看这项预测的全部复盘记录</summary>${j.evaluations.filter(x=>x.forecastId===p.id).map(x=>`<p>${esc(x.evaluatedOn)} · ${labels[x.status]} · ${esc(x.rationale)}</p>`).join('')||'<p class="analysis-note">暂无复盘记录。</p>'}</details></article>`}).join('');
 el('historicalNotes').innerHTML=RESEARCH.editions.map(e=>`<div class="history-note"><strong>${esc(e.date)} · 原日报观察</strong>${e.notes.filter(n=>/判断|课题|事实/.test(n.label)).map(n=>`<p class="analysis-note">${esc(n.label)}：${esc(n.text)}</p>`).join('')}<p class="analysis-note">作为原始历史材料导入；不是当时登记的可评分预测。</p></div>`).join('')+j.statements.map(s=>`<p class="analysis-note">${esc(s.id)} · ${esc(s.createdOn)} · ${esc(s.change)}</p>`).join('');
 el('memoryWorkflow').innerHTML=j.workflow.map((x,i)=>`<div class="memory-step"><b>${String(i+1).padStart(2,'0')}</b><div><strong>${esc(x.title)}</strong><p>${esc(x.text)}</p></div></div>`).join('');
 document.querySelectorAll('#forecastList .forecast').forEach((article,i)=>{
  const reflections=j.evaluations.filter(e=>e.forecastId===j.forecasts[i].id&&e.lesson);
  if(reflections.length)article.insertAdjacentHTML('beforeend',`<h4>判断复盘与下次检查</h4>${reflections.map(e=>`<p class="analysis-note">${esc(e.evaluatedOn)} · ${esc(e.errorType)}<br>经验：${esc(e.lesson)}<br>下次核查：${esc(e.nextCheck)}</p>`).join('')}`);
 });
 el('memoryHistory').innerHTML=`<p>${RESEARCH.memory.backend} · 研究记忆启用 ${esc(j.startedOn)} · ${RESEARCH.memory.revisions} 条版本记录。写入由本地构建流程完成；接口只读，不使用浏览器缓存代替后端。</p>`;
}
for(const id of ['modelFilter','typeFilter','bodyFilter','topicFilter','periodFilter'])el(id).addEventListener('change',renderStats);
el('researchSearch').addEventListener('input',renderStats);
el('resetFilters').addEventListener('click',()=>{for(const id of ['modelFilter','typeFilter','bodyFilter','topicFilter','periodFilter'])el(id).value='all';el('researchSearch').value='';renderStats()});
el('exportAnalysis').addEventListener('click',()=>{const u=URL.createObjectURL(new Blob([JSON.stringify(RESEARCH,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=u;a.download=`embodied-memory-${RESEARCH.catalog.asOf}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)});
const trends=location.pathname.endsWith('trends.html');el('statsPage').hidden=trends;el('trendsPage').hidden=!trends;el(trends?'trendsNav':'statsNav').classList.add('active');el(trends?'trendsNav':'statsNav').setAttribute('aria-current','page');document.title=(trends?'趋势判断':'研究统计')+' · 研究日报';
initialize();
function showConnection(text){el('connectionState').textContent=text;el('trendConnection').textContent=text}
showConnection('离线阅读快照 · 数据和判断已保存在本地 SQLite；最新收录截至 '+RESEARCH.catalog.asOf);
if(location.protocol==='http:'&&['127.0.0.1','localhost'].includes(location.hostname)){
 fetch('/api/research').then(r=>{if(!r.ok)throw Error('Unavailable');return r.json()}).then(data=>{if(!data.catalog||!data.reviews||!data.journal||!data.taxonomy)throw Error('Incomplete');const images=new Map(RESEARCH.catalog.works.map(w=>[w.id,w.image]));for(const w of data.catalog.works){const saved=images.get(w.id);if(saved?.local===w.image?.local&&saved?.src)w.image={...w.image,src:saved.src}}RESEARCH={...RESEARCH,...data};initialize();showConnection('已连接本地 SQLite · 读取最新构建快照 · 截至 '+RESEARCH.catalog.asOf);jumpToWork()}).catch(()=>showConnection('当前为页面内快照 · 本地数据库接口未连接；可正常阅读已生成内容')).finally(()=>fetch('/api/history').then(r=>r.ok?r.json():null).then(h=>{if(h)el('memoryHistory').innerHTML+=`<p>${h.snapshots.map(s=>`${esc(s.as_of)} · ${esc(s.origin)} · 写入 ${esc(s.recorded_at)}<br>`).join('')}</p>`}).catch(()=>{}));
}
function jumpToWork(){const id=decodeURIComponent(location.hash.slice(1));if(id&&RESEARCH.catalog.works.some(w=>w.id===id))showWork(id)}
window.addEventListener('hashchange',jumpToWork);jumpToWork();
