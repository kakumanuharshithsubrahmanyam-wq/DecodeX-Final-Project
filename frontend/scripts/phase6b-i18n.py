#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "src/RtgsPortal.tsx"
s = p.read_text()

old_missing = (
    "const missing=[!location.trim()?t('portal.submit.followUpWhere'):null,!date?t('portal.submit.followUpWhen'):null,"
    "!people.trim()?t('portal.submit.followUpWho'):null,!action.trim()?t('portal.submit.followUpAction'):null]"
    ".filter(Boolean) as string[];"
)
new_missing = (
    "const missingFields=(!location.trim()?['location']:[]).concat(!date?['date']:[])"
    ".concat(!people.trim()?['people']:[]).concat(!action.trim()?['action']:[]);"
)
if old_missing in s:
    s = s.replace(old_missing, new_missing)
else:
    print("WARN: missing block not found")

s = s.replace("const [questions,setQuestions]=useState<string[]>([]);", "")

followup_old = (
    '{missing.length>0&&!answered&&<div className="followup-card"><div className="followup-head">'
    '<MessageCircle size={18}/><div><b>A few quick follow-up questions</b><small>These are optional but recommended.'
    "</small></div></div>{missing.map((q,i)=><label className=\"field-label\" key={q}>{q}{q.includes('Where')?"
    '<input value={location} onChange={e=>setLocation(e.target.value)} placeholder="Area, street, landmark"/>'
    ":q.includes('When')?<input type=\"date\" value={date} onChange={e=>setDate(e.target.value)}/>:q.includes('Who')?"
    '<input value={people} onChange={e=>setPeople(e.target.value)} placeholder="People affected"/>:'
    '<input value={action} onChange={e=>setAction(e.target.value)} placeholder="Action requested"/>}'
    "</label>)}<button className=\"btn btn-soft\" onClick={()=>setAnswered(true)}>Done answering</button></div>}"
)
followup_new = (
    "{missingFields.length>0&&!answered&&<div className=\"followup-card\"><div className=\"followup-head\">"
    "<MessageCircle size={18}/><div><b>{t('portal.submit.followUpTitle')}</b><small>{t('portal.submit.followUpHint')}"
    "</small></div></div>{missingFields.map(field=><label className=\"field-label\" key={field}>"
    "{field==='location'?t('portal.submit.followUpWhere'):field==='date'?t('portal.submit.followUpWhen'):"
    "field==='people'?t('portal.submit.followUpWho'):t('portal.submit.followUpAction')}"
    "{field==='location'?<input value={location} onChange={e=>setLocation(e.target.value)} "
    "placeholder={t('portal.submit.locationPh')}/>:field==='date'?<input type=\"date\" value={date} "
    "onChange={e=>setDate(e.target.value)}/>:field==='people'?<input value={people} "
    "onChange={e=>setPeople(e.target.value)} placeholder={t('portal.submit.peoplePh')}/>:"
    "<input value={action} onChange={e=>setAction(e.target.value)} placeholder={t('portal.submit.actionPh')}/>}"
    "</label>)}<button className=\"btn btn-soft\" onClick={()=>setAnswered(true)}>{t('portal.submit.doneAnswering')}"
    "</button></div>}"
)
if followup_old in s:
    s = s.replace(followup_old, followup_new)
else:
    print("WARN: followup block not found")

