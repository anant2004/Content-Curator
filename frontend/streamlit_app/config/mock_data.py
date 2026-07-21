import re
import copy

DOMAINS = [
    'Steel Manufacturing',
    'Mining',
    'Safety & Compliance',
    'Human Resources',
    'Operations',
    'Procurement',
    'Finance',
    'Environmental Management',
    'Training & Development',
    'Others',
]

OUTPUT_TYPES = [
    'Training Program',
    'SOP',
    'Handbook',
    'Presentation',
    'Executive Report',
    'Video',
    'Podcast',
    'Others',
]

# A-Z sorted list of divisions (as requested in specifications)
DIVISIONS = [
    "Asset & Energy Management",
    "CEO & Managing Director",
    "Corporate Secretarial, Compliance & Legal",
    "Corporate Services",
    "ED & Chief Financial Officer",
    "Engineering & Projects",
    "Financial Control & Business Analytics",
    "Group Strategic Procurement and Business Excellence",
    "Human Resources Management",
    "Marketing & Sales",
    "One IT",
    "Operations Downstream",
    "Operations TSJ",
    "Operations TSK",
    "Raw Materials",
    "Safety, Health & Sustainability",
    "Supply Chain",
    "Tata Steel Meramandali",
    "Technology and R&D",
    "Treasury & Risk Management"
]

FILE_TYPES = [
    "PDF",
    "PPT",
    "Excel",
    "Word",
    "HTML",
    "Markdown",
    "CSV",
    "TXT",
    "Others",
]

COMPLIANCE_FRAMEWORKS = [
    'IS 14489 — Occupational Safety Audit',
    'DGMS Metalliferous Mines Regulations',
    'Factory Act 1948',
    'Tata Steel Corporate EHS Policy',
    'CPCB Environmental Standards',
    'ISO 45001 Occupational Health & Safety',
]

SUGGESTED_ACTIONS = [
    {
        'label': 'Create Training Program',
        'prompt': 'Create a Blast Furnace Safety Training Program for new employees using the uploaded SOPs and incident reports.',
        'outputType': 'Training Program',
    },
    {
        'label': 'Generate SOP',
        'prompt': 'Generate a contractor safety compliance SOP for external maintenance teams at Jamshedpur plant.',
        'outputType': 'SOP',
    },
    {
        'label': 'Create Handbook',
        'prompt': 'Create an operations handbook covering safety principles, emergency response, and compliance for blast furnace teams.',
        'outputType': 'Handbook',
    },
    {
        'label': 'Build Presentation',
        'prompt': 'Build an executive presentation on Q3 blast furnace safety performance for plant leadership review.',
        'outputType': 'Presentation',
    },
    {
        'label': 'Create Executive Report',
        'prompt': 'Create an executive report summarizing safety audit findings, risks, and recommended actions for the plant head.',
        'outputType': 'Executive Report',
    },
    {
        'label': 'Create Video',
        'prompt': 'Generate a safety training video script for Jamshedpur blast furnace workers.',
        'outputType': 'Video',
    },
    {
        'label': 'Create Podcast',
        'prompt': 'Produce an audio briefing on hot metal handling procedures for safety leaders.',
        'outputType': 'Podcast',
    }
]

RECENT_DOCUMENTS = [
    {'id': 'r1', 'name': 'BF4 Safety Training Program', 'type': 'Training Program', 'date': '2 hours ago'},
    {'id': 'r2', 'name': 'Contractor Safety SOP', 'type': 'SOP', 'date': 'Yesterday'},
    {'id': 'r3', 'name': 'Q3 Executive Safety Report', 'type': 'Executive Report', 'date': '3 days ago'},
]

SAMPLE_TEMPLATE_FILES = [
    {'name': 'Safety_Training_Template_2024.pptx', 'size': '5.1 MB', 'type': 'pptx'},
    {'name': 'SOP_Master_Format.docx', 'size': '234 KB', 'type': 'docx'},
]

