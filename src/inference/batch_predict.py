from typing import List, Dict, Any
from .predict import SinglePredictor

class BatchPredictor:
    def __init__(self):
        self.predictor = SinglePredictor()

    def process_batch(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for case in cases:
            res = self.predictor.predict(
                image_path=case.get('image_path'),
                report_text=case.get('report_text', ''),
                vitals_dict=case.get('vitals', {})
            )
            res['case_id'] = case.get('id', 'N/A')
            results.append(res)
        return results
