/**
 * TypeScript type definitions for app-page-redesign
 * Comprehensive type safety for complex state management and UX features
 */

// User and Authentication Types
export interface User {
  id: string
  email: string
  tier: UserTier
  weeklyUsage: number
  weeklyLimit: number
  preferences: UserPreferences
  subscriptionStatus: SubscriptionStatus
  createdAt: string
  updatedAt: string
}

export type UserTier = 'free' | 'pro'
export type SubscriptionStatus = 'active' | 'inactive' | 'trial' | 'cancelled'

export interface UserPreferences {
  defaultMode: ProcessingMode | null
  enhancementLevel: EnhancementLevel
  autoIncludeSections: string[]
  notificationSettings: NotificationSettings
  accessibilitySettings: AccessibilitySettings
}

export interface NotificationSettings {
  processing: boolean
  completion: boolean
  errors: boolean
  weeklyUsage: boolean
}

export interface AccessibilitySettings {
  reducedMotion: boolean
  highContrast: boolean
  largeText: boolean
  screenReader: boolean
}

// Processing and Mode Types
export type ProcessingMode = 'batch' | 'precision'
export type EnhancementLevel = 'conservative' | 'balanced' | 'aggressive'
export type ProcessingStatus = 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled'
export type StepStatus = 'pending' | 'active' | 'completed' | 'failed' | 'skipped'

export interface BatchSettings {
  enhancementLevel: EnhancementLevel
  autoIncludeSections: AutoIncludeSections
  maxJobs: number
  generateCoverLetters: boolean
  optimizeForATS: boolean
}

export interface AutoIncludeSections {
  summary: boolean
  skills: boolean
  education: boolean
  coverLetter: boolean
  achievements: boolean
  certifications: boolean
}

export interface PrecisionSettings {
  enabledEnhancements: string[]
  bulletEnhancementLevels: Record<string, BulletEnhancementLevel>
  customEnhancements: CustomEnhancement[]
  previewMode: boolean
  realTimeUpdates: boolean
  showImpactScores: boolean
}

export type BulletEnhancementLevel = 'light' | 'medium' | 'heavy' | 'custom'

export interface CustomEnhancement {
  id: string
  title: string
  description: string
  beforeText: string
  afterText: string
  impact: number
  keywords: string[]
  category: EnhancementCategory
  createdAt: string
}

// Resume and Job Data Types
export interface ResumeData {
  id: string
  filename: string
  content: string
  originalContent: string
  sections: ResumeSection[]
  metadata: ResumeMetadata
  uploadedAt: string
  lastModified: string
}

export interface ResumeSection {
  id: string
  type: ResumeSectionType
  title: string
  content: string
  order: number
  visible: boolean
  enhanced: boolean
}

export type ResumeSectionType = 
  | 'contact'
  | 'summary'
  | 'experience'
  | 'education'
  | 'skills'
  | 'achievements'
  | 'certifications'
  | 'projects'
  | 'custom'

export interface ResumeMetadata {
  wordCount: number
  pageCount: number
  format: 'pdf' | 'docx' | 'txt'
  language: string
  lastATSScore?: number
}

export interface JobData {
  id: string
  url: string
  title: string
  company: string
  location: string
  description: string
  requirements: string[]
  preferredQualifications: string[]
  keywords: JobKeyword[]
  salary?: SalaryRange
  analyzedAt: string
  relevanceScore: number
}

export interface JobKeyword {
  term: string
  category: KeywordCategory
  importance: KeywordImportance
  frequency: number
  context: string[]
}

export type KeywordCategory = 'technical' | 'soft_skills' | 'industry' | 'tools' | 'certifications'
export type KeywordImportance = 'critical' | 'important' | 'preferred' | 'nice_to_have'

export interface SalaryRange {
  min: number
  max: number
  currency: string
  period: 'hourly' | 'monthly' | 'yearly'
}

// Processing and Results Types
export interface ProcessingJob {
  id: string
  resumeId: string
  jobId: string
  jobTitle: string
  jobCompany: string
  status: ProcessingStatus
  progress: ProcessingProgress
  steps: ProcessingStep[]
  estimatedTime: number
  actualTime?: number
  startTime: string
  completionTime?: string
  error?: ProcessingError
}

export interface ProcessingProgress {
  percentage: number
  currentStep: string
  completedSteps: number
  totalSteps: number
  timeRemaining?: number
}

export interface ProcessingStep {
  id: string
  name: string
  description: string
  status: StepStatus
  startTime?: string
  duration?: number
  details?: string
  error?: string
}

export interface ProcessingError {
  code: string
  message: string
  details?: any
  recoverable: boolean
  retryCount: number
}

