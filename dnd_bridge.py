import os
import json
import tempfile
from typing import Optional, Dict, List, Tuple
import gradio as gr
import google.generativeai as genai

# ==============================
# Voice Support Detection
# ==============================
try:
    import speech_recognition as sr
    from gtts import gTTS
    VOICE_AVAILABLE = True
    print("✓ Voice support enabled")
except ImportError:
    VOICE_AVAILABLE = False
    print("⚠ Voice libraries not available. Install: pip install SpeechRecognition gtts pyaudio")

# ==============================
# Gemini Configuration
# ==============================
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Initialize with API key
genai.configure(api_key=API_KEY)

# Available Gemini models
MODELS = {
    "pro3": "gemini-3-pro",
    "pro3Flash": "gemini-3-flash-preview",
    "pro25": "gemini-2.5-pro",
    "pro25Flash": "gemini-2.5-flash",
    "proOld": "gemini-1.5-pro",
    "flashOld": "gemini-1.5-flash",
    "proOld-002": "gemini-1.5-pro-002"
}
DEFAULT_MODEL = MODELS["pro3Flash"]

# ==============================
# Global Session Management
# ==============================
class SessionManager:
    def __init__(self):
        self.global_log: List[Dict] = []
        self.players: List['PlayerAgent'] = []
        self.environmental_settings: Dict = {}
        self.reactive_mode: str = "individual"  # individual, free_discussion, stat_check
        self.discussion_round: int = 0
        self.max_discussion_rounds: int = 4
        self.pending_reactions: List[Dict] = []
    
    def add_log_entry(self, player_id: int, text: str, event_type: str = "response", emotion: str = "neutral"):
        """Add entry to global session log with emotional tracking"""
        self.global_log.append({
            "player_id": player_id,
            "type": event_type,
            "text": text,
            "emotion": emotion,
            "round": self.discussion_round if self.reactive_mode == "free_discussion" else None
        })
    
    def get_player_count(self) -> int:
        return len(self.players)
    
    def load_environmental_settings(self, json_text: str) -> str:
        """Load environmental/world settings for the session"""
        try:
            settings = json.loads(json_text)
            self.environmental_settings = settings
            return f"✓ Environmental settings loaded successfully.\n" + \
                   f"Campaign: {settings.get('campaign_name', 'N/A')}\n" + \
                   f"Location: {settings.get('current_location', 'N/A')}"
        except json.JSONDecodeError as e:
            return f"❌ JSON Parse Error: {str(e)}"
        except Exception as e:
            return f"❌ Error loading settings: {str(e)}"
    
    def start_reactive_discussion(self):
        """Start a new reactive discussion round"""
        self.reactive_mode = "free_discussion"
        self.discussion_round = 0
        self.pending_reactions.clear()
    
    def end_reactive_discussion(self):
        """End reactive discussion mode"""
        self.reactive_mode = "individual"
        self.discussion_round = 0
        self.pending_reactions.clear()
    
    def clear_session(self):
        """Clear all session data"""
        self.global_log.clear()
        self.players.clear()
        self.environmental_settings.clear()
        self.pending_reactions.clear()

session = SessionManager()

