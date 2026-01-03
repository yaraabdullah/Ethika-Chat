"""
Advanced curriculum generator that uses LLM to create detailed workshop content.
"""
import os
from typing import List, Dict, Any, Optional
from rag_system import RAGSystem
import json


class AdvancedCurriculumGenerator:
    """Generate detailed curriculum content using RAG + LLM."""
    
    def __init__(self, rag_system: RAGSystem, use_llm: bool = True, api_key: Optional[str] = None):
        """
        Initialize the advanced curriculum generator.
        
        Args:
            rag_system: Initialized RAGSystem instance
            use_llm: Whether to use LLM for content generation (requires Upstage API key)
            api_key: Upstage API key (defaults to environment variable or provided key)
        """
        self.rag = rag_system
        self.use_llm = use_llm
        # Using Upstage Solar Pro model
        self.model_name = "solar-pro"
        self.api_base = "https://api.upstage.ai/v1/chat/completions"
        
        if use_llm:
            try:
                import requests
                
                # Get API key from parameter or environment variable (required)
                if api_key:
                    self.api_key = api_key
                else:
                    self.api_key = os.getenv('UPSTAGE_API_KEY')
                    if not self.api_key:
                        raise ValueError(
                            "Upstage API key not found. Please set UPSTAGE_API_KEY environment variable. "
                            "For Railway: Add it in your project settings under 'Variables'."
                        )
                
                self.requests = requests
                print(f"✓ Upstage API initialized with model: {self.model_name}")
            except ImportError:
                print("Warning: requests package not installed. LLM features disabled.")
                print("Install it with: pip install requests")
                self.use_llm = False
            except Exception as e:
                print(f"Warning: Error initializing Upstage API: {e}")
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

IMPORTANT: Respond ONLY with valid JSON. Do not include any markdown formatting, code blocks, or explanatory text. Just return the raw JSON object.

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
            # Create the full prompt with system instruction
            system_message = "You are an expert AI education curriculum designer. Always respond with valid JSON only, no markdown or code blocks."
            user_message = prompt
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model_name,
                'messages': [
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': user_message}
                ],
                'temperature': 0.7,
                'max_tokens': 4096
            }
            
            # Generate content using Upstage API
            response = self.requests.post(self.api_base, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract content from Upstage API response
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content'].strip()
            else:
                raise Exception(f"Unexpected response format: {result}")
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            detailed_content = json.loads(content)
            return detailed_content
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response was: {content[:500]}...")
            return self._create_basic_content(curriculum, learning_objectives)
        except Exception as e:
            error_str = str(e)
            
            # Check if it's an authentication error (401/403)
            if "401" in error_str or "403" in error_str or "unauthorized" in error_str.lower():
                print("\n" + "="*60)
                print("🚨 API KEY ERROR")
                print("="*60)
                print("Your Upstage API key is invalid or expired.")
                print("\nSOLUTION: Check your API key:")
                print("1. Go to https://console.upstage.ai")
                print("2. Navigate to API Keys section")
                print("3. Copy your API key")
                print("4. Update UPSTAGE_API_KEY in Railway (Variables tab) or locally")
                print("="*60 + "\n")
                # Re-raise with helpful message
                raise Exception(
                    "🚨 API KEY ERROR: Your Upstage API key is invalid or expired.\n\n"
                    "SOLUTION: Check your API key:\n"
                    "1. Go to https://console.upstage.ai\n"
                    "2. Navigate to API Keys section\n"
                    "3. Copy your API key\n"
                    "4. Update UPSTAGE_API_KEY in Railway (Variables tab) or locally\n\n"
                    f"Original error: {error_str}"
                )
            
            print(f"Error generating LLM content: {e}")
            import traceback
            traceback.print_exc()
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