export interface ProcessingResult {
  id: string
  jobId: string
  originalResume: string
  tailoredResume: string
  coverLetter?: string
  atsScore: ATSScore
  transformationMetrics: TransformationMetrics
  keywordAnalysis: KeywordAnalysis
  appliedEnhancements: AppliedEnhancement[]
  recommendations: Recommendation[]
  createdAt: string
}

// Analytics and Scoring Types
export interface ATSScore {
  current: number
  potential: number
  improvement: number
  sectionScores: Record<string, SectionScore>
  confidenceLevel: ConfidenceLevel
  factors: ScoreFactor[]
  lastUpdated: string
}

export interface SectionScore {
  score: number
  maxScore: number
  issues: ScoreIssue[]
  recommendations: string[]
}

export interface ScoreIssue {
  type: IssueType
  severity: IssueSeverity
  description: string
  suggestion: string
}

export type IssueType = 
  | 'missing_keywords'
  | 'weak_language'
  | 'formatting'
  | 'length'
  | 'relevance'
  | 'quantification'

export type IssueSeverity = 'critical' | 'major' | 'minor' | 'suggestion'
export type ConfidenceLevel = 'low' | 'medium' | 'high'

export interface ScoreFactor {
  name: string
  impact: number
  description: string
  category: 'positive' | 'negative' | 'neutral'
}

export interface TransformationMetrics {
  keywordsAdded: number
  keywordsRemoved: number
  contentEnhanced: number
  metricsAdded: number
  bulletPointsImproved: number
  sectionsAdded: number
  wordCountChange: number
  readabilityImprovement: number
  estimatedInterviewRateImprovement: number
}

export interface KeywordAnalysis {
  added: AnalyzedKeyword[]
  removed: AnalyzedKeyword[]
  matched: AnalyzedKeyword[]
  missing: AnalyzedKeyword[]
  categories: KeywordCategoryAnalysis[]
  relevanceScore: number
  coverage: number
}

export interface AnalyzedKeyword {
  term: string
  category: KeywordCategory
  importance: KeywordImportance
  frequency: number
  context: string[]
  impact: number
}

export interface KeywordCategoryAnalysis {
  category: KeywordCategory
  total: number
  matched: number
  coverage: number
  importance: number
}

// Enhancement System Types
export interface Enhancement {
  id: string
  title: string
  description: string
  impact: number
  category: EnhancementCategory
  type: EnhancementType
  previewText?: string
  keywords?: string[]
  metrics?: string[]
  available: boolean
  proOnly: boolean
  estimatedTime: number
  difficulty: EnhancementDifficulty
}

export type EnhancementCategory = 'high' | 'medium' | 'advanced' | 'custom'
export type EnhancementType = 
  | 'keyword_optimization'
  | 'content_enhancement'
  | 'structure_improvement'
  | 'quantification'
  | 'language_strengthening'
  | 'formatting'

export type EnhancementDifficulty = 'easy' | 'medium' | 'hard'

export interface AppliedEnhancement {
  enhancementId: string
  appliedAt: string
  impact: number
  beforeText: string
  afterText: string
  keywords: string[]
  metrics: string[]
  sectionId: string
  bulletId?: string
  userApproved: boolean
}

export interface Recommendation {
  id: string
  type: RecommendationType
  priority: RecommendationPriority
  title: string
  description: string
  impact: number
  effort: RecommendationEffort
  category: string
  actionable: boolean
  autoApplicable: boolean
}

export type RecommendationType = 
  | 'enhancement'
  | 'structure'
  | 'content'
  | 'formatting'
  | 'strategy'

export type RecommendationPriority = 'critical' | 'high' | 'medium' | 'low'
export type RecommendationEffort = 'minimal' | 'low' | 'medium' | 'high'

// UI and State Types
export interface UIState {
  selectedMode: ProcessingMode | null
  modeHistory: ModeSelection[]
  processing: ProcessingUIState
  analytics: AnalyticsUIState
  mobile: MobileUIState
  accessibility: AccessibilityUIState
}

export interface ModeSelection {
  mode: ProcessingMode
  timestamp: string
  context?: string
}

export interface ProcessingUIState {
  active: boolean
  mode: ProcessingMode | null
  progress: number
  currentJob?: string
  estimatedTimeRemaining?: number
  queue: ProcessingJob[]
  results: ProcessingResult[]
  showDetails: boolean
  expandedJobs: string[]
}

export interface AnalyticsUIState {
  showRealTimeUpdates: boolean
  expandedSections: string[]
  comparisonMode: boolean
  selectedMetrics: string[]
  timeRange: AnalyticsTimeRange
  chartType: ChartType
}