# ==============================
# Player Agent Class
# ==============================
class PlayerAgent:
    def __init__(self, player_id: int, model_name: str = DEFAULT_MODEL):
        self.player_id = player_id
        self.model_name = model_name
        self.config: Dict = {}
        self.history: List[Dict] = []
        self.config_loaded = False
        self.previous_session_metadata: Dict = {}
        self.current_emotion: str = "neutral"
        self.emotional_trajectory: List[Dict] = []
        self.model = genai.GenerativeModel(model_name)
    
    def load_config(self, json_text: str, metadata_json: str = "") -> str:
        """Load and validate JSON configuration with optional previous session metadata"""
        try:
            config = json.loads(json_text)
            self.config = config
            self.config_loaded = True
            
            # Load previous session metadata if provided
            if metadata_json and metadata_json.strip():
                try:
                    metadata = json.loads(metadata_json)
                    self.previous_session_metadata = metadata
                    
                    # Initialize emotional state from metadata if available
                    if "emotional_journey" in metadata and metadata["emotional_journey"]:
                        last_emotion = metadata["emotional_journey"][-1]
                        self.current_emotion = last_emotion if isinstance(last_emotion, str) else "neutral"
                    
                    metadata_info = f"\n✓ Previous session metadata loaded"
                except:
                    metadata_info = "\n⚠ Could not parse metadata (continuing without it)"
            else:
                metadata_info = ""
            
            # Log configuration load
            session.add_log_entry(
                self.player_id, 
                f"Configuration loaded: {config.get('character_name', 'Unknown')}", 
                "config"
            )
            
            # Display stats if available
            stats_info = ""
            if "ability_scores" in config:
                stats = config["ability_scores"]
                mods = config.get("modifiers", {})
                stats_info = f"\n📊 Stats: STR {stats.get('strength', 10)}({mods.get('strength', 0):+d}) " + \
                           f"DEX {stats.get('dexterity', 10)}({mods.get('dexterity', 0):+d}) " + \
                           f"CON {stats.get('constitution', 10)}({mods.get('constitution', 0):+d})\n" + \
                           f"        INT {stats.get('intelligence', 10)}({mods.get('intelligence', 0):+d}) " + \
                           f"WIS {stats.get('wisdom', 10)}({mods.get('wisdom', 0):+d}) " + \
                           f"CHA {stats.get('charisma', 10)}({mods.get('charisma', 0):+d})"
            
            return f"✓ Player {self.player_id} configuration loaded successfully.\n" + \
                   f"Character: {config.get('character_name', 'N/A')}\n" + \
                   f"Class: {config.get('character_class', 'N/A')} (Level {config.get('level', '?')})\n" + \
                   f"Gender: {config.get('gender', 'Not specified')}" + \
                   stats_info + \
                   metadata_info
        
        except json.JSONDecodeError as e:
            return f"❌ JSON Parse Error: {str(e)}"
        except Exception as e:
            return f"❌ Configuration Error: {str(e)}"
    
    def generate_response(self, user_input: str, response_mode: str = "full") -> Tuple[str, str]:
        """Generate character response based on configuration and history
        
        Args:
            user_input: The input prompt
            response_mode: "full", "reaction", or "stat_check"
            
        Returns:
            Tuple of (response_text, detected_emotion)
        """
        if not self.config_loaded:
            return "⚠ Please load character configuration first.", "neutral"
        
        try:
            # Build comprehensive context
            full_context = self._build_full_context(user_input, response_mode)
            
            # Generate response using old API
            response = self.model.generate_content(full_context)
            
            response_text = response.text.strip()
            
            # Extract emotion from response
            emotion = self._extract_emotion(response_text)
            
            # Update emotional tracking
            self.current_emotion = emotion
            self.emotional_trajectory.append({
                "round": session.discussion_round,
                "emotion": emotion,
                "trigger": user_input[:100]
            })
            
            # Update history
            self.history.append({
                "role": "user",
                "content": user_input
            })
            self.history.append({
                "role": "character",
                "content": response_text,
                "emotion": emotion
            })
            
            # Log to global session
            session.add_log_entry(self.player_id, response_text, "response", emotion)
            
            return response_text, emotion
        
        except Exception as e:
            error_msg = f"❌ Generation Error: {str(e)}"
            print(f"Player {self.player_id}: {error_msg}")
            return error_msg, "frustrated"
    
    def _build_full_context(self, user_input: str, response_mode: str) -> str:
        """Build comprehensive context including emotional state and response mode"""
        
        context_parts = [
            "You are roleplaying as a D&D character. Stay in character at all times.",
            "",
            "=== CHARACTER CONFIGURATION ===",
            json.dumps(self.config, indent=2)
        ]
        
        # Add current emotional state
        if self.current_emotion != "neutral":
            context_parts.extend([
                "",
                f"=== CURRENT EMOTIONAL STATE ===",
                f"You are currently feeling: {self.current_emotion}",
                f"Let this emotion subtly influence your response naturally."
            ])
        
        # Add environmental settings if available
        if session.environmental_settings:
            context_parts.extend([
                "",
                "=== WORLD & ENVIRONMENTAL SETTINGS ===",
                json.dumps(session.environmental_settings, indent=2)
            ])
        
        # Add previous session metadata if available
        if self.previous_session_metadata:
            context_parts.extend([
                "",
                "=== PREVIOUS SESSION SUMMARY ===",
                "This character has history from previous sessions:",
                json.dumps(self.previous_session_metadata, indent=2)
            ])
        
        # Add reactive discussion context if in that mode
        if session.reactive_mode == "free_discussion" and session.pending_reactions:
            context_parts.extend([
                "",
                "=== ONGOING DISCUSSION (Round {}) ===".format(session.discussion_round),
                "Other characters have just said:"
            ])
            for reaction in session.pending_reactions:
                char_name = reaction.get("character_name", f"Player {reaction.get('player_id')}")
                context_parts.append(f"  {char_name}: {reaction.get('text')}")
            context_parts.append("")
            context_parts.append("React naturally to what others have said. Keep it conversational.")
        
        # Add conversation history
        history_text = self._format_history()
        context_parts.extend([
            "",
            "=== CONVERSATION HISTORY ===",
            history_text
        ])
        
        # Add current input and mode-specific instructions
        context_parts.extend([
            "",
            "=== CURRENT INPUT ===",
            user_input,
            "",
            "=== INSTRUCTIONS ==="
        ])
        
        # Mode-specific instructions
        if response_mode == "reaction":
            context_parts.extend([
                "⚠️ REACTION MODE - Keep your response SHORT and NATURAL:",
                "- 1-3 sentences maximum",
                "- A gesture, facial expression, or brief statement",
                "- Quick emotional reaction or immediate action",
                "- Examples: 'I raise my axe defensively' or 'Wait! I sense something...'",
                "- DO NOT write long speeches or detailed actions",
                "- This is a quick back-and-forth conversation"
            ])
        elif response_mode == "stat_check":
            context_parts.extend([
                "⚠️ STAT CHECK MODE:",
                "- If attempting something requiring ability check, state it clearly",
                "- Format: 'Using my [ABILITY], I attempt to [ACTION]'",
                "- Example: 'Using my Strength, I try to force open the door'",
                "- Example: 'With my Charisma, I attempt to persuade the guard'",
                "- The GM will handle dice rolls and resolution"
            ])
        else:  # full response
            context_parts.extend([
                "- Respond fully and naturally in character",
                "- Consider your stats when describing actions",
                "- Reference ability scores when relevant"
            ])
        
        # Common instructions
        context_parts.extend([
            "- Stay in character based on personality, class, and background",
            "- Your emotional state influences your reactions naturally",
            "- Reference previous session events when relevant",
            "- Be aware of environmental settings",
            "- Do not break the fourth wall",
            "- Do not mention configuration, metadata, emotions explicitly, or system details",
            "",
            "CHARACTER'S RESPONSE:"
        ])
        
        return "\n".join(context_parts)
    
    def _extract_emotion(self, response_text: str) -> str:
        """Extract dominant emotion from response using simple heuristics"""
        # This is a lightweight approach - LLM naturally expresses emotion in text
        # We just detect it for tracking purposes
        
        emotion_keywords = {
            "angry": ["furious", "rage", "angry", "snarl", "growl", "thunder"],
            "fearful": ["afraid", "fear", "terrified", "nervous", "worry", "anxious"],
            "joyful": ["laugh", "smile", "happy", "joy", "delight", "pleased"],
            "sad": ["sad", "sorrow", "grief", "weep", "cry", "despair"],
            "determined": ["determined", "resolve", "focus", "steel", "ready"],
            "suspicious": ["suspect", "distrust", "wary", "cautious", "doubt"],
            "curious": ["curious", "wonder", "interest", "examine", "investigate"],
            "confident": ["confident", "certain", "sure", "bold", "proud"]
        }
        
        text_lower = response_text.lower()
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion
        
        return self.current_emotion if self.current_emotion else "neutral"
    
    def _format_history(self) -> str:
        """Format conversation history for context"""
        if not self.history:
            return "No previous conversation in this session."
        
        formatted = []
        for entry in self.history[-10:]:  # Keep last 10 exchanges
            role = entry["role"].upper()
            content = entry["content"]
            emotion = entry.get("emotion", "")
            emotion_tag = f" [{emotion}]" if emotion and emotion != "neutral" else ""
            formatted.append(f"{role}{emotion_tag}: {content}")
        
        return "\n".join(formatted)
    
    def get_stats_display(self) -> str:
        """Get formatted stats display"""
        if not self.config_loaded or "ability_scores" not in self.config:
            return "No stats configured"
        
        stats = self.config["ability_scores"]
        mods = self.config.get("modifiers", {})
        
        lines = []
        lines.append(f"STR: {stats.get('strength', 10)} ({mods.get('strength', 0):+d})")
        lines.append(f"DEX: {stats.get('dexterity', 10)} ({mods.get('dexterity', 0):+d})")
        lines.append(f"CON: {stats.get('constitution', 10)} ({mods.get('constitution', 0):+d})")
        lines.append(f"INT: {stats.get('intelligence', 10)} ({mods.get('intelligence', 0):+d})")
        lines.append(f"WIS: {stats.get('wisdom', 10)} ({mods.get('wisdom', 0):+d})")
        lines.append(f"CHA: {stats.get('charisma', 10)} ({mods.get('charisma', 0):+d})")
        
        return " | ".join(lines)
    
    def extract_metadata(self) -> str:
        """Extract structured metadata from session"""
        try:
            character_info = {
                "character_id": self.player_id,
                "character_name": self.config.get("character_name", "Unknown"),
                "character_class": self.config.get("character_class", "Unknown"),
                "level": self.config.get("level", 1)
            }
            
            prompt = f"""Analyze the following D&D session log and extract structured metadata for this character.

CHARACTER INFO:
{json.dumps(character_info, indent=2)}

EMOTIONAL TRAJECTORY THIS SESSION:
{json.dumps(self.emotional_trajectory, indent=2)}

FULL SESSION LOG:
{json.dumps(session.global_log, indent=2)}

Extract and return a JSON object with this EXACT structure:
{{
  "character_id": {self.player_id},
  "character_name": "name from config",
  "major_events": ["event1", "event2", ...],
  "emotional_journey": ["emotion1 from X event", "emotion2 from Y event", ...],
  "inventory_changes": [
    {{"item": "item_name", "action": "gained/lost/equipped", "details": "description"}}
  ],
  "relationships": [
    {{"character": "name", "status": "ally/enemy/neutral/complex", "details": "description"}}
  ],
  "unresolved_threads": ["thread1", "thread2", ...],
  "character_development": ["development1", "development2", ...],
  "stat_checks_attempted": [
    {{"ability": "strength", "action": "forced door", "success": true/false}}
  ]
}}

IMPORTANT: Return ONLY valid JSON. No markdown, no explanations, no backticks."""

            response = self.model.generate_content(prompt)
            
            result = response.text.strip()
            if result.startswith("```json"):
                result = result.replace("```json", "").replace("```", "").strip()
            
            return result
        
        except Exception as e:
            return json.dumps({
                "error": f"Metadata extraction failed: {str(e)}",
                "character_id": self.player_id
            }, indent=2)