repls = [
    ("alert('Draft saved in this browser.')", "alert(t('portal.submit.draftSaved'))"),
    ("alert('No saved draft found in this browser.')", "alert(t('portal.submit.draftMissing'))"),
    ("alert('Draft loaded.')", "alert(t('portal.submit.draftLoaded'))"),
    (
        "alert('Speech recognition is not supported in this browser. You can type your complaint instead.')",
        "alert(t('portal.submit.speechUnsupported'))",
    ),
    (
        "setError('Some files were skipped. Only images, PDF or text files up to 8 MB are accepted.')",
        "setError(t('portal.submit.filesSkipped'))",
    ),
    (
        "setError('Please add a title, a description of at least 10 characters, and a location.')",
        "setError(t('portal.submit.validationRequired'))",
    ),
    ("throw new Error('Upload failed')", "throw new Error(t('portal.submit.uploadFailed'))"),
    ("useState('All statuses')", "useState('__all__')"),
    ("useState('All priorities')", "useState('__all__')"),
    ("useState('All categories')", "useState('__all__')"),
    ("status==='All statuses'", "status==='__all__'"),
    ("priority==='All priorities'", "priority==='__all__'"),
    ("category==='All categories'", "category==='__all__'"),
    ('<option value="All statuses">', '<option value="__all__">'),
    ('<option value="All priorities">', '<option value="__all__">'),
    ('<option value="All categories">', '<option value="__all__">'),
    ('placeholder="e.g. Water leakage near apartment gate"', "placeholder={t('portal.submit.titlePh')}"),
    (
        "><small>Use a short title that describes the main issue.</small></label>",
        "><small>{t('portal.submit.titleHint')}</small></label>",
    ),
    (
        'placeholder="Explain what happened, where you noticed it, and how it affects people…"',
        "placeholder={t('portal.submit.descPh')}",
    ),
    ("{voice?'Listening…':'Voice input'}", "{voice?t('portal.submit.voiceListen'):t('portal.submit.voiceBtn')}"),
    (
        "{description.length}/2000 characters · {voice?'Listening for speech…':'Voice input depends on browser support.'}",
        "{description.length}/2000 {t('portal.submit.charCount')} · {voice?t('portal.submit.listeningHint'):t('portal.submit.voiceHint')}",
    ),
    (
        '<label className="field-label">Location <em>*</em>',
        "<label className=\"field-label\">{t('portal.submit.locationLabel')} <em>*</em>",
    ),
    ('placeholder="Area, street, landmark"', "placeholder={t('portal.submit.locationPh')}"),
    ('placeholder="e.g. Residents, pedestrians, school children"', "placeholder={t('portal.submit.peoplePh')}"),
    ('placeholder="e.g. Inspect the pipe and repair the leak"', "placeholder={t('portal.submit.actionPh')}"),
    ("<b>Attach supporting evidence</b>", "<b>{t('portal.submit.uploadEvidence')}</b>"),
    (
        "<span>Drop images or documents here, or <u>browse files</u></span>",
        "<span>{t('portal.submit.uploadDrop')} <u>{t('portal.submit.uploadBrowse')}</u></span>",
    ),
    (
        "<small>PNG, JPG, PDF or TXT · Up to 8 MB each · 5 files max</small>",
        "<small>{t('portal.submit.uploadFormat')}</small>",
    ),
    (
        "<small>{(f.size/1024).toFixed(0)} KB · Local preview only</small>",
        "<small>{(f.size/1024).toFixed(0)} KB · {t('portal.submit.localPreview')}</small>",
    ),
    (" Your draft stays in this browser.", " {t('portal.submit.draftPrivacy')}"),
    ("setQuestions(missing);", ""),
    (">Review details <ArrowRight", ">{t('portal.submit.reviewDetailsBtn')} <ArrowRight"),
    (
        "<p>Rule-based demonstration only — not a real AI service.</p>",
        "<p>{t('portal.submit.reviewRulesNote')}</p>",
    ),
    (
        "score>=85?'Good detail level':score>=50?'A few details could help':'More information recommended'",
        "score>=85?t('portal.submit.goodDetail'):score>=50?t('portal.submit.fewDetail'):t('portal.submit.moreDetail')",
    ),
    (
        "score<100?'Add details where possible to help the demo routing rules.':'All suggested detail fields are filled.'",
        "score<100?t('portal.submit.completenessDemoNote'):t('portal.submit.allFieldsFilled')",
    ),
    (
        "{missing.length===0&&<div className=\"success-banner\"><CheckCircle2 size={17}/> Great — the key details are present.</div>}",
        "{missingFields.length===0&&<div className=\"success-banner\"><CheckCircle2 size={17}/> {t('portal.submit.greatDetails')}</div>}",
    ),
    ('<span className="sim-tag">SIMULATED NLP</span>', "<span className=\"sim-tag\">{t('portal.submit.simNlp')}</span>"),
    ("<small>Category</small>", "<small>{t('portal.submit.categoryLabel')}</small>"),
    ("{CATEGORIES.map(c=><option key={c}>{c}</option>)}", "{CATEGORIES.map(c=><option key={c} value={c}>{labelCategory(t,c)}</option>)}"),
    ("<small>Department</small>", "<small>{t('portal.submit.deptLabel')}</small>"),
    ("<small>Suggested priority</small>", "<small>{t('portal.submit.priorityLabel')}</small>"),
    (
        "{(['Critical','High','Medium','Low'] as Priority[]).map(p=><option key={p}>{p}</option>)}",
        "{(['Critical','High','Medium','Low'] as Priority[]).map(p=><option key={p} value={p}>{labelUiPriority(t,p)}</option>)}",
    ),
    ("<small>Rule confidence</small>", "<small>{t('portal.submit.confidenceLabel')}</small>"),
    ("· indicative only", "· {t('portal.submit.confidenceHint')}"),
    ("<b>Potential immediate hazard</b>", "<b>{t('portal.submit.potentialHazard')}</b>"),
    (
        "<p>If anyone is in immediate danger, contact the appropriate emergency service directly. This demo does not dispatch help.</p>",
        "<p>{t('portal.submit.hazardDemoBody')}</p>",
    ),
    ("<h3>Clearer wording suggestion</h3>", "<h3>{t('portal.submit.clearerWording')}</h3>"),
    ("<p>Preserves your facts; review before using.</p>", "<p>{t('portal.submit.preservesFacts')}</p>"),
    ('<span className="sim-tag">RULE-BASED</span>', "<span className=\"sim-tag\">{t('portal.submit.ruleBased')}</span>"),
    (">Keep original</button>", ">{t('portal.submit.keepOriginal')}</button>"),
    (
        "{useRewrite?'Suggestion selected':'Use suggestion'}",
        "{useRewrite?t('portal.submit.suggestionSelected'):t('portal.submit.useSuggestion')}",
    ),
    (">Back to details</button>", ">{t('portal.submit.backToDetails')}</button>"),
    (">Continue to submit <ArrowRight", ">{t('portal.submit.continueSubmit')} <ArrowRight"),
    (
        "<p>Check your report before saving it to the demo workspace.</p>",
        "<p>{dataCtx.mode==='live'?t('portal.submit.reviewSubmitDesc'):t('portal.submit.reviewSubmitDescDemo')}</p>",
    ),
    (
        "<span><FileText size={14}/>{files.length} attachment(s)</span>",
        "<span><FileText size={14}/>{files.length} {t('portal.submit.attachmentsCount')}</span>",
    ),
    ("<b>Demo submission only</b>", "<b>{t('portal.submit.demoSubmitTitle')}</b>"),
    (
        "<p>This creates a local demonstration record. It is not sent to GHMC or any government department.</p>",
        "<p>{t('portal.submit.demoSubmitBody')}</p>",
    ),
    (
        ">Back</button><button className=\"btn btn-primary\" onClick={submit}>",
        ">{t('portal.submit.back')}</button><button className=\"btn btn-primary\" onClick={submit}>",
    ),
    ("<h3>Smart guidance</h3>", "<h3>{t('portal.submit.smartGuidance')}</h3>"),
    (
        "<p>Our local demo rules help structure a report. All recommendations are indicative and should be reviewed by a human.</p>",
        "<p>{t('portal.submit.smartGuidanceBody')}</p>",
    ),
    (
        "<b>Be specific</b><small>Include a street or landmark.</small>",
        "<b>{t('portal.submit.beSpecific')}</b><small>{t('portal.submit.beSpecificHint')}</small>",
    ),
    (
        "<b>Explain the impact</b><small>Who is affected and how?</small>",
        "<b>{t('portal.submit.explainImpact')}</b><small>{t('portal.submit.explainImpactHint')}</small>",
    ),
    (
        "<b>Suggest an action</b><small>Describe what would help.</small>",
        "<b>{t('portal.submit.suggestAction')}</b><small>{t('portal.submit.suggestActionHint')}</small>",
    ),
    ("<b>Immediate danger?</b>", "<b>{t('portal.submit.emergencyTitle')}</b>"),
    (
        "<p>Do not wait for a portal response. Contact the appropriate local emergency service directly.</p>",
        "<p>{t('portal.submit.emergencyBody')}</p>",
    ),
    ("<b>Local demo storage</b>", "<b>{t('portal.submit.asidePrivacyTitle')}</b>"),
    (
        "<p>Details and attachments are not uploaded to a server. Only file names are stored in the grievance record.</p>",
        "<p>{t('portal.submit.asidePrivacyBody')}</p>",
    ),
    (
        "<b>{flagged.length} cases flagged for human review</b>",
        "<b>{formatNumber(flagged.length)} {t('portal.officer.flaggedCount')}</b>",
    ),
    (
        "<p>Flags are generated by deterministic demo rules. They do not constitute an actual risk assessment.</p>",
        "<p>{t('portal.officer.flaggedHint')}</p>",
    ),
    (
        "detail={`${ratings.length} feedback submissions`}",
        "detail={`${formatNumber(ratings.length)} ${t('portal.admin.feedbackSubmissions')}`}",
    ),
    ('eyebrow="ADMINISTRATION / SERVICE LEVELS"', "eyebrow={t('portal.admin.eyebrow')}"),
    ("setChatInput('How do I file a grievance?')", "setChatInput(t('chat.quickFile'))"),
]

for a, b in repls:
    if a in s:
        s = s.replace(a, b)
    else:
        print("MISS:", a[:80])

s = s.replace(
    "function ReviewQueue({grievances,update}:{grievances:Grievance[],update:(id:string,p:Partial<Grievance>,m?:string)=>void}){const {t}=useI18n();",
    "function ReviewQueue({grievances,update}:{grievances:Grievance[],update:(id:string,p:Partial<Grievance>,m?:string)=>void}){const {t,formatNumber}=useI18n();",
)

p.write_text(s)
print("OK", p)