export type AnalyticsTimeRange = 'day' | 'week' | 'month' | 'all'
export type ChartType = 'line' | 'bar' | 'pie' | 'radar'

export interface MobileUIState {
  activeTab: string
  sidebarOpen: boolean
  keyboardVisible: boolean
  orientation: 'portrait' | 'landscape'
  safeAreaInsets: SafeAreaInsets
}

export interface SafeAreaInsets {
  top: number
  right: number
  bottom: number
  left: number
}

export interface AccessibilityUIState {
  reducedMotion: boolean
  highContrast: boolean
  largeText: boolean
  screenReaderActive: boolean
  keyboardNavigation: boolean
  focusVisible: boolean
}

// API and WebSocket Types
export interface APIResponse<T = any> {
  success: boolean
  data?: T
  error?: APIError
  timestamp: string
}

export interface APIError {
  code: string
  message: string
  details?: any
  field?: string
}

export interface WebSocketMessage {
  type: WebSocketMessageType
  payload: any
  timestamp: string
  id?: string
}

export type WebSocketMessageType = 
  | 'processing_update'
  | 'ats_score_update'
  | 'analytics_update'
  | 'enhancement_applied'
  | 'error'
  | 'ping'
  | 'pong'

export interface WebSocketState {
  connected: boolean
  connecting: boolean
  error: string | null
  reconnectAttempts: number
  lastMessage?: WebSocketMessage
}

// Form and Validation Types
export interface FormField<T = any> {
  value: T
  error?: string
  touched: boolean
  valid: boolean
}

export interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: any) => string | null
}

export interface FormState {
  fields: Record<string, FormField>
  valid: boolean
  submitting: boolean
  submitted: boolean
  errors: Record<string, string>
}

// Event and Analytics Types
export interface AnalyticsEvent {
  name: string
  properties: Record<string, any>
  timestamp: string
  userId?: string
  sessionId: string
}

export interface PerformanceMetric {
  name: string
  value: number
  unit: string
  timestamp: string
  context?: Record<string, any>
}

// React Query Types
export interface QueryConfig {
  staleTime: number
  cacheTime: number
  retry: number | boolean
  retryDelay: number
  refetchOnWindowFocus: boolean
  refetchOnReconnect: boolean
}

export interface MutationConfig {
  retry: number | boolean
  retryDelay: number
  onSuccess?: (data: any) => void
  onError?: (error: APIError) => void
  onSettled?: () => void
}

// WebSocket Enhanced Types
export interface WebSocketConfig {
  url: string
  protocols?: string[]
  reconnectInterval: number
  maxReconnectAttempts: number
  heartbeatInterval: number
  timeout: number
}

export interface WebSocketEventHandlers {
  onOpen?: (event: Event) => void
  onClose?: (event: CloseEvent) => void
  onError?: (event: Event) => void
  onMessage?: (message: WebSocketMessage) => void
  onReconnect?: (attempt: number) => void
  onMaxReconnectAttemptsReached?: () => void
}

// Enhanced Processing Types
export interface ProcessingQueue {
  jobs: ProcessingJob[]
  maxConcurrent: number
  currentlyProcessing: string[]
  completed: string[]
  failed: string[]
  paused: boolean
}

export interface ProcessingMetrics {
  totalJobs: number
  completedJobs: number
  failedJobs: number
  averageProcessingTime: number
  successRate: number
  queueLength: number
  estimatedCompletionTime: number
}

// Enhanced Enhancement Types
export interface EnhancementPreview {
  enhancementId: string
  beforeText: string
  afterText: string
  impact: number
  keywords: string[]
  metrics: string[]
  confidence: number
  reasoning: string
}

export interface EnhancementBatch {
  id: string
  enhancements: Enhancement[]
  totalImpact: number
  estimatedTime: number
  category: EnhancementCategory
  autoApply: boolean
}

// Tier and Subscription Enhanced Types
export interface TierLimitations {
  maxJobsPerBatch: number
  maxJobsPerWeek: number
  precisionModeAccess: boolean
  advancedAnalytics: boolean
  customEnhancements: boolean
  priorityProcessing: boolean
  exportFormats: string[]
}

export interface UpgradeContext {
  currentFeature: string
  blockedAction: string
  potentialBenefit: string
  urgency: 'low' | 'medium' | 'high'
  showPreview: boolean
}

// Utility Types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

// Component Props Types
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
  'data-testid'?: string
}

export interface InteractiveComponentProps extends BaseComponentProps {
  disabled?: boolean
  loading?: boolean
  onClick?: () => void
  onKeyDown?: (event: React.KeyboardEvent) => void
}

