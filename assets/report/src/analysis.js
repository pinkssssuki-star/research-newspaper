'use strict';
let RESEARCH=JSON.parse(document.getElementById('analysisData').textContent);
const el=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const href=u=>{try{const p=new URL(u);return p.protocol==='https:'?esc(p.href):'#'}catch{return '#'}};
const chip=t=>`<span class="pill">${esc(t)}</span>`;
const list=a=>`<ul>${a.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`;
const metric=(n,t)=>`<div><strong>${esc(n)}</strong><span>${esc(t)}</span></div>`;
function workLink(id){const w=RESEARCH.catalog.works.find(x=>x.id===id);return w?`<a class="evidence-link" href="statistics.html#${encodeURIComponent(id)}">${esc(w.short)} ↗</a>`:''}
function select(id,values){const previous=el(id).value;el(id).innerHTML='<option value="all">全部</option>'+values.map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join('');if(values.includes(previous))el(id).value=previous}
function initialize(){
 const d=RESEARCH.catalog,t=RESEARCH.taxonomy;
 select('modelFilter',t.model);select('typeFilter',t.workType);select('bodyFilter',t.embodiment);select('topicFilter',[...new Set(d.works.flatMap(w=>w.tags))]);
 el('asof').textContent=`截至 ${d.asOf} / ${d.timezone}`;
 renderStats();renderTrends();
}
function renderBars(id,key,works){const values=RESEARCH.taxonomy[key];el(id).innerHTML=values.map(v=>{const n=works.filter(w=>w.classification[key].includes(v)).length;return `<div class="bar-row"><span>${esc(v)}</span><div class="bar-track"><div class="bar-fill" style="width:${works.length?n/works.length*100:0}%"></div></div><b>${n}</b></div>`}).join('')}
function renderStats(){
 const d=RESEARCH.catalog,q=el('researchSearch').value.trim().toLowerCase(),period=el('periodFilter').value;
 const filters=[['modelFilter','model'],['typeFilter','workType'],['bodyFilter','embodiment']];
 const works=d.works.filter(w=>filters.every(([id,key])=>el(id).value==='all'||w.classification[key].includes(el(id).value))&&(el('topicFilter').value==='all'||w.tags.includes(el('topicFilter').value))&&(period==='all'||(!w.datePrecision&&(Date.parse(d.asOf)-Date.parse(w.date))/86400000<Number(period)))&&[w.short,w.title,w.summary,RESEARCH.reviews[w.id].abstractZh,...w.orgIds.map(id=>d.organizations.find(o=>o.id===id)?.short||''),...RESEARCH.reviews[w.id].baselines.map(b=>b.name)].join(' ').toLowerCase().includes(q)).sort((a,b)=>b.date.localeCompare(a.date)||a.short.localeCompare(b.short));
 const full=works.filter(w=>RESEARCH.reviews[w.id].depth==='全文核验').length;
 el('statsMetrics').innerHTML=metric(works.length,'当前筛选工作')+metric(d.works.length,'累计去重工作')+metric(full,'当前筛选已核全文')+metric(RESEARCH.editions.length,'期历史调研');
 renderBars('modelBars','model',works);renderBars('typeBars','workType',works);
 el('resultCount').textContent=`${works.length} 项结果 · 摘要为中文转述 · 评价是有依据的编辑判断`;
 el('reviewList').innerHTML=works.length?works.map(w=>renderReview(w,RESEARCH.reviews[w.id])).join(''):'<div class="empty">没有符合这些条件的已收录工作。</div>';
}
function renderReview(w,r){
 const c=w.classification;
 const baselineRows=r.baselines.map(b=>`<tr><td>${esc(b.name)}</td><td>${esc(b.setting)}</td><td>${esc(b.result)}</td><td><a href="${href(b.sourceUrl)}" target="_blank" rel="noopener noreferrer">原始依据 ↗</a></td></tr>`).join('')||'<tr><td colspan="4">本次核验未找到可报告的统一对照基线；产品公告或数据管线不据演示认定性能胜出。具体证据范围见下方来源。</td></tr>';
 return `<article id="${esc(w.id)}" class="review-item"><div class="meta">${esc(w.date)} · ${esc(w.dateType)} · <span class="status">${esc(r.depth)}</span> · 核验 ${esc(r.reviewedAt)}</div><h2>${esc(w.short)} · ${esc(w.headline)}</h2><div class="review-tags">${c.model.map(chip).join('')}${c.workType.map(chip).join('')}${c.embodiment.map(chip).join('')}</div><p class="analysis-note">${esc(w.title)}<br>分类依据：${esc(c.basis)}</p><p class="review-abstract"><strong>摘要：</strong>${esc(r.abstractZh)}</p><div class="review-judgment"><p><strong>实际价值：</strong>${esc(r.verdict)}</p><p><strong>结论与结果：</strong>${esc(r.resultSummary)}</p></div><details><summary>展开基线、实验条件与提升归因</summary><h3>比较了哪些基线？</h3><div class="review-table-wrap"><table class="review-table"><thead><tr><th>基线 / 对照</th><th>比较设置</th><th>结果与口径</th><th>出处</th></tr></thead><tbody>${baselineRows}</tbody></table></div><h3>哪些条件会影响比较？</h3>${r.conditions.map(x=>`<p><strong>${esc(x.factor)}：</strong>${esc(x.observation)}<br><span class="analysis-note">影响：${esc(x.impact)}</span></p>`).join('')}<h3>为什么基线落后，或为什么不能说落后？</h3><p>${esc(r.bestBaselineReason)}</p><div class="callout"><p><strong>主要提升来源 / ${esc(r.attribution.confidence)}：</strong>${esc(r.attribution.main)}</p><p><strong>支持证据：</strong>${esc(r.attribution.evidence)}</p><p><strong>尚不能归因：</strong>${esc(r.attribution.unresolved)}</p></div><h3>成本与复用限制</h3><p>${esc(r.cost)}</p><p>${esc(w.limits)}</p><h3>可回查的依据</h3><div class="source-provenance">${r.sources.map(s=>`<p><a href="${href(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.label)} ↗</a><br><span class="analysis-note">定位：${esc(s.locator)}</span></p>`).join('')}</div><p class="analysis-note">“额外条件”不等于作弊；未报告不等于未做。没有同条件实验时不把数据、架构、领域适配的作用强行分成百分比。${esc(r.depth)}表示本次实际审读范围，不代表独立复现。</p></details></article>`;
}
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
 fetch('/api/research').then(r=>{if(!r.ok)throw Error('Unavailable');return r.json()}).then(data=>{if(!data.catalog||!data.reviews||!data.journal||!data.taxonomy)throw Error('Incomplete');RESEARCH={...RESEARCH,...data};initialize();showConnection('已连接本地 SQLite · 读取最新构建快照 · 截至 '+RESEARCH.catalog.asOf);jumpToWork()}).catch(()=>showConnection('当前为页面内快照 · 本地数据库接口未连接；可正常阅读已生成内容')).finally(()=>fetch('/api/history').then(r=>r.ok?r.json():null).then(h=>{if(h)el('memoryHistory').innerHTML+=`<p>${h.snapshots.map(s=>`${esc(s.as_of)} · ${esc(s.origin)} · 写入 ${esc(s.recorded_at)}<br>`).join('')}</p>`}).catch(()=>{}));
}
function jumpToWork(){const id=decodeURIComponent(location.hash.slice(1));if(id&&el(id))el(id).scrollIntoView({block:'start'})}
window.addEventListener('hashchange',jumpToWork);jumpToWork();