SAMPLE_SOURCE_FILES = [
    {'name': 'BF4_Safety_Audit_Q2_2026.pdf', 'size': '2.4 MB', 'type': 'pdf'},
    {'name': 'Hot_Metal_Handling_SOP_v4.docx', 'size': '856 KB', 'type': 'docx'},
    {'name': 'DGMS_Circular_2025_14.pdf', 'size': '1.1 MB', 'type': 'pdf'},
    {'name': 'Contractor_Safety_Guidelines.pptx', 'size': '3.2 MB', 'type': 'pptx'},
    {'name': 'PPE_Compliance_Matrix_Q2.xlsx', 'size': '445 KB', 'type': 'xlsx'},
]

# Mock generated data structures matching React
PRESENTATION_SLIDES = [
    {
        'id': 1,
        'title': 'Blast Furnace Safety Excellence Program',
        'subtitle': 'Q3 Employee Training Initiative',
        'type': 'title',
    },
    {
        'id': 2,
        'title': 'Agenda',
        'bullets': [
            'Program Overview & Objectives',
            'Risk Prevention Framework',
            'Emergency Response Protocols',
            'Building Safety Culture',
            'Assessment & Certification',
        ],
        'type': 'content',
    },
    {
        'id': 3,
        'title': 'Risk Prevention',
        'bullets': [
            'Hot metal handling procedures per SOP-BF-042',
            'Mandatory PPE requirements for furnace area',
            'Gas detection and ventilation protocols',
            'Pre-shift safety briefing checklist',
        ],
        'type': 'content',
    },
    {
        'id': 4,
        'title': 'Emergency Response',
        'bullets': [
            'Evacuation routes and assembly points',
            'First aid station locations',
            'Incident reporting within 15 minutes',
            'Emergency contact escalation matrix',
        ],
        'type': 'content',
    },
    {
        'id': 5,
        'title': 'Safety Culture',
        'bullets': [
            'Stop Work Authority for all employees',
            'Near-miss reporting incentives',
            'Monthly safety committee participation',
            'Recognition program for safety champions',
        ],
        'type': 'content',
    },
]

DOCUMENT_SECTIONS = [
    {
        'title': 'Executive Summary',
        'content': 'This report presents the Q3 Blast Furnace Safety Training Program designed for 120 new contract workers at Tata Steel Jamshedpur Plant. The program addresses critical safety gaps identified in the Q2 audit and aligns with IS 14489 and DGMS regulatory requirements. Expected outcomes include 40% reduction in near-miss incidents and 100% PPE compliance within 90 days of implementation.',
    },
    {
        'title': 'Current Situation',
        'content': 'Blast Furnace #4 operations involve high-risk activities including hot metal tapping, slag handling, and gas system maintenance. The Q2 safety audit identified 23 observations across contractor management, PPE compliance, and emergency preparedness. Three near-miss incidents in May 2026 involved inadequate hot work permit procedures.',
    },
    {
        'title': 'Key Findings',
        'content': 'Analysis of 14 source documents reveals: (1) 68% of contract workers lack formal blast furnace safety certification, (2) Emergency evacuation drills conducted quarterly vs. monthly requirement, (3) Existing training materials dated 2022 and missing updated gas detection protocols, (4) Strong safety culture foundation with active safety committee participation.',
    },
    {
        'title': 'Recommendations',
        'content': 'Implement a structured 5-day induction program with classroom and field components. Deploy digital competency assessments via plant LMS. Establish contractor safety passport system with quarterly recertification. Integrate real-time PPE compliance monitoring at furnace access points.',
    },
    {
        'title': 'Implementation Plan',
        'content': 'Phase 1 (July 2026): Program rollout for first 40 workers. Phase 2 (August 2026): Scale to remaining 80 workers. Phase 3 (September 2026): Assessment, certification, and program evaluation. Budget allocation: ₹42 lakhs including trainer deployment, materials, and LMS integration.',
    },
    {
        'title': 'Expected Outcomes',
        'content': 'Target metrics: Zero lost-time injuries in BF#4 area during Q3-Q4 2026. 100% contractor safety passport compliance. 95%+ training assessment pass rate. Reduction in safety observations from 23 to below 5 by December 2026 audit.',
    },
]