export interface FormComponentProps extends BaseComponentProps {
  name: string
  value: any
  onChange: (value: any) => void
  onBlur?: () => void
  error?: string
  required?: boolean
  disabled?: boolean
}

// Store Types - Enhanced for Zustand state management
export interface UserStore {
  user: User | null
  preferences: UserPreferences | null
  tier: UserTier
  weeklyUsage: number
  weeklyLimit: number
  subscriptionStatus: SubscriptionStatus
  
  // Actions
  setUser: (user: User) => void
  updateUser: (updates: Partial<User>) => void
  updatePreferences: (preferences: Partial<UserPreferences>) => void
  updateUsage: (usage: number) => void
  resetUserStore: () => void
}

export interface ProcessingStore {
  selectedMode: ProcessingMode | null
  modeHistory: ModeSelection[]
  batchSettings: BatchSettings
  precisionSettings: PrecisionSettings
  activeJobs: ProcessingJob[]
  completedJobs: ProcessingJob[]
  currentProgress: ProcessingProgress | null
  isProcessing: boolean
  
  // Actions
  setSelectedMode: (mode: ProcessingMode) => void
  updateBatchSettings: (settings: Partial<BatchSettings>) => void
  updatePrecisionSettings: (settings: Partial<PrecisionSettings>) => void
  addJob: (job: ProcessingJob) => void
  updateJob: (jobId: string, updates: Partial<ProcessingJob>) => void
  removeJob: (jobId: string) => void
  setProgress: (progress: ProcessingProgress) => void
  startProcessing: () => void
  stopProcessing: () => void
  resetProcessingStore: () => void
}

export interface AnalyticsStore {
  atsScores: Record<string, ATSScore>
  keywordAnalyses: Record<string, KeywordAnalysis>
  transformationMetrics: Record<string, TransformationMetrics>
  realTimeUpdates: boolean
  lastUpdated: string | null
  
  // Actions
  updateATSScore: (jobId: string, score: ATSScore) => void
  updateKeywordAnalysis: (jobId: string, analysis: KeywordAnalysis) => void
  updateTransformationMetrics: (jobId: string, metrics: TransformationMetrics) => void
  setRealTimeUpdates: (enabled: boolean) => void
  clearAnalytics: () => void
  resetAnalyticsStore: () => void
}

export interface UIStore {
  selectedMode: ProcessingMode | null
  processing: ProcessingUIState
  analytics: AnalyticsUIState
  mobile: MobileUIState
  accessibility: AccessibilityUIState
  modals: ModalState
  notifications: NotificationState[]
  
  // Actions
  setSelectedMode: (mode: ProcessingMode) => void
  updateProcessingUI: (updates: Partial<ProcessingUIState>) => void
  updateAnalyticsUI: (updates: Partial<AnalyticsUIState>) => void
  updateMobileUI: (updates: Partial<MobileUIState>) => void
  updateAccessibilityUI: (updates: Partial<AccessibilityUIState>) => void
  openModal: (modal: ModalType, props?: any) => void
  closeModal: (modal: ModalType) => void
  addNotification: (notification: NotificationState) => void
  removeNotification: (id: string) => void
  resetUIStore: () => void
}

// Additional UI State Types
export interface ModalState {
  upgradeModal: boolean
  enhancementPreview: boolean
  resultsComparison: boolean
  settingsModal: boolean
  helpModal: boolean
}

export type ModalType = keyof ModalState

export interface NotificationState {
  id: string
  type: NotificationType
  title: string
  message: string
  duration?: number
  actions?: NotificationAction[]
  timestamp: string
}

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface NotificationAction {
  label: string
  action: () => void
  style?: 'primary' | 'secondary'
}

// Combined Store Type for global state
export interface GlobalStore {
  user: UserStore
  processing: ProcessingStore
  analytics: AnalyticsStore
  ui: UIStore
}

// Legacy Store Types for backward compatibility
export interface StoreState {
  user: User | null
  ui: UIState
  processing: ProcessingUIState
  analytics: AnalyticsUIState
  cache: Record<string, any>
}

export interface StoreActions {
  setUser: (user: User) => void
  updateUserPreferences: (preferences: Partial<UserPreferences>) => void
  setSelectedMode: (mode: ProcessingMode) => void
  startProcessing: (mode: ProcessingMode, jobs: ProcessingJob[]) => void
  updateProcessingProgress: (progress: number, currentJob?: string) => void
  completeProcessing: (results: ProcessingResult[]) => void
  stopProcessing: () => void
  resetStore: () => void
}

export type Store = StoreState & StoreActions