# ==============================
# Voice Utilities with Gender Support
# ==============================
def speech_to_text() -> Tuple[Optional[str], Optional[str]]:
    """Capture voice input and convert to text"""
    if not VOICE_AVAILABLE:
        return None, "Voice input unavailable. Please install: pip install SpeechRecognition gtts pyaudio"
    
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
        
        print("🔄 Processing speech...")
        text = recognizer.recognize_google(audio)
        print(f"✓ Recognized: {text}")
        return text, None
    
    except sr.WaitTimeoutError:
        return None, "⚠ No speech detected. Please try again."
    except sr.UnknownValueError:
        return None, "⚠ Could not understand audio. Please speak clearly."
    except sr.RequestError as e:
        return None, f"⚠ Speech recognition service error: {str(e)}"
    except Exception as e:
        return None, f"⚠ Voice input error: {str(e)}"

def text_to_speech(text: str, gender: str = "neutral") -> Optional[str]:
    """Convert text to speech with gender-appropriate voice"""
    if not VOICE_AVAILABLE:
        return None
    
    try:
        tld_map = {
            "male": "com.au",
            "female": "com",
            "neutral": "co.uk"
        }
        
        tld = tld_map.get(gender.lower(), "com")
        tts = gTTS(text=text, lang='en', tld=tld, slow=False)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp.name)
        return tmp.name
    except Exception as e:
        print(f"⚠ Text-to-speech error: {str(e)}")
        return None