SPREADSHEET_DATA = [
    {
        'department': 'Blast Furnace',
        'completion': '94%',
        'compliance': '92',
        'risk': 'Medium',
        'status': 'On Track',
        'reviewDate': '15 Jul 2026',
    },
    {
        'department': 'Coke Oven',
        'completion': '88%',
        'compliance': '85',
        'risk': 'High',
        'status': 'Action Required',
        'reviewDate': '12 Jul 2026',
    },
    {
        'department': 'Steel Melting Shop',
        'completion': '97%',
        'compliance': '96',
        'risk': 'Low',
        'status': 'Compliant',
        'reviewDate': '20 Jul 2026',
    },
    {
        'department': 'Continuous Casting',
        'completion': '91%',
        'compliance': '89',
        'risk': 'Medium',
        'status': 'On Track',
        'reviewDate': '18 Jul 2026',
    },
    {
        'department': 'Maintenance',
        'completion': '76%',
        'compliance': '72',
        'risk': 'High',
        'status': 'Critical',
        'reviewDate': '10 Jul 2026',
    },
    {
        'department': 'Logistics & Transport',
        'completion': '99%',
        'compliance': '98',
        'risk': 'Low',
        'status': 'Compliant',
        'reviewDate': '25 Jul 2026',
    },
]

HANDBOOK_CHAPTERS = [
    {
        'id': 1,
        'title': 'Introduction',
        'content': 'Welcome to the Blast Furnace Operations Handbook. This document serves as the primary reference for all personnel working in or around Blast Furnace #4 at Tata Steel Jamshedpur Plant. It consolidates operational guidelines, safety requirements, and best practices developed over decades of steel manufacturing excellence.',
    },
    {
        'id': 2,
        'title': 'Safety Principles',
        'content': 'Safety is non-negotiable at Tata Steel. All personnel must adhere to the Life Saving Rules: obtain authorization before overriding safety systems, protect yourself against falling objects, do not walk under suspended loads, and report all incidents and near-misses immediately. Stop Work Authority empowers every employee to halt unsafe operations.',
    },
    {
        'id': 3,
        'title': 'Operational Guidelines',
        'content': 'Standard operating procedures govern all blast furnace activities including charging, tapping, slag handling, and maintenance. Pre-shift briefings are mandatory. Gas monitoring systems must be operational before area entry. Hot metal transport follows designated routes with escort vehicles during peak operations.',
    },
    {
        'id': 4,
        'title': 'Emergency Response',
        'content': 'In case of gas leak: evacuate immediately using nearest exit route, report to assembly point BF-Alpha, do not re-enter until all-clear from Safety Officer. Fire emergency: activate nearest alarm, use appropriate extinguisher if safe to do so, evacuate and account for all personnel. Medical emergency: contact plant medical center ext. 119.',
    },
    {
        'id': 5,
        'title': 'Compliance Requirements',
        'content': 'Operations must comply with IS 14489 (Code of Practice on Occupational Safety and Health Audit), DGMS Circular on Metalliferous Mines Regulations, Factory Act 1948, and Tata Steel Corporate EHS Policy. Annual compliance audits are conducted by internal and external assessors. Non-compliance items require corrective action within defined timelines.',
    },
]

