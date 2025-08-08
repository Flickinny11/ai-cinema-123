#!/usr/bin/env python3
"""
Natural Language Processor for Cinema AI Pipeline
Handles user prompts with multi-character dialogue, actions, and descriptions
Production implementation using spaCy and transformers
"""

import os
import re
import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import openai
from openai import OpenAI

# Import NLP libraries
try:
    import spacy
    from spacy import displacy
    from spacy.matcher import Matcher
except ImportError:
    spacy = None

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
except ImportError:
    pipeline = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Character:
    """Represents a character in the scene"""
    name: str
    description: str = ""
    voice_characteristics: str = ""
    emotions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)

@dataclass
class DialogueLine:
    """Represents a line of dialogue"""
    character: str
    text: str
    emotion: str = "neutral"
    action: str = ""
    timing: float = 0.0
    non_verbal: List[str] = field(default_factory=list)

@dataclass
class ParsedScene:
    """Represents a parsed scene from natural language"""
    description: str
    characters: List[Character]
    dialogue: List[DialogueLine]
    actions: List[str]
    environment: str
    mood: str
    duration_estimate: int

class NaturalLanguageProcessor:
    """Production natural language processor for cinema prompts"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        
        # Initialize DeepSeek client for advanced processing
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1"
            )
            self.model = "deepseek-chat"
        else:
            self.client = None
            logger.warning("No DeepSeek API key - using local processing only")
        
        # Initialize spaCy for NLP
        self.nlp = None
        self.matcher = None
        self._load_nlp_models()
        
        # Initialize NER pipeline for character extraction
        self.ner_pipeline = None
        self._load_ner_pipeline()
    
    def _load_nlp_models(self):
        """Load spaCy models for natural language processing"""
        try:
            if spacy:
                # Try to load English model
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except OSError:
                    logger.info("Downloading spaCy English model...")
                    import subprocess
                    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
                    self.nlp = spacy.load("en_core_web_sm")
                
                # Initialize matcher for dialogue patterns
                self.matcher = Matcher(self.nlp.vocab)
                
                # Pattern for quoted dialogue: "text"
                dialogue_pattern = [{"TEXT": {"REGEX": r'^".*"$'}}]
                self.matcher.add("DIALOGUE", [dialogue_pattern])
                
                # Pattern for character names (capitalized words before dialogue)
                character_pattern = [{"POS": "PROPN"}, {"TEXT": ":"}, {"TEXT": {"REGEX": r'^".*"$'}}]
                self.matcher.add("CHARACTER_DIALOGUE", [character_pattern])
                
                logger.info("✅ spaCy NLP models loaded")
            else:
                logger.warning("spaCy not available - installing...")
                import subprocess
                subprocess.run(["pip", "install", "spacy"], check=True)
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
                import spacy
                self.nlp = spacy.load("en_core_web_sm")
                
        except Exception as e:
            logger.error(f"Failed to load spaCy models: {e}")
            self.nlp = None
    
    def _load_ner_pipeline(self):
        """Load Named Entity Recognition pipeline"""
        try:
            if pipeline:
                self.ner_pipeline = pipeline(
                    "ner",
                    model="dbmdz/bert-large-cased-finetuned-conll03-english",
                    aggregation_strategy="simple"
                )
                logger.info("✅ NER pipeline loaded")
        except Exception as e:
            logger.error(f"Failed to load NER pipeline: {e}")
            self.ner_pipeline = None
    
    async def process_natural_language_prompt(self, prompt: str) -> ParsedScene:
        """Process natural language prompt into structured scene data"""
        logger.info(f"Processing natural language prompt: {prompt[:100]}...")
        
        try:
            # Use DeepSeek for advanced processing if available
            if self.client:
                return await self._process_with_deepseek(prompt)
            else:
                return await self._process_with_local_nlp(prompt)
                
        except Exception as e:
            logger.error(f"Natural language processing failed: {e}")
            return await self._process_with_fallback(prompt)
    
    async def _process_with_deepseek(self, prompt: str) -> ParsedScene:
        """Process prompt using DeepSeek v3 for advanced understanding"""
        
        system_prompt = """You are an expert AI that understands natural language descriptions of video scenes with multiple characters, dialogue, and actions.