# ==============================
# UI Handler Functions
# ==============================
def add_player(model_choice: str) -> str:
    """Create a new player agent"""
    player_id = session.get_player_count() + 1
    model_name = MODELS.get(model_choice, DEFAULT_MODEL)
    player = PlayerAgent(player_id, model_name)
    session.players.append(player)
    
    return f"✓ Player {player_id} created using {model_name}"

def load_environmental_settings(json_text: str) -> str:
    """Load environmental/world settings"""
    return session.load_environmental_settings(json_text)

def load_player_config(player_index: int, json_text: str, metadata_json: str) -> str:
    """Load configuration for a specific player with optional metadata"""
    try:
        idx = int(player_index) - 1
        if idx < 0 or idx >= len(session.players):
            return f"❌ Invalid player number. Valid range: 1-{len(session.players)}"
        
        return session.players[idx].load_config(json_text, metadata_json)
    except ValueError:
        return "❌ Invalid player number format"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def player_listen(player_index: int) -> str:
    """Capture voice input for a specific player"""
    text, error = speech_to_text()
    if error:
        return f"[Voice Error] {error}"
    return text or ""

def player_talk(player_index: int, input_text: str) -> Tuple[str, Optional[str]]:
    """Process input and generate response for a specific player"""
    try:
        idx = int(player_index) - 1
        if idx < 0 or idx >= len(session.players):
            return f"❌ Invalid player number. Valid range: 1-{len(session.players)}", None
        
        if not input_text.strip():
            return "⚠ Please provide input text or use the Listen button.", None
        
        player = session.players[idx]
        response, emotion = player.generate_response(input_text, "full")
        
        gender = player.config.get('gender', 'neutral')
        audio_path = text_to_speech(response, gender)
        
        # Add emotion indicator
        emotion_emoji = {
            "angry": "😠", "fearful": "😰", "joyful": "😊",
            "sad": "😢", "determined": "💪", "suspicious": "🤨",
            "curious": "🤔", "confident": "😎", "neutral": ""
        }
        emotion_display = f"[{emotion_emoji.get(emotion, '')} {emotion}] " if emotion != "neutral" else ""
        
        return emotion_display + response, audio_path
    
    except Exception as e:
        return f"❌ Error: {str(e)}", None

def broadcast_to_all() -> str:
    """Capture voice and broadcast to all players"""
    text, error = speech_to_text()
    if error:
        return f"[Voice Error] {error}"
    
    if not text:
        return "⚠ No input captured"
    
    return text