SOP_SECTIONS = [
    {
        'title': 'Purpose',
        'content': 'This Standard Operating Procedure establishes the requirements for contractor safety management during maintenance and project activities at Tata Steel manufacturing facilities, ensuring compliance with corporate EHS standards and regulatory requirements.',
    },
    {
        'title': 'Scope',
        'content': 'Applies to all external contractors, vendors, and service providers performing work at Tata Steel Jamshedpur, Kalinganagar, and Meramandali plants. Covers hot work, confined space entry, work at height, and general maintenance activities.',
    },
    {
        'title': 'Definitions',
        'content': 'Contractor: Any external entity performing work under contract. Permit-to-Work (PTW): Formal authorization system for high-risk activities. Safety Passport: Digital credential verifying contractor safety training and competency. EHS: Environment, Health, and Safety.',
    },
    {
        'title': 'Responsibilities',
        'content': 'Plant Head: Overall accountability for contractor safety. EHS Manager: PTW system administration and audit. Contract Owner: Pre-qualification and performance monitoring. Contractor Supervisor: On-site safety compliance and workforce briefing. Safety Officer: PTW approval and incident investigation.',
    },
    {
        'title': 'Procedure',
        'content': 'Step 1: Contractor pre-qualification via approved vendor portal. Step 2: Safety induction within 24 hours of site entry. Step 3: PTW application for all high-risk activities. Step 4: Toolbox talk before work commencement. Step 5: Continuous supervision and compliance monitoring. Step 6: Work completion verification and PTW closure.',
    },
    {
        'title': 'Safety Requirements',
        'content': 'Mandatory PPE: helmet, safety shoes, high-visibility vest, gloves, eye protection. Hot work requires fire watch for 30 minutes post-completion. Confined space entry mandates gas testing and standby attendant. Work at height above 1.8m requires fall protection and edge protection.',
    },
    {
        'title': 'Escalation Matrix',
        'content': 'Level 1 (Minor observation): Contractor supervisor correction within 4 hours. Level 2 (Repeat violation): Work stoppage, re-induction required. Level 3 (Serious violation): Contract suspension, EHS review. Level 4 (Incident/injury): Immediate work stoppage, investigation, potential contract termination.',
    },
    {
        'title': 'Approval Workflow',
        'content': 'Document prepared by: EHS Team. Reviewed by: Plant Safety Committee. Approved by: Plant Head. Effective date upon signature. Next review: Annual or upon regulatory change.',
    },
    {
        'title': 'Revision History',
        'content': 'Rev 3.0 — June 2026: Added digital safety passport requirements. Rev 2.0 — January 2025: Updated hot work procedures. Rev 1.0 — March 2023: Initial release.',
    },
    {
        'title': 'Document Control',
        'content': 'Document ID: SOP-EHS-CON-001. Classification: Internal — Controlled. Owner: Corporate EHS Department. Distribution: All plant EHS managers, contractor coordinators. Supersedes: SOP-EHS-CON-001 Rev 2.0.',
    },
]

VIDEO_SCRIPT = [
    {'scene': 'Scene 1: Introduction', 'visual': 'Opening shot of Tata Steel Jamshedpur plant with BF#4 in center. Text overlay: "Safety First, Always."', 'audio': 'Welcome to Tata Steel Jamshedpur Plant. Today we will outline the mandatory safety training program for all new contract workers joining our blast furnace operations. Let\'s get started.'},
    {'scene': 'Scene 2: PPE Compliance', 'visual': 'Close-up of a worker putting on a safety helmet, eye protection, and high-visibility vest. Highlight elements in green.', 'audio': 'Before entering the plant, ensure you are wearing all required PPE. This includes your safety helmet, steel-toed boots, protective glasses, and cut-resistant gloves.'},
    {'scene': 'Scene 3: Confined Space Access', 'visual': 'Worker checking gas level using a portable detector at a manhole cover. Show digital readings.', 'audio': 'Entering confined spaces requires a valid permit. Always test gas levels and make sure a standby attendant is stationed at the entrance before entry.'},
]

PODCAST_SCRIPT = [
    {'segment': 'Intro', 'speaker': 'Host', 'dialogue': 'Hello and welcome to the Tata Steel Safety Podcast. Today we are discussing the new contractor safety induction program at the Jamshedpur plant.'},
    {'segment': 'Background', 'speaker': 'Safety Director', 'dialogue': 'Thank you. The new program focuses on hot metal handling, PPE compliance, and strict adherence to permit-to-work systems following our recent Q2 audit recommendations.'},
    {'segment': 'Key Steps', 'speaker': 'Host', 'dialogue': 'What are the main changes for contractors?'},
    {'segment': 'Requirements', 'speaker': 'Safety Director', 'dialogue': 'First, a digital safety passport is now mandatory. Second, all toolbox talks must be logged in the system. Finally, zero tolerance on high-risk safety observations.'},
]

