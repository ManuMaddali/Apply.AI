// Curated job URLs for testing different resume categories
export const jobUrlCollections = {
  'Software Engineering': [
    '',
    'https://boards.greenhouse.io/airbnb/jobs/4567890',
    'https://www.google.com/about/careers/applications/jobs/results/123456789',
    'https://jobs.apple.com/en-us/details/200354321/software-engineer',
    'https://careers.microsoft.com/us/en/job/1234567/Software-Engineer'
  ],
  'Data Science': [
    'https://jobs.lever.co/netflix/data-scientist-machine-learning',
    'https://boards.greenhouse.io/uber/jobs/data-scientist-analytics',
    'https://www.google.com/about/careers/applications/jobs/results/data-scientist',
    'https://jobs.apple.com/en-us/details/200354322/data-scientist',
    'https://careers.microsoft.com/us/en/job/1234568/Data-Scientist'
  ],
  'Product Management': [
    'https://www.linkedin.com/jobs/view/4255827451/',
    'https://www.linkedin.com/jobs/view/4258748648/',
    'https://job-boards.eu.greenhouse.io/stubhubinc/jobs/4578234101?gh_src=47e65a22teu',
    'https://careers.truist.com/us/en/job/TBJTBFUSR0100496EXTERNALENUS/Product-Manager-Digital-Commerce?',
    'https://delta.avature.net/en_US/careers/JobDetail/Associate-Software-Development-Engineer-Delta-Vacations/28923?jobId=28923'
  ],
  'Marketing': [
    'https://jobs.lever.co/spotify/marketing-manager-brand',
    'https://boards.greenhouse.io/uber/jobs/marketing-manager-growth',
    'https://www.google.com/about/careers/applications/jobs/results/marketing-manager',
    'https://jobs.apple.com/en-us/details/200354324/marketing-manager',
    'https://careers.microsoft.com/us/en/job/1234570/Marketing-Manager'
  ],
  'Sales': [
    'https://jobs.lever.co/salesforce/enterprise-sales-director',
    'https://boards.greenhouse.io/oracle/jobs/enterprise-account-executive',
    'https://www.google.com/about/careers/applications/jobs/results/sales-director',
    'https://jobs.apple.com/en-us/details/200354325/enterprise-sales',
    'https://careers.microsoft.com/us/en/job/1234571/Enterprise-Sales-Director'
  ],
  'Design': [
    'https://jobs.lever.co/figma/senior-product-designer',
    'https://boards.greenhouse.io/airbnb/jobs/senior-ux-designer',
    'https://www.google.com/about/careers/applications/jobs/results/ux-designer',
    'https://jobs.apple.com/en-us/details/200354326/senior-designer',
    'https://careers.microsoft.com/us/en/job/1234572/Senior-UX-Designer'
  ],
  'Healthcare': [
    'https://careers.kaiserpermanente.org/jobs/registered-nurse-icu',
    'https://jobs.uclahealth.org/job/registered-nurse-emergency-department',
    'https://www.cedars-sinai.org/careers/registered-nurse-charge-nurse',
    'https://careers.chla.org/job/pediatric-nurse-specialist',
    'https://jobs.dignityhealth.org/registered-nurse-medical-surgical'
  ],
  'Executive': [
    'https://boards.greenhouse.io/uber/jobs/chief-technology-officer',
    'https://jobs.lever.co/netflix/vice-president-engineering',
    'https://www.google.com/about/careers/applications/jobs/results/engineering-director',
    'https://jobs.apple.com/en-us/details/200354327/director-engineering',
    'https://careers.microsoft.com/us/en/job/1234573/VP-Engineering'
  ],
  'Business': [
    'https://boards.greenhouse.io/consulting-firm/jobs/business-analyst',
    'https://jobs.lever.co/mckinsey/business-analyst-consultant',
    'https://www.google.com/about/careers/applications/jobs/results/business-analyst',
    'https://jobs.apple.com/en-us/details/200354328/business-analyst',
    'https://careers.microsoft.com/us/en/job/1234574/Business-Analyst'
  ],
  'Career Transition': [
    'https://boards.greenhouse.io/tech-startup/jobs/junior-developer',
    'https://jobs.lever.co/bootcamp-grad/associate-product-manager',
    'https://www.google.com/about/careers/applications/jobs/results/entry-level-tech',
    'https://jobs.apple.com/en-us/details/200354329/associate-engineer',
    'https://careers.microsoft.com/us/en/job/1234575/Associate-Technical-Program-Manager'
  ]
};

// Quick test scenarios - pre-configured combinations
export const testScenarios = [
  {
    id: 'entry_level_swe_big_tech',
    name: 'Entry Level → Big Tech',
    resumeId: 'entry_level_swe',
    jobUrls: jobUrlCollections['Software Engineering'].slice(0, 3),
    description: 'Test how entry-level resume gets tailored for major tech companies'
  },
  {
    id: 'senior_marketing_growth',
    name: 'Marketing → Growth Roles',
    resumeId: 'senior_marketing_manager',
    jobUrls: jobUrlCollections['Marketing'].slice(0, 3),
    description: 'Test marketing experience adaptation for different growth-focused roles'
  },
  {
    id: 'data_scientist_variety',
    name: 'Data Science → Various Companies',
    resumeId: 'data_scientist_phd',
    jobUrls: jobUrlCollections['Data Science'].slice(0, 3),
    description: 'Test PhD-level data science resume across different company types'
  },
  {
    id: 'career_changer_tech',
    name: 'Finance → Tech Transition',
    resumeId: 'career_changer_finance_to_tech',
    jobUrls: jobUrlCollections['Career Transition'].slice(0, 3),
    description: 'Test career transition resume for entry-level tech positions'
  },
  {
    id: 'recent_grad_business',
    name: 'Recent Grad → Business Roles',
    resumeId: 'recent_graduate_internships',
    jobUrls: jobUrlCollections['Business'].slice(0, 3),
    description: 'Test recent graduate resume for various business analyst positions'
  },
  {
    id: 'product_manager_cross_company',
    name: 'Product Manager → Cross-Company',
    resumeId: 'mid_level_product_manager',
    jobUrls: jobUrlCollections['Product Management'].slice(0, 3),
    description: 'Test product management experience across different company cultures'
  },
  {
    id: 'executive_leadership',
    name: 'Executive → Leadership Roles',
    resumeId: 'senior_executive_cto',
    jobUrls: jobUrlCollections['Executive'].slice(0, 3),
    description: 'Test executive resume for various high-level leadership positions'
  },
  {
    id: 'designer_creative',
    name: 'Designer → Creative Roles',
    resumeId: 'creative_ux_designer',
    jobUrls: jobUrlCollections['Design'].slice(0, 3),
    description: 'Test creative design experience for various UX/UI positions'
  },
  {
    id: 'sales_enterprise',
    name: 'Sales → Enterprise Focus',
    resumeId: 'enterprise_sales_professional',
    jobUrls: jobUrlCollections['Sales'].slice(0, 3),
    description: 'Test enterprise sales experience for various sales director roles'
  },
  {
    id: 'healthcare_nursing',
    name: 'Healthcare → Nursing Roles',
    resumeId: 'healthcare_professional_nurse',
    jobUrls: jobUrlCollections['Healthcare'].slice(0, 3),
    description: 'Test healthcare nursing experience for various hospital positions'
  }
];

export default { jobUrlCollections, testScenarios }; 