def process_reactive_discussion(broadcast_text: str, rounds: int) -> str:
    """Process reactive discussion mode with multiple rounds"""
    if not broadcast_text.strip():
        return "⚠ No broadcast text provided"
    
    if not session.players:
        return "⚠ No players available. Please add players first."
    
    configured_players = [p for p in session.players if p.config_loaded]
    if not configured_players:
        return "⚠ No configured players available."
    
    session.start_reactive_discussion()
    all_rounds = []
    
    # Initial prompt
    all_rounds.append(f"📢 GAME MASTER: {broadcast_text}")
    all_rounds.append("=" * 80)
    
    # Run discussion rounds
    for round_num in range(1, rounds + 1):
        session.discussion_round = round_num
        session.pending_reactions.clear()
        
        all_rounds.append(f"\n🔄 ROUND {round_num}")
        all_rounds.append("-" * 80)
        
        # Each player reacts
        for player in configured_players:
            char_name = player.config.get('character_name', f'Player {player.player_id}')
            
            # First round uses original prompt, subsequent rounds use conversation context
            if round_num == 1:
                prompt = broadcast_text
            else:
                prompt = "React to what others have said and continue the conversation naturally."
            
            response, emotion = player.generate_response(prompt, "reaction")
            
            # Store reaction for next round
            session.pending_reactions.append({
                "player_id": player.player_id,
                "character_name": char_name,
                "text": response,
                "emotion": emotion
            })
            
            # Emotion emoji
            emotion_emoji = {
                "angry": "😠", "fearful": "😰", "joyful": "😊",
                "sad": "😢", "determined": "💪", "suspicious": "🤨",
                "curious": "🤔", "confident": "😎", "neutral": "💬"
            }
            emoji = emotion_emoji.get(emotion, "💬")
            
            all_rounds.append(f"{emoji} {char_name}: {response}")
        
        # Check for stat check keywords or conflicts
        stat_check_detected = any(
            any(keyword in reaction["text"].lower() 
                for keyword in ["using my", "with my", "strength", "dexterity", "charisma", 
                               "intelligence", "wisdom", "constitution", "i roll", "check"])
            for reaction in session.pending_reactions
        )
        
        if stat_check_detected:
            all_rounds.append("\n⚠️ STAT CHECK DETECTED - GM Resolution Needed")
            break
    
    session.end_reactive_discussion()
    
    all_rounds.append("\n" + "=" * 80)
    all_rounds.append("💡 Discussion complete. GM can now respond or resolve actions.")
    
    return "\n".join(all_rounds)

def process_stat_check_broadcast(broadcast_text: str) -> str:
    """Process broadcast in stat check mode - players can attempt stat-based actions"""
    if not broadcast_text.strip():
        return "⚠ No broadcast text provided"
    
    if not session.players:
        return "⚠ No players available."
    
    configured_players = [p for p in session.players if p.config_loaded]
    if not configured_players:
        return "⚠ No configured players available."
    
    responses = []
    responses.append(f"📢 GAME MASTER: {broadcast_text}\n")
    responses.append("=" * 80)
    
    for player in configured_players:
        char_name = player.config.get('character_name', f'Player {player.player_id}')
        response, emotion = player.generate_response(broadcast_text, "stat_check")
        
        # Check if stat is mentioned
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        mentioned_stat = next((ability for ability in abilities if ability in response.lower()), None)
        
        stat_indicator = ""
        if mentioned_stat and "modifiers" in player.config:
            modifier = player.config["modifiers"].get(mentioned_stat, 0)
            stat_indicator = f" [🎲 {mentioned_stat.upper()} {modifier:+d}]"
        
        responses.append(f"\n🎭 {char_name}{stat_indicator}:")
        responses.append(response)
        responses.append("-" * 80)
    
    responses.append("\n💡 GM: Now resolve any stat checks with dice rolls and broadcast the results!")
    
    return "\n".join(responses)

def gm_resolution(resolution_text: str) -> str:
    """GM provides resolution after dice rolls"""
    if not resolution_text.strip():
        return "⚠ No resolution provided"
    
    session.add_log_entry(0, resolution_text, "gm_resolution", "neutral")
    
    return f"✓ GM Resolution broadcasted to all players:\n\n{resolution_text}\n\n" + \
           "Players can now respond to this resolution in the next round."

def extract_player_metadata(player_index: int) -> str:
    """Extract metadata for a specific player"""
    try:
        idx = int(player_index) - 1
        if idx < 0 or idx >= len(session.players):
            return f"❌ Invalid player number. Valid range: 1-{len(session.players)}"
        
        return session.players[idx].extract_metadata()
    except Exception as e:
        return f"❌ Error: {str(e)}"