GENERATED_ASSETS_BY_OUTPUT = {
    'Training Program': [
        {'id': 'presentation', 'label': 'Presentation', 'artifact': 'presentation', 'description': '12-slide training deck'},
        {'id': 'handbook', 'label': 'Handbook', 'artifact': 'handbook', 'description': '5-chapter guide'},
        {'id': 'sop', 'label': 'SOP', 'artifact': 'sop', 'description': 'Operational procedure'},
        {'id': 'checklist', 'label': 'Training Checklist', 'artifact': 'spreadsheet', 'description': 'Compliance tracker'},
    ],
    'SOP': [{'id': 'sop', 'label': 'SOP', 'artifact': 'sop', 'description': 'Standard operating procedure'}],
    'Handbook': [{'id': 'handbook', 'label': 'Handbook', 'artifact': 'handbook', 'description': 'Corporate handbook'}],
    'Presentation': [
        {'id': 'presentation', 'label': 'Presentation', 'artifact': 'presentation', 'description': 'Executive slide deck'},
    ],
    'Executive Report': [
        {'id': 'document', 'label': 'Executive Report', 'artifact': 'document', 'description': 'Full report document'},
    ],
    'Video': [{'id': 'video', 'label': 'Video Script', 'artifact': 'video', 'description': 'Training video script'}],
    'Podcast': [
        {'id': 'podcast', 'label': 'Podcast Script', 'artifact': 'podcast', 'description': 'Audio briefing script'},
    ],
}

SIMPLE_PROGRESS_STEPS = {
    'Training Program': [
        'Analyzing documents...',
        'Building training structure...',
        'Generating presentation...',
        'Creating handbook...',
    ],
    'SOP': ['Analyzing documents...', 'Mapping compliance requirements...', 'Structuring procedure...', 'Finalizing SOP...'],
    'Handbook': [
        'Analyzing documents...',
        'Organizing chapters...',
        'Applying compliance standards...',
        'Creating handbook...',
    ],
    'Presentation': [
        'Analyzing documents...',
        'Structuring narrative...',
        'Designing slides...',
        'Finalizing presentation...',
    ],
    'Executive Report': [
        'Analyzing documents...',
        'Extracting key findings...',
        'Drafting recommendations...',
        'Finalizing report...',
    ],
    'Video': [
        'Analyzing documents...',
        'Planning scenes...',
        'Writing narration...',
        'Finalizing script...',
    ],
    'Podcast': [
        'Analyzing documents...',
        'Structuring segments...',
        'Drafting script...',
        'Finalizing briefing...',
    ],
}

ASSISTANT_CHECKS = [
    'documents analyzed',
    'Existing SOP framework detected',
    'Safety compliance standards applied',
]