Parse the user's natural language description and extract:
1. Characters mentioned (names, descriptions, emotions)
2. Dialogue in quotes with speaker identification
3. Actions and movements described
4. Scene environment and setting
5. Overall mood and atmosphere
6. Estimated scene duration

Return a JSON structure with this format:
{
    "description": "Overall scene description",
    "characters": [
        {
            "name": "Character name",
            "description": "Physical/personality description",
            "voice_characteristics": "Voice description if mentioned",
            "emotions": ["emotion1", "emotion2"],
            "actions": ["action1", "action2"]
        }
    ],
    "dialogue": [
        {
            "character": "Character name",
            "text": "Dialogue text without quotes",
            "emotion": "emotion",
            "action": "concurrent action",
            "timing": 0.0,
            "non_verbal": ["laugh", "sigh", "gesture"]
        }
    ],
    "actions": ["General scene actions"],
    "environment": "Setting description",
    "mood": "Overall mood",
    "duration_estimate": 10
}

Be very precise in identifying:
- Character names (even if implied)
- Exact dialogue text from quotes
- Emotional states and non-verbal cues
- Physical actions and movements
- Environmental details"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this scene description:\n\n{prompt}"}
                ],
                temperature=0.3,  # Lower temperature for more precise parsing
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON response
            try:
                data = json.loads(result)
                return self._convert_to_parsed_scene(data)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return self._convert_to_parsed_scene(data)
                else:
                    raise Exception("No valid JSON found in response")
                    
        except Exception as e:
            logger.error(f"DeepSeek processing failed: {e}")
            return await self._process_with_local_nlp(prompt)
    
    async def _process_with_local_nlp(self, prompt: str) -> ParsedScene:
        """Process prompt using local NLP models"""
        logger.info("Processing with local NLP models...")
        
        # Extract characters using NER
        characters = self._extract_characters(prompt)
        
        # Extract dialogue using regex and spaCy
        dialogue = self._extract_dialogue(prompt)
        
        # Extract actions and descriptions
        actions = self._extract_actions(prompt)
        
        # Determine environment and mood
        environment = self._extract_environment(prompt)
        mood = self._extract_mood(prompt)
        
        # Estimate duration based on content
        duration_estimate = self._estimate_duration(prompt, dialogue)
        
        return ParsedScene(
            description=prompt[:200] + "..." if len(prompt) > 200 else prompt,
            characters=characters,
            dialogue=dialogue,
            actions=actions,
            environment=environment,
            mood=mood,
            duration_estimate=duration_estimate
        )
    
    def _extract_characters(self, text: str) -> List[Character]:
        """Extract character information from text"""
        characters = []
        
        # Use NER to find person names
        if self.ner_pipeline:
            entities = self.ner_pipeline(text)
            person_names = [ent['word'] for ent in entities if ent['entity_group'] == 'PER']
        else:
            # Fallback: look for capitalized words before dialogue
            person_names = re.findall(r'\b([A-Z][a-z]+)(?=\s*[:""])', text)
        
        # Remove duplicates and common false positives
        person_names = list(set(person_names))
        person_names = [name for name in person_names if name.lower() not in ['the', 'and', 'but', 'or']]
        
        for name in person_names:
            # Extract character description from context
            description = self._extract_character_description(text, name)
            emotions = self._extract_character_emotions(text, name)
            actions = self._extract_character_actions(text, name)
            
            characters.append(Character(
                name=name,
                description=description,
                emotions=emotions,
                actions=actions
            ))
        
        return characters
    
    def _extract_dialogue(self, text: str) -> List[DialogueLine]:
        """Extract dialogue lines from text"""
        dialogue_lines = []
        
        # Pattern 1: Character: "dialogue"
        pattern1 = r'([A-Z][a-z]+)\s*:\s*"([^"]+)"'
        matches1 = re.finditer(pattern1, text)
        
        for match in matches1:
            character = match.group(1)
            dialogue_text = match.group(2)
            
            # Extract emotion and non-verbal cues
            emotion = self._extract_emotion_from_dialogue(dialogue_text)
            non_verbal = self._extract_non_verbal_cues(dialogue_text)
            
            dialogue_lines.append(DialogueLine(
                character=character,
                text=dialogue_text,
                emotion=emotion,
                non_verbal=non_verbal
            ))
        
        # Pattern 2: "dialogue" said Character
        pattern2 = r'"([^"]+)"\s+(?:said|says|asks|replies|responds)\s+([A-Z][a-z]+)'
        matches2 = re.finditer(pattern2, text)
        
        for match in matches2:
            dialogue_text = match.group(1)
            character = match.group(2)
            
            emotion = self._extract_emotion_from_dialogue(dialogue_text)
            non_verbal = self._extract_non_verbal_cues(dialogue_text)
            
            dialogue_lines.append(DialogueLine(
                character=character,
                text=dialogue_text,
                emotion=emotion,
                non_verbal=non_verbal
            ))
        
        # Pattern 3: Just quoted text (assign to unnamed character)
        if not dialogue_lines:
            pattern3 = r'"([^"]+)"'
            matches3 = re.finditer(pattern3, text)
            
            for i, match in enumerate(matches3):
                dialogue_text = match.group(1)
                
                dialogue_lines.append(DialogueLine(
                    character=f"Character{i+1}",
                    text=dialogue_text,
                    emotion=self._extract_emotion_from_dialogue(dialogue_text),
                    non_verbal=self._extract_non_verbal_cues(dialogue_text)
                ))
        
        return dialogue_lines
    
    def _extract_character_description(self, text: str, character_name: str) -> str:
        """Extract description for a specific character"""
        # Look for descriptive text near character name
        pattern = rf'{character_name}[^.]*?([^.]*(?:tall|short|young|old|beautiful|handsome|wearing|dressed)[^.]*)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _extract_character_emotions(self, text: str, character_name: str) -> List[str]:
        """Extract emotions for a specific character"""
        emotions = []
        
        # Look for emotion words near character name
        emotion_words = ['happy', 'sad', 'angry', 'excited', 'nervous', 'calm', 'worried', 'surprised', 'confused']
        
        for emotion in emotion_words:
            pattern = rf'{character_name}[^.]*?{emotion}|{emotion}[^.]*?{character_name}'
            if re.search(pattern, text, re.IGNORECASE):
                emotions.append(emotion)
        
        return emotions
    
    def _extract_character_actions(self, text: str, character_name: str) -> List[str]:
        """Extract actions for a specific character"""
        actions = []
        
        # Look for action verbs near character name
        action_pattern = rf'{character_name}\s+(walks|runs|sits|stands|looks|turns|moves|enters|exits|grabs|holds)'
        matches = re.finditer(action_pattern, text, re.IGNORECASE)
        
        for match in matches:
            actions.append(match.group(1))
        
        return actions
    
    def _extract_actions(self, text: str) -> List[str]:
        """Extract general scene actions"""
        actions = []
        
        # Look for action verbs and movement descriptions
        action_patterns = [
            r'(walks? (?:to|into|towards)[^.]*)',
            r'(runs? (?:to|into|towards)[^.]*)',
            r'(enters? [^.]*)',
            r'(exits? [^.]*)',
            r'(sits? (?:down|on)[^.]*)',
            r'(stands? (?:up|on)[^.]*)',
            r'(looks? (?:at|towards)[^.]*)',
            r'(turns? (?:to|towards)[^.]*)'
        ]
        
        for pattern in action_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                actions.append(match.group(1))
        
        return actions
    
    def _extract_environment(self, text: str) -> str:
        """Extract environment/setting description"""
        # Look for location indicators
        location_patterns = [
            r'(?:in|at|inside|outside)\s+(?:a|an|the)?\s*([^.]*(?:room|house|park|street|office|restaurant|cafe|bar|store|school|hospital|church|beach|forest|mountain|city|town|village)[^.]*)',
            r'(?:INT\.|EXT\.)\s*([^-\n]*)',
            r'(?:setting|location|place):\s*([^\n]*)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: look for descriptive environment words
        env_words = ['indoor', 'outdoor', 'sunny', 'dark', 'bright', 'cozy', 'spacious', 'crowded', 'quiet', 'noisy']
        found_env = [word for word in env_words if word in text.lower()]
        
        if found_env:
            return ', '.join(found_env)
        
        return "unspecified location"
    
    def _extract_mood(self, text: str) -> str:
        """Extract overall mood/atmosphere"""
        mood_indicators = {
            'happy': ['happy', 'joyful', 'cheerful', 'upbeat', 'positive', 'bright'],
            'sad': ['sad', 'melancholy', 'depressing', 'gloomy', 'somber'],
            'tense': ['tense', 'suspenseful', 'dramatic', 'intense', 'serious'],
            'romantic': ['romantic', 'intimate', 'loving', 'tender', 'sweet'],
            'comedic': ['funny', 'humorous', 'comedic', 'amusing', 'lighthearted'],
            'mysterious': ['mysterious', 'enigmatic', 'puzzling', 'strange', 'eerie']
        }
        
        text_lower = text.lower()
        
        for mood, indicators in mood_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return mood
        
        return 'neutral'
    
    def _extract_emotion_from_dialogue(self, dialogue_text: str) -> str:
        """Extract emotion from dialogue text"""
        # Look for emotional indicators in the text
        if '!' in dialogue_text:
            return 'excited'
        elif '?' in dialogue_text:
            return 'questioning'
        elif '...' in dialogue_text:
            return 'hesitant'
        elif dialogue_text.isupper():
            return 'angry'
        else:
            return 'neutral'
    
    def _extract_non_verbal_cues(self, text: str) -> List[str]:
        """Extract non-verbal cues from text"""
        non_verbal_patterns = [
            r'\[([^\]]+)\]',  # [laughs], [sighs]
            r'\(([^\)]+)\)',  # (smiling), (crying)
        ]
        
        non_verbal = []
        for pattern in non_verbal_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                non_verbal.append(match.group(1).lower())
        
        return non_verbal
    
    def _estimate_duration(self, text: str, dialogue: List[DialogueLine]) -> int:
        """Estimate scene duration based on content"""
        # Base duration on word count and dialogue
        word_count = len(text.split())
        dialogue_count = len(dialogue)
        
        # Rough estimates
        base_duration = max(5, word_count // 20)  # ~20 words per second
        dialogue_duration = dialogue_count * 3  # ~3 seconds per dialogue line
        
        return min(30, max(base_duration, dialogue_duration))  # Cap at 30 seconds
    
    def _convert_to_parsed_scene(self, data: Dict) -> ParsedScene:
        """Convert dictionary data to ParsedScene object"""
        characters = []
        for char_data in data.get('characters', []):
            characters.append(Character(
                name=char_data.get('name', ''),
                description=char_data.get('description', ''),
                voice_characteristics=char_data.get('voice_characteristics', ''),
                emotions=char_data.get('emotions', []),
                actions=char_data.get('actions', [])
            ))
        
        dialogue = []
        for dial_data in data.get('dialogue', []):
            dialogue.append(DialogueLine(
                character=dial_data.get('character', ''),
                text=dial_data.get('text', ''),
                emotion=dial_data.get('emotion', 'neutral'),
                action=dial_data.get('action', ''),
                timing=dial_data.get('timing', 0.0),
                non_verbal=dial_data.get('non_verbal', [])
            ))
        
        return ParsedScene(
            description=data.get('description', ''),
            characters=characters,
            dialogue=dialogue,
            actions=data.get('actions', []),
            environment=data.get('environment', ''),
            mood=data.get('mood', 'neutral'),
            duration_estimate=data.get('duration_estimate', 10)
        )
    
    async def _process_with_fallback(self, prompt: str) -> ParsedScene:
        """Fallback processing for when other methods fail"""
        logger.info("Using fallback natural language processing...")
        
        # Very basic parsing
        characters = [Character(name="Character1")]
        
        # Extract any quoted text as dialogue
        quotes = re.findall(r'"([^"]+)"', prompt)
        dialogue = []
        
        for i, quote in enumerate(quotes):
            dialogue.append(DialogueLine(
                character=f"Character{i+1}",
                text=quote,
                emotion="neutral"
            ))
        
        return ParsedScene(
            description=prompt,
            characters=characters,
            dialogue=dialogue,
            actions=["scene action"],
            environment="unspecified",
            mood="neutral",
            duration_estimate=10
        )