def extract_environmental_metadata() -> str:
    """Extract updated environmental settings based on session events"""
    if not session.players:
        return json.dumps({
            "error": "No players in session. Cannot extract environmental data."
        }, indent=2)
    
    try:
        # Get a reference model from first configured player
        model = None
        for player in session.players:
            if player.config_loaded:
                model = player.model
                break
        
        if not model:
            return json.dumps({
                "error": "No configured players found."
            }, indent=2)
        
        # Build extraction prompt
        prompt = f"""Analyze this D&D session and update the environmental settings with what happened.

ORIGINAL ENVIRONMENTAL SETTINGS:
{json.dumps(session.environmental_settings, indent=2)}

FULL SESSION LOG (all events):
{json.dumps(session.global_log, indent=2)}

TASK: Create an UPDATED environmental settings JSON that includes:
1. All original settings (campaign_name, current_location, etc.)
2. Updated "recent_events" - add what happened this session
3. Updated "active_quests" - update status/progress
4. Updated "known_npcs" - add new NPCs met or update relationships
5. Updated "world_state" - reflect changes from session
6. NEW "session_summary" field with key developments
7. NEW "next_session_hooks" - unresolved situations for next time

Return ONLY valid JSON in this structure:
{{
  "campaign_name": "...",
  "current_arc": "...",
  "session_number": <increment by 1>,
  "current_location": "...",
  "time_of_day": "...",
  "active_quests": [...],
  "recent_events": [...include this session's events...],
  "known_npcs": [...],
  "world_state": {{...}},
  "session_summary": "What happened this session in 2-3 sentences",
  "next_session_hooks": ["Hook 1", "Hook 2", ...],
  "dm_notes": "Important info for next session"
}}

IMPORTANT: Return ONLY valid JSON. No markdown, no explanations, no backticks."""

        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # Clean up response
        if result.startswith("```json"):
            result = result.replace("```json", "").replace("```", "").strip()
        
        return result
    
    except Exception as e:
        return json.dumps({
            "error": f"Environmental extraction failed: {str(e)}",
            "original_settings": session.environmental_settings
        }, indent=2)

def get_session_summary() -> str:
    """Get summary of current session"""
    summary = []
    summary.append(f"📊 SESSION SUMMARY")
    summary.append(f"Players: {len(session.players)}")
    summary.append(f"Total Events: {len(session.global_log)}")
    summary.append(f"Mode: {session.reactive_mode.replace('_', ' ').title()}")
    
    if session.environmental_settings:
        campaign = session.environmental_settings.get('campaign_name', 'N/A')
        location = session.environmental_settings.get('current_location', 'N/A')
        summary.append(f"\nCampaign: {campaign}")
        summary.append(f"Current Location: {location}")
    
    summary.append("\n" + "=" * 60)
    summary.append("PLAYERS:")
    summary.append("=" * 60)
    
    for player in session.players:
        if not player.config_loaded:
            summary.append(f"\nPlayer {player.player_id}: Not configured")
            continue
            
        char_name = player.config.get('character_name', 'Unknown')
        char_class = player.config.get('character_class', 'Unknown')
        level = player.config.get('level', '?')
        gender = player.config.get('gender', 'N/A')
        emotion = player.current_emotion
        
        emotion_emoji = {
            "angry": "😠", "fearful": "😰", "joyful": "😊",
            "sad": "😢", "determined": "💪", "suspicious": "🤨",
            "curious": "🤔", "confident": "😎", "neutral": "😐"
        }
        emoji = emotion_emoji.get(emotion, "😐")
        
        has_metadata = "✓" if player.previous_session_metadata else "✗"
        
        summary.append(f"\n🎭 Player {player.player_id}: {char_name}")
        summary.append(f"   Class: {char_class} (Level {level}) | Gender: {gender}")
        summary.append(f"   Current Emotion: {emoji} {emotion.title()}")
        summary.append(f"   Previous Session Data: {has_metadata}")
        
        if "ability_scores" in player.config:
            summary.append(f"   Stats: {player.get_stats_display()}")
    
    return "\n".join(summary)