DOMAIN_EXAMPLES = {
    'Steel Manufacturing': {
        'objective': 'Create a Q3 Blast Furnace Safety Training Program for New Employees at Jamshedpur Plant.',
        'context': 'Following the Q2 safety audit at Blast Furnace #4, management has directed HR and Safety teams to develop a comprehensive induction program for 120 new contract workers joining in Q3 2026. Key focus areas include hot metal handling, PPE compliance, and emergency evacuation procedures per IS 14489 standards.',
    },
    'Mining': {
        'objective': 'Develop an Open-Pit Mining Operations Handbook for Noamundi Iron Ore Mine.',
        'context': 'Operations team requires updated documentation covering bench drilling protocols, haul road safety, and environmental dust suppression measures aligned with DGMS regulations and Tata Steel sustainability commitments.',
    },
    'Safety & Compliance': {
        'objective': 'Generate a Contractor Safety Compliance SOP for External Maintenance Teams.',
        'context': 'Recent incidents involving third-party contractors at the coke oven battery highlight gaps in permit-to-work systems. Safety department needs a standardized SOP covering contractor onboarding, hot work permits, and escalation procedures.',
    },
    'Human Resources': {
        'objective': 'Build an Employee Induction Program for Graduate Engineer Trainees — 2026 Batch.',
        'context': 'HR leadership has approved a structured 90-day onboarding framework covering Tata Steel values, plant orientation, mentorship assignment, and competency assessments for 45 GETs joining across Jamshedpur and Kalinganagar plants.',
    },
    'Operations': {
        'objective': 'Create an Executive Briefing on Continuous Casting Line Optimization — FY2026.',
        'context': 'Plant head requires a leadership presentation summarizing CC Line #2 throughput improvements, quality metrics, downtime analysis, and recommended capital investments for the upcoming board review.',
    },
    'Procurement': {
        'objective': 'Produce a Vendor Compliance Assessment Report for Raw Material Suppliers.',
        'context': 'Procurement team needs an executive summary of Q2 vendor audits covering iron ore, coking coal, and flux suppliers with compliance scores, risk ratings, and corrective action timelines.',
    },
    'Finance': {
        'objective': 'Generate a Cost Optimization Executive Summary for Energy Management Division.',
        'context': 'CFO office requires a quarterly report on energy consumption trends, renewable integration progress, and projected savings from blast furnace gas recovery initiatives across integrated steel plants.',
    },
    'Environmental Management': {
        'objective': 'Create an Environmental Compliance Handbook for Zero Liquid Discharge Operations.',
        'context': 'Environmental team must document ZLD system operations, effluent monitoring protocols, CPCB compliance requirements, and incident reporting procedures for all Tata Steel manufacturing facilities.',
    },
    'Training & Development': {
        'objective': 'Develop a Leadership Development Program for Plant Managers — Safety Excellence Track.',
        'context': 'Corporate L&D requires a structured program covering behavioral safety leadership, incident investigation methodology, regulatory compliance oversight, and cross-plant best practice sharing for 28 plant managers.',
    },
}

def infer_output_type_from_prompt(prompt, fallback='Training Program'):
    t = prompt.lower()
    if 'sop' in t or 'standard operating procedure' in t:
        return 'SOP'
    if 'handbook' in t:
        return 'Handbook'
    if 'presentation' in t or 'slide' in t or 'deck' in t:
        return 'Presentation'
    if 'executive report' in t or ('report' in t and 'executive' in t):
        return 'Executive Report'
    if 'video' in t:
        return 'Video'
    if 'podcast' in t:
        return 'Podcast'
    if 'training' in t or 'induction' in t:
        return 'Training Program'
    return fallback

# Improvements Delta Constants
IMPROVEMENT_SUGGESTIONS = [
    'Make language more executive-focused',
    'Add environmental compliance references',
    'Simplify technical terminology',
    'Create a version for contractors',
]

def classify_improvement(text: str) -> str:
    t = text.lower()
    if 'executive' in t or 'leadership' in t or 'cxo' in t:
        return 'executive'
    if 'environment' in t or 'compliance' in t or 'cpcb' in t:
        return 'environmental'
    if 'simplif' in t or 'plain' in t or 'non-technical' in t:
        return 'simplified'
    if 'contractor' in t or 'vendor' in t or 'third-party' in t:
        return 'contractor'
    return 'general'

