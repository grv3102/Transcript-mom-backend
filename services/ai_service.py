import os
import re
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Load environment variables
load_dotenv()

class AIService:
    """High-performance AI service using OpenAI via Emergent LLM integration"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
            
        # Use GPT-4o-mini for optimal performance and cost
        self.model_name = "gpt-4o-mini"
        self.provider = "openai"
        
        # Initialize chat client with optimized settings
        self.chat_client = LlmChat(
            api_key=self.api_key,
            session_id="meeting-transcript-processor",
            system_message=self._get_system_prompt()
        ).with_model(self.provider, self.model_name)
        
    def _get_system_prompt(self) -> str:
        """Optimized system prompt for meeting transcript processing"""
        return """
You are an expert meeting minutes processor. Your task is to analyze meeting transcripts and extract structured information with high accuracy.

You must return a JSON response with exactly these fields:
- summary: Clear bullet-point summary of key discussion points
- decisions: Array of confirmed decisions made (not suggestions)
- agenda: Array of topics/agenda items discussed
- participants: Array of unique valid participant names (no junk like "date", "need", etc.)
- topics: Array of objects with 'topic' and 'confidence' score (0.0-1.0)
- actionItems: Array of objects with 'task', 'owner', 'deadline', 'status'
- processed_at: Current ISO timestamp
- model_used: The AI model used for processing

Be precise and only extract what's clearly present in the transcript. For action items, extract only clear commitments with owners.
"""
    
    async def process_transcript(self, transcript: str) -> Dict[str, Any]:
        """Process meeting transcript with AI and fallback mechanisms"""
        try:
            # Primary AI processing
            result = await self._ai_process(transcript)
            
            # Validate and enhance with fallback if needed
            validated_result = self._validate_and_enhance(result, transcript)
            
            return validated_result
            
        except Exception as e:
            print(f"AI processing failed: {e}")
            # Fallback to regex-based processing
            return await self._fallback_process(transcript)
    
    async def _ai_process(self, transcript: str) -> Dict[str, Any]:
        """Primary AI processing using OpenAI"""
        prompt = f"""
Analyze this meeting transcript and extract structured information:

{transcript}

Return the result as a JSON object with the required fields. Ensure:
- Participants are real names only (no junk words)
- Action items have clear owners and tasks
- Decisions are confirmed commitments, not discussions
- Topics include confidence scores
- Summary is concise bullet points
"""
        
        user_message = UserMessage(text=prompt)
        response = await self.chat_client.send_message(user_message)
        
        # Parse JSON response
        import json
        try:
            # Extract JSON from response if wrapped in markdown
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            
            # Add metadata
            result['processed_at'] = datetime.utcnow().isoformat()
            result['model_used'] = f"{self.provider}/{self.model_name}"
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print(f"Response: {response}")
            raise
    
    def _validate_and_enhance(self, result: Dict[str, Any], transcript: str) -> Dict[str, Any]:
        """Validate AI results and enhance with fallback processing"""
        # Ensure all required fields exist
        required_fields = ['summary', 'decisions', 'agenda', 'participants', 'topics', 'actionItems']
        for field in required_fields:
            if field not in result:
                result[field] = []
        
        # Clean participants (remove junk words)
        if result['participants']:
            result['participants'] = self._clean_participants(result['participants'])
        
        # If critical fields are empty, try fallback extraction
        if not result['participants']:
            result['participants'] = self._extract_participants_fallback(transcript)
        
        if not result['actionItems']:
            result['actionItems'] = self._extract_action_items_fallback(transcript)
        
        return result
    
    def _clean_participants(self, participants: List[str]) -> List[str]:
        """Clean participant list, removing junk and duplicates"""
        junk_words = {
            'date', 'time', 'meeting', 'call', 'team', 'group', 'project', 
            'need', 'will', 'can', 'should', 'would', 'discussion', 'agenda',
            'minutes', 'action', 'item', 'decision', 'summary', 'everyone',
            'all', 'we', 'us', 'they', 'them', 'it', 'this', 'that'
        }
        
        cleaned = []
        for participant in participants:
            participant = participant.strip()
            # Must be 2+ chars, start with capital, and not in junk words
            if (len(participant) >= 2 and 
                participant[0].isupper() and 
                participant.lower() not in junk_words and
                not participant.lower().startswith(('http', 'www', '@'))):
                cleaned.append(participant)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(cleaned))
    
    def _extract_participants_fallback(self, transcript: str) -> List[str]:
        """Extract participants using regex fallback"""
        # Look for patterns like "Name:" or "Name said" or "Name mentioned"
        patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):',  # Name: format
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|mentioned|noted|stated)',  # Name said format
        ]
        
        participants = set()
        for pattern in patterns:
            matches = re.findall(pattern, transcript)
            participants.update(matches)
        
        return self._clean_participants(list(participants))
    
    def _extract_action_items_fallback(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract action items using regex fallback"""
        action_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:will|should|needs to|must)\s+(.+?)(?=\.|\n|$)',
            r'Action item[^:]*:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:will|should|needs to|must)\s+(.+?)(?=\.|\n|$)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:agreed to|committed to)\s+(.+?)(?=\.|\n|$)'
        ]
        
        action_items = []
        for pattern in action_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    owner, task = match
                    action_items.append({
                        'task': task.strip(),
                        'owner': owner.strip(),
                        'deadline': 'Not specified',
                        'status': 'Pending'
                    })
        
        return action_items
    
    async def _fallback_process(self, transcript: str) -> Dict[str, Any]:
        """Fallback processing when AI fails"""
        print("Using fallback processing...")
        
        return {
            'summary': ["Meeting transcript processed with fallback method", "AI processing temporarily unavailable"],
            'decisions': [],
            'agenda': ["General discussion"],
            'participants': self._extract_participants_fallback(transcript),
            'topics': [{'topic': 'General meeting discussion', 'confidence': 0.7}],
            'actionItems': self._extract_action_items_fallback(transcript),
            'processed_at': datetime.utcnow().isoformat(),
            'model_used': 'fallback/regex'
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        try:
            has_key = bool(self.api_key)
            return {
                'status': 'healthy' if has_key else 'unhealthy',
                'model': f"{self.provider}/{self.model_name}",
                'has_api_key': has_key,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
