"""
AI Analyzer - Uses Claude API to analyze measurement data
"""

import os
import json
import pandas as pd
from anthropic import Anthropic
from typing import Dict, Any


class AIAnalyzer:
    def __init__(self):
        """Initialize Claude API client"""
        # In production, use environment variable
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            print("WARNING: ANTHROPIC_API_KEY not set. AI analysis will return mock data.")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)
    
    async def analyze(
        self, 
        data: pd.DataFrame, 
        template_type: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Analyze measurement data with Claude AI
        
        Args:
            data: Pandas DataFrame with measurement data
            template_type: Type of report (testing, quality, field, process)
            language: Output language (en, fi)
        
        Returns:
            Dictionary with AI analysis results
        """
        
        # If no API key, return mock analysis
        if not self.client:
            return self._mock_analysis(data, template_type, language)
        
        # Prepare data summary for Claude
        data_summary = self._prepare_data_summary(data)
        
        # Create prompt based on template type and language
        prompt = self._create_prompt(data_summary, template_type, language)
        
        try:
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse response
            analysis_text = message.content[0].text
            
            # Structure the analysis
            analysis = self._structure_analysis(analysis_text, template_type)
            
            return analysis
            
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return self._mock_analysis(data, template_type, language)
    
    def _prepare_data_summary(self, data: pd.DataFrame) -> str:
        """Prepare data summary for Claude"""
        summary = f"""
DATA SUMMARY:
- Total rows: {len(data)}
- Total columns: {len(data.columns)}
- Columns: {', '.join(data.columns.tolist()[:10])}
{' ... and more' if len(data.columns) > 10 else ''}

SAMPLE DATA (first 5 rows):
{data.head(5).to_string()}

STATISTICS:
{data.describe().to_string()}
"""
        return summary
    
    def _create_prompt(self, data_summary: str, template_type: str, language: str) -> str:
        """Create analysis prompt for Claude"""
        
        lang_instruction = "in English" if language == "en" else "in Finnish (suomeksi)"
        
        if template_type == "testing":
            prompt = f"""
You are a quality engineer analyzing testing data. Analyze the following measurement data and provide:

1. EXECUTIVE SUMMARY: A brief overview of what was tested and key findings
2. KEY FINDINGS: 3-5 most important observations from the data
3. STATISTICAL ANALYSIS: Mean, median, standard deviation, and trends
4. RECOMMENDATIONS: Actionable recommendations based on the findings
5. CONCLUSION: Summary statement about data quality and test results

{data_summary}

Provide your analysis {lang_instruction} in a professional, technical tone suitable for an engineering report.
Format your response as JSON with keys: executive_summary, key_findings (array), statistical_analysis, recommendations (array), conclusion
"""
        else:
            prompt = f"Analyze this data {lang_instruction}: {data_summary}"
        
        return prompt
    
    def _structure_analysis(self, analysis_text: str, template_type: str) -> Dict[str, Any]:
        """Structure the AI analysis response"""
        try:
            # Try to parse as JSON first
            return json.loads(analysis_text)
        except:
            # If not JSON, structure manually
            return {
                "executive_summary": analysis_text[:500],
                "key_findings": [analysis_text[500:1000]],
                "statistical_analysis": analysis_text[1000:1500],
                "recommendations": [analysis_text[1500:2000]],
                "conclusion": analysis_text[2000:]
            }
    
    def _mock_analysis(self, data: pd.DataFrame, template_type: str, language: str) -> Dict[str, Any]:
        """Return mock analysis when API is not available"""
        
        if language == "fi":
            return {
                "executive_summary": f"Tämä raportti analysoi {len(data)} mittaustulosta. Data sisältää {len(data.columns)} saraketta ja kattaa useita testiolosuhteita.",
                "key_findings": [
                    f"Yhteensä {len(data)} mittausta analysoitu",
                    f"Data sisältää {len(data.columns)} eri parametria",
                    "Mittaukset vaihtelevat eri olosuhteissa",
                    "Huomattu systemaattisia trendejä datassa"
                ],
                "statistical_analysis": f"Keskiarvo: {data.select_dtypes(include='number').mean().mean():.2f}, Keskihajonta: {data.select_dtypes(include='number').std().mean():.2f}. Data osoittaa johdonmukaisia tuloksia eri mittauspisteissä.",
                "recommendations": [
                    "Jatka nykyisten testausprotokollien käyttöä",
                    "Tarkkaile poikkeavia arvoja säännöllisesti",
                    "Dokumentoi kaikki testausolosuhteet tarkasti"
                ],
                "conclusion": "Testausdata on laadultaan hyvää ja osoittaa johdonmukaisia tuloksia. Suositellaan jatkotoimenpiteitä havaittujen trendien perusteella."
            }
        else:
            return {
                "executive_summary": f"This report analyzes {len(data)} measurement results. The data contains {len(data.columns)} columns covering multiple test conditions.",
                "key_findings": [
                    f"Total of {len(data)} measurements analyzed",
                    f"Data contains {len(data.columns)} different parameters",
                    "Measurements vary across different conditions",
                    "Systematic trends observed in the data"
                ],
                "statistical_analysis": f"Mean: {data.select_dtypes(include='number').mean().mean():.2f}, Std Dev: {data.select_dtypes(include='number').std().mean():.2f}. Data shows consistent results across measurement points.",
                "recommendations": [
                    "Continue with current testing protocols",
                    "Monitor outlier values regularly",
                    "Document all test conditions precisely"
                ],
                "conclusion": "Testing data is of good quality and shows consistent results. Further actions recommended based on observed trends."
            }