IMPROVEMENT_DELTAS = {
    'executive': {
        'label': 'Executive tone applied',
        'presentation': {
            'subtitleOverride': 'Executive Briefing — Q3 Safety Initiative',
            'extraBullets': {
                1: ['Board-ready KPI summary included', 'Strategic risk overview for leadership'],
                4: ['Leadership accountability framework added'],
            },
        },
        'document': {
            'summaryAppend': ' This version has been refined for CXO and Plant Head review, emphasizing strategic outcomes, accountability metrics, and board-ready formatting.',
            'extraSection': {
                'title': 'Leadership Action Items',
                'content': 'Plant Head to review program rollout by 15 July. Safety Committee to sign off on assessment criteria. HR to report completion rates weekly to executive leadership.',
            },
        },
        'sop': {
            'sectionAppend': {
                'Purpose': ' This executive-aligned revision emphasizes governance, audit readiness, and leadership oversight requirements.',
            },
        },
        'handbook': {
            'chapterAppend': {
                '1': ' This edition includes executive summary callouts and leadership accountability checkpoints at the start of each chapter.',
            },
        },
        'video': {
            'titleSuffix': ' — Leadership Edition',
            'captionExtra': 'Executive overview segment included for plant leadership.',
        },
        'podcast': {
            'titleSuffix': ' — Executive Briefing',
            'narratorNote': 'Tone adjusted for senior leadership audience.',
        },
    },
    'environmental': {
        'label': 'Environmental compliance added',
        'presentation': {
            'extraBullets': {
                2: ['CPCB emission standards referenced', 'Zero Liquid Discharge protocols included'],
                3: ['Environmental hazard identification checklist added'],
            },
        },
        'document': {
            'summaryAppend': ' Environmental compliance references have been integrated, including CPCB guidelines, effluent monitoring requirements, and Zero Liquid Discharge operational standards.',
            'extraSection': {
                'title': 'Environmental Compliance',
                'content': 'All training modules now reference Tata Steel environmental policy, CPCB notification requirements, and plant-specific ZLD monitoring procedures. Contractors must complete environmental awareness certification before site access.',
            },
        },
        'sop': {
            'sectionAppend': {
                'Safety Requirements': ' Additional environmental controls: spill containment kits mandatory, effluent discharge monitoring before shift handover, and immediate reporting of any environmental incidents to EHS within 30 minutes.',
            },
        },
        'handbook': {
            'chapterAppend': {
                '4': ' Updated with environmental incident reporting procedures and CPCB compliance contact escalation paths.',
            },
        },
        'video': {
            'captionExtra': 'Environmental compliance segment: ZLD systems and emission monitoring.',
        },
        'podcast': {
            'narratorNote': 'Environmental compliance update segment added.',
        },
    },
    'simplified': {
        'label': 'Language simplified',
        'presentation': {
            'bulletPrefix': '→ ',
            'simplifiedBullets': True,
        },
        'document': {
            'summaryAppend': ' Technical language has been simplified for broader workforce comprehension while retaining regulatory accuracy.',
        },
        'sop': {
            'sectionAppend': {
                'Procedure': ' Note: Step descriptions simplified for field readability. Visual job aids recommended at each checkpoint.',
            },
        },
        'handbook': {
            'chapterAppend': {
                '2': ' Key safety principles restated in plain language with visual reference guides for non-technical staff.',
            },
        },
        'video': {
            'captionExtra': 'Simplified narration script for new and contract workers.',
        },
        'podcast': {
            'narratorNote': 'Script simplified for plant-wide accessibility.',
        },
    },
    'contractor': {
        'label': 'Contractor version created',
        'presentation': {
            'subtitleOverride': 'Contractor Safety Induction — Q3 2026',
            'extraBullets': {
                0: ['Contractor Safety Passport requirements', 'Permit-to-Work overview for external teams'],
                2: ['Contractor PPE verification checklist', 'Hot work permit procedures for third-party teams'],
            },
        },
        'document': {
            'summaryAppend': ' This contractor-specific version includes permit-to-work requirements, safety passport verification, and third-party escalation procedures.',
            'extraSection': {
                'title': 'Contractor Requirements',
                'content': 'All external maintenance teams must complete contractor safety induction within 24 hours of site entry. Safety passport verification required at all BF#4 access points. Hot work permits mandatory for welding, cutting, and grinding activities.',
            },
        },
        'sop': {
            'titleOverride': 'Contractor Safety Compliance SOP — Field Edition',
            'sectionAppend': {
                'Scope': ' Enhanced contractor onboarding checklist and digital safety passport integration included in this revision.',
            },
        },
        'handbook': {
            'chapterAppend': {
                '3': ' Contractor-specific operational guidelines including escort requirements, restricted area access, and toolbox talk documentation.',
            },
        },
        'video': {
            'titleSuffix': ' — Contractor Edition',
            'captionExtra': 'Contractor onboarding and permit-to-work procedures highlighted.',
        },
        'podcast': {
            'titleSuffix': ' — Contractor Briefing',
            'narratorNote': 'Tailored for external maintenance and project teams.',
        },
    },
    'general': {
        'label': 'Refinement applied',
        'document': {
            'summaryAppend': ' Content has been updated based on your refinement request.',
        },
    },
}

