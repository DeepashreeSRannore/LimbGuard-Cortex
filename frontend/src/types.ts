export interface Advice {
  status?: string;
  urgency?: string;
  recommended_action?: string;
  action?: string;
  home_care?: string;
  sugar_maintenance?: string;
  skin_care?: string;
  footwear?: string;
  scheduling?: string;
  [key: string]: string | undefined;
}

export interface PredictionResult {
  success: boolean;
  demo_mode: boolean;
  classification: string;
  display_name: string;
  advice: Advice;
  rag_guidance?: string | null;
}

export interface ApiError {
  detail: string;
}
