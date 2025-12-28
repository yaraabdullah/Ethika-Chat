"""
Prompt-based curriculum generator - ChatGPT-like interface for educational content.
"""
import os
from typing import Dict, Any, Optional
from rag_system import RAGSystem
import json


class PromptBasedGenerator:
    """Generate educational content from natural language prompts using RAG + LLM."""
    
    def __init__(self, rag_system: RAGSystem, api_key: Optional[str] = None):
        """
        Initialize the prompt-based generator.
        
        Args:
            rag_system: Initialized RAGSystem instance
            api_key: Gemini API key (defaults to environment variable or provided key)
        """
        self.rag = rag_system
        # Use gemini-2.5-flash (works on free tier!)
        # This is the current free tier model that actually works
        self.model_name = "gemini-2.5-flash"
        
        try:
            import google.generativeai as genai
            
            # Get API key from parameter, environment variable, or use default
            if api_key:
                self.api_key = api_key
            else:
                self.api_key = os.getenv('GEMINI_API_KEY') or "AIzaSyDcbzxiB8WbCxDS0teU9wP-VAeBSZCxkhU"
            
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            print(f"✓ Gemini API initialized with model: {self.model_name}")
        except ImportError:
            raise ImportError("google-generativeai package not installed. Install it with: pip install google-generativeai")
        except Exception as e:
            raise Exception(f"Error initializing Gemini API: {e}")
    
    def generate_from_prompt(
        self,
        prompt: str,
        max_tokens: int = 4096,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Generate educational content from a natural language prompt.
        Searches comprehensively for all related resources.
        
        Args:
            prompt: Natural language description of what content to create
            max_tokens: Maximum tokens for the response
            
        Returns:
            Dictionary containing generated content and retrieved resources
        """
        import google.generativeai as genai
        
        # Step 1: Comprehensive search for all relevant resources
        print(f"🔍 Searching database comprehensively for all relevant resources...")
        
        # Search with a high limit to get as many relevant resources as possible
        all_results = []
        seen_ids = set()
        
        # First, do a broad search
        search_results = self.rag.search(
            query=prompt,
            limit=50  # Get many results
        )
        
        for result in search_results:
            if result['id'] not in seen_ids:
                all_results.append(result)
                seen_ids.add(result['id'])
        
        # Also search for key topics/concepts from the prompt
        # Extract meaningful phrases and terms
        import re
        
        # Find quoted phrases, topics after "on", "about", "for", etc.
        topics = []
        
        # Extract phrases in quotes
        quoted = re.findall(r'"([^"]+)"', prompt)
        topics.extend(quoted)
        
        # Extract topics after common prepositions
        topic_patterns = [
            r'(?:on|about|regarding|concerning)\s+([^,\.!?]+)',
            r'(?:for|with|including)\s+([^,\.!?]+)',
        ]
        for pattern in topic_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            topics.extend([m.strip() for m in matches if len(m.strip()) > 3])
        
        # Also extract important nouns (words that are likely topics)
        # Remove common stop words and get meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can'}
        words = [w.lower().strip('.,!?;:') for w in prompt.split() if len(w) > 4 and w.lower() not in stop_words]
        topics.extend(words[:8])  # Add top meaningful words
        
        # Remove duplicates and search for each topic
        unique_topics = list(set(topics))[:10]  # Limit to 10 unique topics
        
        print(f"🔍 Also searching for related topics: {', '.join(unique_topics[:5])}...")
        
        for topic in unique_topics:
            if len(topic.strip()) > 2:  # Only search meaningful topics
                try:
                    keyword_results = self.rag.search(
                        query=topic,
                        limit=15
                    )
                    for result in keyword_results:
                        if result['id'] not in seen_ids:
                            all_results.append(result)
                            seen_ids.add(result['id'])
                except:
                    pass  # Skip if search fails
        
        search_results = all_results
        
        if not search_results:
            return {
                "error": "No relevant resources found in the database. Please try a different prompt or add more resources.",
                "resources": [],
                "content": None
            }
        
        print(f"✅ Found {len(search_results)} relevant resources")
        
        # Format resources for display (used in both LLM and fallback modes)
        # Remove duplicates first based on file_path or title
        seen_resources = {}
        unique_results = []
        for resource in search_results:
            metadata = resource['metadata']
            file_path = metadata.get('file_path', '')
            title = metadata.get('title', '').strip()
            
            # Use file_path as primary key, fallback to title
            key = file_path or title or resource.get('id', '')
            
            if key and key not in seen_resources:
                seen_resources[key] = resource
                unique_results.append(resource)
            elif not key:
                # If no key, still add it (shouldn't happen but be safe)
                unique_results.append(resource)
        
        search_results = unique_results
        if len(search_results) < len(all_results):
            print(f"✅ Removed {len(all_results) - len(search_results)} duplicates. {len(search_results)} unique resources")
        
        formatted_resources = []
        for i, resource in enumerate(search_results, 1):
            metadata = resource['metadata']
            document = resource.get('document', '')
            
            # Try to extract title from document if metadata is empty
            title = metadata.get('title', '').strip()
            if not title and document:
                import re
                # Try multiple patterns to find title
                # Pattern 1: title: "Title Text"
                quoted_match = re.search(r'title:\s*"([^"]+)"', document, re.IGNORECASE)
                if quoted_match:
                    title = quoted_match.group(1).strip()
                else:
                    # Pattern 2: Title: Title Text (after Content: or in YAML)
                    title_match = re.search(r'(?:Content:\s*)?---\s*\n.*?title:\s*"([^"]+)"', document, re.IGNORECASE | re.DOTALL)
                    if title_match:
                        title = title_match.group(1).strip()
                    else:
                        # Pattern 3: Title: Title Text (simple)
                        title_match = re.search(r'Title:\s*([^\n]+)', document, re.IGNORECASE)
                        if title_match:
                            title = title_match.group(1).strip().strip('"\'')
            
            # Try to extract author from document if metadata is empty
            author = metadata.get('author', '').strip()
            if not author and document:
                import re
                # Pattern 1: author: "Author Text"
                quoted_author = re.search(r'author:\s*"([^"]+)"', document, re.IGNORECASE)
                if quoted_author:
                    author = quoted_author.group(1).strip()
                else:
                    # Pattern 2: Author: Author Text
                    author_match = re.search(r'Author:\s*([^\n]+)', document, re.IGNORECASE)
                    if author_match:
                        author = author_match.group(1).strip().strip('"\'')
            
            # Fallbacks
            title = title or 'Untitled Resource'
            author = author or 'Unknown Author'
            url = metadata.get('url', '').strip() or ''
            
            formatted_resources.append({
                "number": i,
                "title": title,
                "author": author,
                "url": url,
                "relevance": resource.get('distance', 0),
                "citation": f"[Source {i}]",
                "document": document[:500]  # Preview
            })
        
        # If LLM is disabled, return curated resources only
        if not use_llm:
            return {
                "content": self._create_content_from_resources_only(prompt, search_results),
                "resources": formatted_resources,
                "num_resources_used": len(search_results),
                "prompt": prompt,
                "llm_used": False,
                "note": "Content generated from database resources only (LLM disabled)"
            }
        
        # Step 2: Format resources for the LLM
        resources_text = self._format_resources_for_prompt(search_results)
        
        # Step 3: Create the full prompt for Gemini
        # Create resource references for citations (use formatted_resources with extracted titles)
        resource_refs = []
        for res in formatted_resources:
            ref = {
                'number': res['number'],
                'title': res['title'],
                'author': res['author'],
                'url': res['url']
            }
            resource_refs.append(ref)
        
        full_prompt = f"""You are an expert AI education content creator. A user wants you to create a COMPLETE, FULL educational workshop/curriculum based on their request.

USER REQUEST:
{prompt}

RELEVANT RESOURCES FROM DATABASE:
{resources_text}

CRITICAL REQUIREMENTS - YOU MUST CREATE A COMPLETE WORKSHOP/CURRICULUM:

1. **COMPLETE STRUCTURE REQUIRED:**
   - Title and Overview (compelling introduction)
   - Target Audience (clearly specified)
   - Duration (exact time)
   - Learning Objectives (3-5 specific, measurable objectives - COMPLETE ALL OF THEM)
   - Detailed Schedule/Timeline (break down the entire duration with specific activities)
   - Activity Descriptions (detailed instructions for each activity)
   - Materials Needed (complete list)
   - Assessment/Evaluation Methods
   - Conclusion/Wrap-up
   - Sources Section (at the end)

2. **CONTENT REQUIREMENTS:**
   - The content must be COMPLETE and READY TO USE
   - Include ALL sections - do not cut off or leave sections incomplete
   - Each learning objective must be fully written out
   - Every activity must have detailed instructions
   - The schedule must cover the ENTIRE duration specified
   - Be thorough, detailed, and comprehensive

3. **CITATION REQUIREMENTS:**
   - You MUST cite sources throughout using [Source 1], [Source 2], etc.
   - When using information from resources, cite them naturally
   - Include a complete "Sources" section at the end with all cited resources

4. **QUALITY REQUIREMENTS:**
   - Content should be practical, engaging, and suitable for the specified audience
   - Include specific activities, examples, and actionable steps
   - Make it professional and ready for immediate use

RESOURCE REFERENCE NUMBERS:
{chr(10).join([f"[Source {r['number']}]: {r['title']} by {r['author']}" + (f" ({r['url']})" if r['url'] else "") for r in resource_refs])}

IMPORTANT: 
- Generate the COMPLETE, FULL workshop/curriculum in MARKDOWN format
- Use proper markdown formatting: # for main headings, ## for section headings, ### for subsections, **bold** for emphasis, - for lists, etc.
- Format tables using markdown table syntax
- Make it professional, well-structured, and easy to read
- Do not stop mid-sentence or leave sections incomplete
- Make sure ALL learning objectives are fully written, ALL activities are described in detail, and the entire workshop structure is complete from start to finish
- The output should be ready-to-use markdown that looks professional when rendered"""

        # Step 4: Generate content using Gemini
        print(f"🤖 Generating content with Gemini...")
        try:
            import time
            
            # Retry logic for quota errors
            max_retries = 3
            retry_delay = 5  # seconds
            
            for attempt in range(max_retries):
                try:
                    response = self.client.generate_content(
                        full_prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.7,
                            top_p=0.95,
                            top_k=40,
                            max_output_tokens=8192,  # Increased for complete workshops/curriculums
                        )
                    )
                    
                    # Handle response - newer API might return different format
                    if hasattr(response, 'text'):
                        generated_content = response.text.strip()
                    elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                        generated_content = response.candidates[0].content.parts[0].text.strip()
                    else:
                        generated_content = str(response).strip()
                    
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    error_str = str(e)
                    
                    # Check if it's a quota error
                    if "quota" in error_str.lower() or "429" in error_str:
                        if attempt < max_retries - 1:
                            # Extract retry delay from error if available
                            if "retry in" in error_str.lower():
                                import re
                                delay_match = re.search(r'retry in ([\d.]+)s', error_str.lower())
                                if delay_match:
                                    retry_delay = float(delay_match.group(1)) + 2
                            
                            print(f"⚠️ Quota limit reached. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue
                        else:
                            # Quota exceeded - return resources without LLM generation
                            print("⚠️ Quota exceeded. Returning curated resources without LLM generation.")
                            return {
                                "content": self._create_content_from_resources_only(prompt, search_results),
                                "resources": formatted_resources,
                                "num_resources_used": len(search_results),
                                "prompt": prompt,
                                "llm_used": False,
                                "quota_error": True,
                                "note": "⚠️ LLM quota exceeded. Content generated from database resources only. Please wait a few minutes and try again for LLM-generated content, or check your quota at https://ai.dev/usage?tab=rate-limit"
                            }
                    else:
                        # Not a quota error, re-raise
                        raise
            
            if 'generated_content' not in locals():
                return {
                    "error": "Failed to generate content after multiple attempts",
                    "resources": [],
                    "content": None
                }
            
            return {
                "content": generated_content,
                "resources": formatted_resources,
                "num_resources_used": len(search_results),
                "prompt": prompt,
                "llm_used": True
            }
        except Exception as e:
            error_str = str(e)
            # If it's a quota error, return resources without LLM
            if "quota" in error_str.lower() or "429" in error_str:
                return {
                    "content": self._create_content_from_resources_only(prompt, search_results),
                    "resources": formatted_resources,
                    "num_resources_used": len(search_results),
                    "prompt": prompt,
                    "llm_used": False,
                    "quota_error": True,
                    "note": "⚠️ LLM quota exceeded. Content generated from database resources only. Please wait and try again for LLM-generated content."
                }
            return {
                "error": f"Error generating content: {error_str[:300]}",
                "resources": formatted_resources,
                "content": None
            }
    
    def _create_content_from_resources_only(self, prompt: str, resources: list) -> str:
        """Create content summary from resources when LLM is not available."""
        content = f"""# Educational Content: {prompt}

## Overview
Based on your request, I've curated the following resources from our database. While AI-generated content is currently unavailable due to API quota limits, these resources directly address your needs.

## Your Request
{prompt}

## Curated Resources

"""
        
        for i, resource in enumerate(resources, 1):
            metadata = resource['metadata']
            content += f"\n### [Source {i}] {metadata.get('title', 'Untitled')}\n\n"
            content += f"**Author:** {metadata.get('author', 'Unknown')}\n\n"
            
            if metadata.get('url'):
                content += f"**URL:** {metadata.get('url')}\n\n"
            
            # Add tags
            tags = metadata.get('tags', '[]')
            if tags and tags != '[]':
                try:
                    tags_list = json.loads(tags) if isinstance(tags, str) else tags
                    if tags_list:
                        content += f"**Tags:** {', '.join(tags_list)}\n\n"
                except:
                    pass
            
            # Add relevance/description
            if metadata.get('relevance'):
                content += f"**Relevance:** {metadata['relevance']}\n\n"
            
            # Add content preview
            doc_preview = resource.get('document', '')
            if doc_preview:
                content += f"**Content Preview:**\n{doc_preview[:800]}\n\n"
            
            content += "---\n\n"
        
        content += f"""
## How to Use These Resources

1. Review each resource above to find content relevant to your needs
2. Combine information from multiple sources as needed
3. Adapt the content for your specific audience and context
4. Check the URLs provided for full resource details

## Note
This content was generated from database resources only. For AI-generated, comprehensive content, please wait a few minutes and try again when the API quota resets.

## Sources Reference
"""
        
        for i, resource in enumerate(resources, 1):
            metadata = resource['metadata']
            content += f"- [Source {i}]: {metadata.get('title', 'Untitled')} by {metadata.get('author', 'Unknown')}"
            if metadata.get('url'):
                content += f" ({metadata.get('url')})"
            content += "\n"
        
        return content
    
    def _format_resources_for_prompt(self, resources: list) -> str:
        """Format resources for LLM prompt."""
        text = ""
        for i, resource in enumerate(resources, 1):
            metadata = resource['metadata']
            text += f"\n--- Resource {i} ---\n"
            text += f"Title: {metadata.get('title', 'Untitled')}\n"
            text += f"Author: {metadata.get('author', 'Unknown')}\n"
            
            if metadata.get('url'):
                text += f"URL: {metadata.get('url')}\n"
            
            # Add tags
            tags = metadata.get('tags', '[]')
            if tags and tags != '[]':
                try:
                    tags_list = json.loads(tags) if isinstance(tags, str) else tags
                    if tags_list:
                        text += f"Tags: {', '.join(tags_list)}\n"
                except:
                    pass
            
            # Add target audience
            audience = metadata.get('target_audience', '[]')
            if audience and audience != '[]':
                try:
                    audience_list = json.loads(audience) if isinstance(audience, str) else audience
                    if audience_list:
                        text += f"Target Audience: {', '.join(audience_list)}\n"
                except:
                    pass
            
            # Add relevance/description
            if metadata.get('relevance'):
                text += f"Relevance: {metadata['relevance']}\n"
            
            # Include document preview
            doc_preview = resource.get('document', '')[:500]
            if doc_preview:
                text += f"Content Preview: {doc_preview}...\n"
            
            text += "\n"
        
        return text

