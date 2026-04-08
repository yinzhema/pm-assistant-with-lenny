export const TEMPLATES: Record<string, string> = {
  'prd-1pager': 'PRD (1-pager)',
  'prd-full': 'PRD (Full)',
  'strategy-doc': 'Strategy Doc',
  'rice': 'RICE Prioritization',
  'ice': 'ICE Prioritization',
  'moscow': 'MoSCoW Prioritization',
  'kano': 'Kano Model',
  'wsjf': 'WSJF Prioritization',
  'now-next-later': 'Now / Next / Later Roadmap',
  'outcome-roadmap': 'Outcome-Based Roadmap',
  'jtbd': 'Jobs-to-be-Done',
  'opp-solution-tree': 'Opportunity Solution Tree',
}

export interface TemplateItem {
  id: string
  name: string
  desc: string
}

export interface TemplateGroup {
  label: string
  items: TemplateItem[]
}

export const TEMPLATE_GROUPS: TemplateGroup[] = [
  {
    label: '📄 Docs',
    items: [
      { id: 'prd-1pager', name: 'PRD (1-pager)', desc: 'One-page product requirements' },
      { id: 'prd-full', name: 'PRD (Full)', desc: 'Detailed product requirements doc' },
      { id: 'strategy-doc', name: 'Strategy Doc', desc: 'Strategic context and bets' },
    ],
  },
  {
    label: '📊 Prioritization',
    items: [
      { id: 'rice', name: 'RICE', desc: 'Reach · Impact · Confidence · Effort' },
      { id: 'ice', name: 'ICE', desc: 'Impact · Confidence · Ease' },
      { id: 'moscow', name: 'MoSCoW', desc: "Must / Should / Could / Won't" },
      { id: 'kano', name: 'Kano Model', desc: 'Delighters vs must-haves' },
      { id: 'wsjf', name: 'WSJF', desc: 'Weighted Shortest Job First' },
    ],
  },
  {
    label: '🗺️ Roadmap',
    items: [
      { id: 'now-next-later', name: 'Now / Next / Later', desc: 'Horizon-based roadmap' },
      { id: 'outcome-roadmap', name: 'Outcome-Based', desc: 'Goals → initiatives' },
    ],
  },
  {
    label: '🔍 Discovery',
    items: [
      { id: 'jtbd', name: 'Jobs-to-be-Done', desc: 'Situation · Motivation · Outcome' },
      { id: 'opp-solution-tree', name: 'Opportunity Tree', desc: 'Outcomes → opportunities → solutions' },
    ],
  },
]