def get_applied_deltas(applied_improvements):
    return [
        {
            **IMPROVEMENT_DELTAS.get(classify_improvement(item['text']), IMPROVEMENT_DELTAS['general']),
            'type': classify_improvement(item['text']),
            'requestText': item['text'],
            'id': item['id']
        }
        for item in applied_improvements
    ]

def merge_presentation_slides(base_slides, deltas):
    base_slides = copy.deepcopy(base_slides)
    subtitle = None
    extra_bullets_by_index = {}
    simplified_bullets = False

    for delta in deltas:
        p = delta.get('presentation', {})
        if not p:
            continue
        if 'subtitleOverride' in p:
            subtitle = p['subtitleOverride']
        if 'simplifiedBullets' in p:
            simplified_bullets = p['simplifiedBullets']
        if 'extraBullets' in p:
            for idx, bullets in p['extraBullets'].items():
                i = int(idx)
                extra_bullets_by_index[i] = extra_bullets_by_index.get(i, []) + bullets

    for index, slide in enumerate(base_slides):
        extras = extra_bullets_by_index.get(index, [])
        bullets = slide.get('bullets', [])
        if bullets:
            bullets = list(bullets) + extras
        elif extras:
            bullets = extras

        if simplified_bullets and bullets:
            bullets = [re.sub(r' per SOP-[A-Z0-9-]+', '', b) for b in bullets]
            bullets = [re.sub(r'\(IS [0-9]+\)', '(standards)', b) for b in bullets]

        slide['bullets'] = bullets

        if slide.get('type') == 'title' and extras:
            if subtitle:
                slide['subtitle'] = subtitle
            slide['titleNote'] = ' · '.join(extras)
        else:
            if index == 0 and subtitle:
                slide['subtitle'] = subtitle

    return base_slides

def merge_document_sections(base_sections, deltas):
    sections = copy.deepcopy(base_sections)
    for delta in deltas:
        d = delta.get('document', {})
        if not d:
            continue
        if 'summaryAppend' in d:
            summary = next((s for s in sections if s['title'] == 'Executive Summary'), None)
            if summary:
                summary['content'] += d['summaryAppend']
        if 'extraSection' in d:
            exists = next((s for s in sections if s['title'] == d['extraSection']['title']), None)
            if not exists:
                sections.append(copy.deepcopy(d['extraSection']))
    return sections

def merge_sop_sections(base_sections, deltas):
    sections = copy.deepcopy(base_sections)
    title_override = None
    for delta in deltas:
        sop = delta.get('sop', {})
        if not sop:
            continue
        if 'titleOverride' in sop:
            title_override = sop['titleOverride']
        if 'sectionAppend' in sop:
            for title, append in sop['sectionAppend'].items():
                section = next((s for s in sections if s['title'] == title), None)
                if section:
                    section['content'] += append
    return sections, title_override

def merge_handbook_chapters(base_chapters, deltas):
    chapters = copy.deepcopy(base_chapters)
    for ch in chapters:
        ch_id = str(ch['id'])
        content = ch['content']
        for delta in deltas:
            append = delta.get('handbook', {}).get('chapterAppend', {}).get(ch_id)
            if append:
                content += append
        ch['content'] = content
    return chapters

def get_video_meta(deltas):
    title_suffix = ''
    caption_extra = ''
    for delta in deltas:
        if 'video' in delta:
            if 'titleSuffix' in delta['video']:
                title_suffix += delta['video']['titleSuffix']
            if 'captionExtra' in delta['video']:
                caption_extra = delta['video']['captionExtra']
    return title_suffix, caption_extra

def get_podcast_meta(deltas):
    title_suffix = ''
    narrator_note = ''
    for delta in deltas:
        if 'podcast' in delta:
            if 'titleSuffix' in delta['podcast']:
                title_suffix += delta['podcast']['titleSuffix']
            if 'narratorNote' in delta['podcast']:
                narrator_note = delta['podcast']['narratorNote']
    return title_suffix, narrator_note
