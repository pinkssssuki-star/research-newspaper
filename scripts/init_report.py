"""Create a clean independent newspaper. Never overwrite an existing path."""
import argparse
import datetime as dt
import json
import shutil
from pathlib import Path


def initialize(output,topic,focus,timezone,date,language='zh-CN'):
    output=Path(output).resolve()
    if output.exists():
        raise FileExistsError('Output already exists; select the existing newspaper instead of reinitializing it')
    dt.date.fromisoformat(date)
    if not topic.strip() or not focus.strip():
        raise ValueError('Topic and reader focus are required')
    # --date is authoritative client-local date; do not silently substitute host timezone.
    template=Path(__file__).resolve().parents[1]/'assets/report'
    shutil.copytree(template,output)
    (output/'data/editions').mkdir(parents=True)
    (output/'assets').mkdir()
    def save(name,value):
        (output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    save('profile.json',dict(title=topic+'日报',topic=topic,readerFocus=focus,timezone=timezone,language=language,windowDays=7,historyDays=30,outputPolicy='local',trigger='出版一下今天的报纸'))
    save('data/catalog.json',dict(schemaVersion=1,title=topic+'日报',asOf=date,timezone=timezone,datePolicy='Preserve source event dates; separate first publication, updates, discovery and review dates.',organizations=[],technologies=[],works=[]))
    save('data/organization-profiles.json',{})
    save('data/classifications.json',{})
    save('data/reviews-current.json',{})
    save('data/abstracts.json',{})
    save('data/taxonomy.json',dict(model=['待确认研究对象分类'],workType=['模型 / 方法','Benchmark','数据集','系统 / 平台','分析 / 观点'],embodiment=['待确认应用设置分类']))
    save('data/research-journal.json',dict(startedOn=date,statements=[],forecasts=[],evaluations=[],labDirections=[],workflow=[dict(title='证据与比较',text='核验一手材料、日期、基线、适配与成本，保留反例和阅读深度。'),dict(title='趋势与复盘',text='对照历史判断，追加新版本；按提前登记条件复核预测，记录教训与下次检查。')]))
    (output/'AGENTS.md').write_text('''# Daily newspaper maintenance

Trigger: 出版一下今天的报纸

Read profile.json, data/catalog.json, reviews-*.json, all existing editions and data/research-journal.json before updating. Follow the research-newspaper skill (SKILL.md and its references). If that skill is not installed, stop and locate it rather than silently omitting the evidence/review/memory workflow.

Use the profile timezone and trusted current client date. Research primary sources, deduplicate stable work IDs, preserve event/discovery dates, review depth and independent source clusters. Add classification, abstract, baselines, comparison conditions, fair usefulness judgment, improvement attribution with uncertainty, costs and sources for every work. Keep registered issues/statements/forecasts/evaluations unchanged; add new IDs/versions. Never delete the SQLite database to bypass history checks. Same-day revisions use edition id plus numeric revision. No additions is valid and should be explained in edition notes.

Maintain data/abstracts.json with the original paper Abstract, its full selected-language translation, exact source version and verification date; preserve qualifications, negative results and availability claims. Check official releases for companion papers. Label missing/inaccessible Abstracts explicitly. Keep editorialSummaryZh separate from the translation; the legacy abstractZh field was an editorial paraphrase and must not be promoted to a translation. Daily work-detail dialogs must include the translation/original, baselines, usefulness, experimental conditions/techniques, attribution and cost. Statistics reuses the same src/work-view.js card/detail renderer and figures. Display/metadata corrections alone preserve prior editions and forecasts without inventing a new issue.

Review pending and overdue forecasts, counterevidence and prior lessons each day. Do not backdate predictions or count old events as new hits. Resolve only against the preregistered rules, documenting coverage, errorType, lesson and nextCheck. Rates exclude pending/unresolved/retracted predictions.

Run python build.py and python check_report.py; check all five pages, old editions, filters, figures and phone layout when browser tools are available. Confirm the same work has matching complete details in the daily and statistics pages, original-text expansion and clear missing-Abstract labels. Preserve JSON and SQLite. Serving locally is optional; no external publishing, automatic schedule, or LAN service is implied by the trigger.
''',encoding='utf8')
    print(output)
    return output


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for field in ['output','topic','focus','timezone','date']:
        p.add_argument('--'+field,required=True)
    p.add_argument('--language',default='zh-CN')
    a=p.parse_args()
    initialize(a.output,a.topic,a.focus,a.timezone,a.date,a.language)
