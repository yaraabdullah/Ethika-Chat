"""
Advanced curriculum generator that uses LLM to create detailed workshop content.
"""
import os
from typing import List, Dict, Any, Optional
from rag_system import RAGSystem
import json


class AdvancedCurriculumGenerator:
    """Generate detailed curriculum content using RAG + LLM."""
    
    def __init__(self, rag_system: RAGSystem, use_llm: bool = True):
        """
        Initialize the advanced curriculum generator.
        
        Args:
            rag_system: Initialized RAGSystem instance
            use_llm: Whether to use LLM for content generation (requires OpenAI API key)
        """
        self.rag = rag_system
        self.use_llm = use_llm
        
        if use_llm:
            try:
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                else:
                    print("Warning: OPENAI_API_KEY not found. LLM features disabled.")
                    self.use_llm = False
            except ImportError:
                print("Warning: openai package not installed. LLM features disabled.")
                self.use_llm = False
    
    def generate_detailed_curriculum(
        self,
        institution: str,
        target_audience: List[str],
        topics: List[str],
        duration_hours: float = 2.0,
        preferred_types: Optional[List[str]] = None,
        learning_objectives: Optional[List[str]] = None,
        institution_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a detailed curriculum with full content.
        
        Args:
            institution: Institution name
            target_audience: List of target audiences
            topics: List of topics to cover
            duration_hours: Workshop duration
            preferred_types: Preferred resource types
            learning_objectives: Specific learning objectives
            institution_context: Additional context about the institution
            
        Returns:
            Detailed curriculum dictionary
        """
        # First, get resources using RAG
        curriculum = self.rag.generate_curriculum(
            institution=institution,
            target_audience=target_audience,
            topics=topics,
            duration_hours=duration_hours,
            preferred_types=preferred_types,
            limit_per_topic=5
        )
        
        # Enhance with detailed content
        curriculum['detailed_content'] = self._create_detailed_content(
            curriculum,
            learning_objectives,
            institution_context
        )
        
        return curriculum
    
    def _create_detailed_content(
        self,
        curriculum: Dict[str, Any],
        learning_objectives: Optional[List[str]],
        institution_context: Optional[str]
    ) -> Dict[str, Any]:
        """Create detailed workshop content."""
        
        if not self.use_llm:
            # Fallback: create structured content without LLM
            return self._create_basic_content(curriculum, learning_objectives)
        
        # Use LLM to generate detailed content
        resources_text = self._format_resources_for_prompt(curriculum['resources'])
        
        prompt = f"""You are an expert AI education curriculum designer. Create a detailed workshop curriculum based on the following resources and requirements.

INSTITUTION: {curriculum['institution']}
TARGET AUDIENCE: {', '.join(curriculum['target_audience'])}
TOPICS: {', '.join(curriculum['topics'])}
DURATION: {curriculum['duration_hours']} hours

AVAILABLE RESOURCES:
{resources_text}
"""
        
        if learning_objectives:
            prompt += f"\nLEARNING OBJECTIVES:\n" + "\n".join(f"- {obj}" for obj in learning_objectives)
        
        if institution_context:
            prompt += f"\nINSTITUTION CONTEXT:\n{institution_context}"
        
        prompt += """

Create a detailed curriculum that includes:
1. Workshop Overview (brief description, goals)
2. Learning Objectives (3-5 specific objectives)
3. Detailed Schedule (with time allocations and activities)
4. Activity Descriptions (for each resource/activity)
5. Assessment Ideas (how to evaluate learning)
6. Materials Needed
7. Additional Notes

Format as JSON with the following structure:
{
  "overview": "...",
  "learning_objectives": ["...", "..."],
  "schedule": [
    {
      "time": "00:00-00:30",
      "activity": "...",
      "description": "...",
      "resource": "..."
    }
  ],
  "activities": [
    {
      "title": "...",
      "description": "...",
      "duration_minutes": 30,
      "materials": ["..."],
      "instructions": "..."
    }
  ],
  "assessment": {
    "formative": ["..."],
    "summative": "..."
  },
  "materials_needed": ["..."],
  "notes": "..."
}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert AI education curriculum designer. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            detailed_content = json.loads(content)
            return detailed_content
        except Exception as e:
            print(f"Error generating LLM content: {e}")
            return self._create_basic_content(curriculum, learning_objectives)
    
    def _format_resources_for_prompt(self, resources: List[Dict[str, Any]]) -> str:
        """Format resources for LLM prompt."""
        text = ""
        for i, resource in enumerate(resources, 1):
            metadata = resource['metadata']
            text += f"\n{i}. {metadata.get('title', 'Untitled')}\n"
            text += f"   Author: {metadata.get('author', 'Unknown')}\n"
            if metadata.get('url'):
                text += f"   URL: {metadata.get('url')}\n"
            
            tags = json.loads(metadata.get('tags', '[]')) if isinstance(metadata.get('tags'), str) else metadata.get('tags', [])
            if tags:
                text += f"   Tags: {', '.join(tags)}\n"
            
            if metadata.get('relevance'):
                text += f"   Relevance: {metadata['relevance']}\n"
            
            # Include document preview
            doc_preview = resource.get('document', '')[:200]
            if doc_preview:
                text += f"   Preview: {doc_preview}...\n"
        
        return text
    
    def _create_basic_content(
        self,
        curriculum: Dict[str, Any],
        learning_objectives: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Create basic structured content without LLM."""
        objectives = learning_objectives or [
            f"Understand key concepts in {topic}" for topic in curriculum['topics']
        ]
        
        activities = []
        for resource in curriculum['resources']:
            metadata = resource['metadata']
            activities.append({
                "title": metadata.get('title', 'Untitled'),
                "description": metadata.get('relevance', 'Educational activity'),
                "duration_minutes": 30,
                "materials": ["Computer/Tablet", "Internet access"],
                "instructions": f"Follow the activity guide: {metadata.get('url', 'See resource file')}"
            })
        
        return {
            "overview": f"Workshop on {', '.join(curriculum['topics'])} for {', '.join(curriculum['target_audience'])} students.",
            "learning_objectives": objectives,
            "schedule": curriculum['schedule'],
            "activities": activities,
            "assessment": {
                "formative": ["Observation during activities", "Q&A sessions"],
                "summative": "Reflection exercise at the end"
            },
            "materials_needed": ["Computer/Tablet", "Internet access", "Projector"],
            "notes": "Customize activities based on student needs and available time."
        }

