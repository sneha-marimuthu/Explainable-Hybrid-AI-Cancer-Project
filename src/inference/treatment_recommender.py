CANCER_TYPES = {
    0: 'Breast Cancer',
    1: 'Lung Cancer',
    2: 'Colon Cancer'
}

class TreatmentRecommender:
    """Treatment recommendation based on cancer type and stage based on NCCN guidelines"""
    
    TREATMENT_GUIDELINES = {
        'normal': {
            'early': {
                'stage_n/a': ['Routine Clinical Surveillance', 'Annual Preventive Screening'],
                'stage_ii': ['Routine Clinical Surveillance', 'Annual Preventive Screening']
            }
        },
        'breast': {
            'early': {
                'stage_0': ['Lumpectomy (Wide Local Excision)', 'Adjuvant Radiation Therapy'],
                'stage_i': ['Breast-conserving Surgery (Lumpectomy)', 'Sentinel Lymph Node Biopsy', 'Adjuvant Endocrine Therapy (Tamoxifen / Anastrozole)'],
                'stage_ii': ['Total Mastectomy or Lumpectomy', 'Adjuvant Dose-Dense Chemotherapy (AC-T)', 'Hormonal Therapy + Radiation Therapy']
            },
            'advanced': {
                'stage_iii': ['Neoadjuvant Chemotherapy (AC-T)', 'Modified Radical Mastectomy', 'Post-Mastectomy Radiation Therapy', 'HER2 Targeted Therapy (Trastuzumab)'],
                'stage_iv': ['Systemic Targeted Therapy (CDK4/6 Inhibitors)', 'Palliative Radiation Therapy', 'First-line Immunotherapy & Endocrine Therapy']
            }
        },
        'lung': {
            'early': {
                'stage_i': ['Surgical Segmentectomy / Lobectomy', 'Active Post-Operative Surveillance (No Chemotherapy)'],
                'stage_ii': ['Surgical Lobectomy with Lymph Node Dissection', 'Adjuvant Platinum-Based Chemotherapy (Cisplatin + Vinorelbine)']
            },
            'advanced': {
                'stage_iii': ['Concurrent Definitive Chemoradiation (Cisplatin + RT)', 'Consolidation Immunotherapy (Durvalumab)'],
                'stage_iv': ['Targeted EGFR/ALK Inhibitor Therapy (Osimertinib)', 'First-line Anti-PD-L1 Immunotherapy (Pembrolizumab)', 'Systemic Platinum Chemotherapy']
            }
        },
        'colon': {
            'early': {
                'stage_i': ['Laparoscopic Partial Colectomy', 'Active Post-Operative Surveillance (No Chemotherapy Needed)'],
                'stage_ii': ['Surgical Colectomy with Clear Margins', 'Adjuvant Fluoropyrimidine Monotherapy (Capecitabine or 5-FU/LV)']
            },
            'advanced': {
                'stage_iii': ['Surgical Resection with Regional Lymphadenectomy', 'Adjuvant Combination Chemotherapy (FOLFOX or CAPOX for 3-6 Months)'],
                'stage_iv': ['Systemic Doublet/Triplet Chemotherapy (FOLFOXIRI)', 'Targeted Monoclonal Antibodies (Bevacizumab / Cetuximab)', 'Palliative Surgical Resection']
            }
        }
    }
    
    def __init__(self):
        self.treatment_guidelines = self.TREATMENT_GUIDELINES

    @staticmethod
    def recommend(cancer_type: str, confidence: float = None, stage: str = 'Stage II', biomarkers: dict = None) -> dict:
        """Recommend treatment based on cancer type, stage, and confidence"""
        if not cancer_type:
            cancer_type = 'breast'

        if 'normal' in str(cancer_type).lower() or 'benign' in str(cancer_type).lower():
            return {
                'cancer_type': 'Normal / Non-Malignant (No Cancer Detected)',
                'stage': 'N/A (Healthy)',
                'primary_regimen': 'None (Healthy / Non-Malignant)',
                'adjuvant_therapies': ['Routine Preventative Screening'],
                'recommended_treatments': ['None Required (Healthy / Non-Malignant)'],
                'confidence': confidence or 0.985,
                'guidelines_source': 'NCCN Clinical Practice Guidelines - Non-Malignant Evaluation'
            }
            
        cancer_key = str(cancer_type).lower().split()[0]
        if cancer_key not in TreatmentRecommender.TREATMENT_GUIDELINES:
            cancer_key = 'breast'
            
        guidelines = TreatmentRecommender.TREATMENT_GUIDELINES[cancer_key]
        
        stage_str = str(stage).lower().replace(' ', '_') if stage else 'stage_ii'
        
        # Match in reverse order (IV -> III -> II -> I -> 0) to avoid substring collisions
        if 'stage_iv' in stage_str or 'stage_4' in stage_str or 'iv' in stage_str:
            stage_key = 'stage_iv'
            group = 'advanced'
        elif 'stage_iii' in stage_str or 'stage_3' in stage_str or 'iii' in stage_str:
            stage_key = 'stage_iii'
            group = 'advanced'
        elif 'stage_ii' in stage_str or 'stage_2' in stage_str or 'ii' in stage_str:
            stage_key = 'stage_ii'
            group = 'early'
        elif 'stage_i' in stage_str or 'stage_1' in stage_str or 'stage_ia' in stage_str or 'stage_ib' in stage_str:
            stage_key = 'stage_i'
            group = 'early'
        elif 'stage_0' in stage_str or '0' in stage_str:
            stage_key = 'stage_0'
            group = 'early'
        else:
            stage_key = 'stage_ii'
            group = 'early'
            
        stage_dict = guidelines.get(group, guidelines['early'])
        treatments = stage_dict.get(stage_key, stage_dict.get('stage_ii', list(stage_dict.values())[0]))
        
        recommendations = list(treatments)
        if isinstance(biomarkers, dict):
            if biomarkers.get('her2_positive', False) and cancer_key == 'breast':
                recommendations.append('Trastuzumab (Herceptin) Targeted Therapy')
            if biomarkers.get('egfr_mutation', False) and cancer_key == 'lung':
                recommendations.append('Osimertinib EGFR Inhibitor Therapy')
                
        return {
            'cancer_type': cancer_type,
            'stage': stage_key.upper().replace('_', ' '),
            'primary_regimen': recommendations[0] if recommendations else 'Standard Clinical Surveillance',
            'adjuvant_therapies': recommendations[1:],
            'recommended_treatments': recommendations,
            'confidence': confidence,
            'guidelines_source': 'NCCN Clinical Practice Guidelines in Oncology'
        }