# ==============================
# Gradio Interface
# ==============================
def create_interface():
    with gr.Blocks(title="D&D Multi-Agent Bridge v3", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("""
        # 🎲 D&D Multi-Agent Bridge v3 - Reactive Edition
        ### Powered by Google Gemini | Features: Reactive Conversations, Stat Checks, Emotional Tracking
        
        New in v3: Characters have natural conversations with each other, attempt stat checks, and develop emotional arcs!
        """)
        
        # Session Info
        with gr.Row():
            session_info = gr.Textbox(
                label="📊 Session Info",
                value="No players created yet.",
                interactive=False,
                lines=12
            )
            refresh_btn = gr.Button("🔄 Refresh Info", size="sm")
        
        gr.Markdown("---")
        
        # Environmental Settings
        with gr.Accordion("🌍 Environmental Settings (Game Master)", open=False):
            gr.Markdown("""
            **Set the world state once - all characters will know about it.**
            Include: campaign, location, quests, NPCs, weather, recent events.
            """)
            
            env_config_input = gr.Code(
                label="Environmental Settings (JSON)",
                language="json",
                lines=12,
                value='''{
  "campaign_name": "The Lost Crown",
  "current_arc": "Investigation of the Abandoned Mill",
  "current_location": "Village of Thornhaven",
  "time_of_day": "Late afternoon, storm approaching",
  "active_quests": ["Clear the kobold infestation"],
  "recent_events": ["Villagers reported organized kobold attacks"]
}'''
            )
            load_env_btn = gr.Button("🌍 Load Environmental Settings")
            env_status = gr.Textbox(label="Status", interactive=False)
        
        load_env_btn.click(
            fn=load_environmental_settings,
            inputs=[env_config_input],
            outputs=[env_status]
        )
        
        gr.Markdown("---")
        
        # Player Management
        gr.Markdown("## 👥 Player Management")
        
        with gr.Row():
            model_selector = gr.Dropdown(
                choices=list(MODELS.keys()),
                value="pro3Flash",
                label="Model Selection"
            )
            add_player_btn = gr.Button("➕ Add New Player", variant="primary")
            system_msg = gr.Textbox(label="System Message", interactive=False)
        
        add_player_btn.click(
            fn=add_player,
            inputs=[model_selector],
            outputs=[system_msg]
        )
        
        refresh_btn.click(
            fn=get_session_summary,
            outputs=[session_info]
        )
        
        gr.Markdown("---")
        
        # Individual Player Interface
        gr.Markdown("## 🎭 Individual Player Control")
        
        player_num = gr.Number(
            label="Player Number",
            value=1,
            precision=0,
            minimum=1
        )
        
        # Configuration
        with gr.Accordion("⚙️ Player Configuration", open=True):
            gr.Markdown("""
            **IMPORTANT: Include ability scores and gender!**
            
            Required fields: character_name, gender, ability_scores, modifiers
            """)
            
            with gr.Row():
                config_input = gr.Code(
                    label="Character Configuration (JSON)",
                    language="json",
                    lines=12,
                    value='''{
  "character_name": "Thorin Oakenshield",
  "gender": "male",
  "character_class": "Fighter",
  "level": 5,
  "race": "Mountain Dwarf",
  "ability_scores": {
    "strength": 18,
    "dexterity": 12,
    "constitution": 16,
    "intelligence": 10,
    "wisdom": 13,
    "charisma": 14
  },
  "modifiers": {
    "strength": 4,
    "dexterity": 1,
    "constitution": 3,
    "intelligence": 0,
    "wisdom": 1,
    "charisma": 2
  },
  "personality": "Brave, proud, distrusts elves"
}'''
                )
                metadata_input = gr.Code(
                    label="Previous Session Metadata (Optional) - Paste extracted metadata here",
                    language="json",
                    lines=12,
                    value=""
                )
            
            load_config_btn = gr.Button("📥 Load Configuration")
            config_status = gr.Textbox(label="Configuration Status", interactive=False, lines=4)
        
        load_config_btn.click(
            fn=load_player_config,
            inputs=[player_num, config_input, metadata_input],
            outputs=[config_status]
        )
        
        # Individual Interaction
        gr.Markdown("### 💬 Individual Conversation")
        
        with gr.Row():
            listen_btn = gr.Button("🎤 Listen", variant="secondary")
            talk_btn = gr.Button("💬 Talk", variant="primary")
        
        input_textbox = gr.Textbox(
            label="Input",
            placeholder="Type or use voice...",
            lines=3
        )
        
        output_textbox = gr.Textbox(
            label="Character Response (with emotion tracking)",
            lines=6,
            interactive=False
        )
        
        audio_output = gr.Audio(
            label="🔊 Voice Output",
            type="filepath",
            autoplay=True
        )
        
        listen_btn.click(
            fn=player_listen,
            inputs=[player_num],
            outputs=[input_textbox]
        )
        
        talk_btn.click(
            fn=player_talk,
            inputs=[player_num, input_textbox],
            outputs=[output_textbox, audio_output]
        )
        
        gr.Markdown("---")
        
        # Reactive Broadcast Section
        gr.Markdown("## 🔄 Reactive Broadcast Modes")
        
        with gr.Tabs():
            # Free Discussion Tab
            with gr.TabItem("💬 Free Discussion"):
                gr.Markdown("""
                **Players have natural conversations with each other!**
                
                - Set number of rounds (recommended: 4)
                - Players react to each other naturally
                - Short, conversational responses
                - Auto-detects when stat checks are needed
                """)
                
                with gr.Row():
                    discussion_listen_btn = gr.Button("🎤 Listen")
                    discussion_rounds = gr.Slider(
                        minimum=2,
                        maximum=8,
                        value=4,
                        step=1,
                        label="Discussion Rounds"
                    )
                    discussion_send_btn = gr.Button("📣 Start Discussion", variant="primary")
                
                discussion_input = gr.Textbox(
                    label="GM Narrative / Scene Description",
                    placeholder="Describe the scene or situation...",
                    lines=3
                )
                
                discussion_output = gr.Textbox(
                    label="Reactive Discussion",
                    lines=20,
                    interactive=False
                )
                
                discussion_listen_btn.click(
                    fn=broadcast_to_all,
                    outputs=[discussion_input]
                )
                
                discussion_send_btn.click(
                    fn=process_reactive_discussion,
                    inputs=[discussion_input, discussion_rounds],
                    outputs=[discussion_output]
                )
            
            # Stat Check Tab
            with gr.TabItem("🎲 Stat Check Mode"):
                gr.Markdown("""
                **Players attempt ability checks!**
                
                - Players can state: "Using my Strength, I force the door"
                - System shows character's modifiers
                - GM rolls dice and enters result below
                """)
                
                with gr.Row():
                    stat_listen_btn = gr.Button("🎤 Listen")
                    stat_send_btn = gr.Button("🎲 Prompt for Stat Checks", variant="primary")
                
                stat_input = gr.Textbox(
                    label="GM Prompt (describe situation requiring checks)",
                    placeholder="You face a locked door. What do you do?",
                    lines=3
                )
                
                stat_output = gr.Textbox(
                    label="Player Actions (with stat modifiers shown)",
                    lines=15,
                    interactive=False
                )
                
                gr.Markdown("### 🎯 GM Resolution")
                gr.Markdown("After rolling dice, broadcast the results:")
                
                resolution_input = gr.Textbox(
                    label="GM Resolution",
                    placeholder="Example: 'Thorin rolled 14 + 4 (STR) = 18. The DC was 16. The door bursts open! What do you do now?'",
                    lines=4
                )
                
                resolution_btn = gr.Button("📢 Broadcast Resolution")
                resolution_output = gr.Textbox(label="Status", interactive=False)
                
                stat_listen_btn.click(
                    fn=broadcast_to_all,
                    outputs=[stat_input]
                )
                
                stat_send_btn.click(
                    fn=process_stat_check_broadcast,
                    inputs=[stat_input],
                    outputs=[stat_output]
                )
                
                resolution_btn.click(
                    fn=gm_resolution,
                    inputs=[resolution_input],
                    outputs=[resolution_output]
                )
        
        gr.Markdown("---")
        
        # Metadata Extraction
        gr.Markdown("## 📜 Session Metadata & Continuity")
        
        with gr.Row():
            metadata_player = gr.Number(
                label="Player Number",
                value=1,
                precision=0,
                minimum=1
            )
            extract_btn = gr.Button("📊 Extract Player Metadata", variant="secondary")
        
        metadata_output = gr.Code(
            label="Metadata (JSON) - Save for next session! Includes emotional journey and stat attempts",
            language="json",
            lines=15
        )
        
        extract_btn.click(
            fn=extract_player_metadata,
            inputs=[metadata_player],
            outputs=[metadata_output]
        )
        
        gr.Markdown("---")
        
        # Environmental Settings Update
        gr.Markdown("## 🌍 Extract Updated Environmental Settings")
        gr.Markdown("""
        **Extract session events and update environmental settings for next session!**
        
        This analyzes everything that happened and creates an updated environmental settings JSON with:
        - Updated recent_events (includes this session)
        - Updated quest progress
        - New NPCs encountered
        - Changed world state
        - Session summary
        - Hooks for next session
        
        **Use this at the END of each session**, then load it at the start of the next session!
        """)
        
        extract_env_btn = gr.Button("🌍 Extract Updated Environmental Settings", variant="primary", size="lg")
        
        env_metadata_output = gr.Code(
            label="Updated Environmental Settings (JSON) - Load this at start of next session!",
            language="json",
            lines=20
        )
        
        extract_env_btn.click(
            fn=extract_environmental_metadata,
            outputs=[env_metadata_output]
        )
        
        # Footer
        gr.Markdown("""
        ---
        ### 🎮 Quick Guide
        
        **💬 Free Discussion Mode**: Natural player conversations (4 rounds recommended)
        - Players react to each other, have back-and-forth dialogue
        - System detects when stat checks are needed
        
        **🎲 Stat Check Mode**: Players attempt ability-based actions
        - Characters say "Using my Strength..." or similar
        - GM rolls dice, enters: "Rolled 14, DC was 16"
        - GM broadcasts outcome
        
        **😊 Emotional Tracking**: Automatic throughout session
        - Emotions influence future responses naturally
        - Extracted in metadata for continuity
        
        **📊 Stats Display**: Always visible in session summary
        - Shows ability scores and modifiers
        - Referenced in stat check attempts
        
        **🌍 End of Session Workflow**:
        1. Extract metadata for EACH player → save individually
        2. Extract updated environmental settings → save as new file
        3. Next session: Load updated environmental settings FIRST
        4. Then load each player with their metadata
        
        This ensures perfect continuity between sessions!
        """)
    
    return demo

# ==============================
# Main Entry Point
# ==============================
if __name__ == "__main__":
    print("🎲 D&D Multi-Agent Bridge v3 - Reactive Edition")
    print(f"Voice Support: {'✓ Enabled' if VOICE_AVAILABLE else '⚠ Disabled'}")
    print(f"Default Model: {DEFAULT_MODEL}")
    print(f"✓ New Features: Reactive Conversations, Stat Checks, Emotional Tracking")
    
    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )
