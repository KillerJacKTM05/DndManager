# 🎯 Complete Guide: Enhanced D&D Bridge v2

## 🆕 What's New in Version 2?

### 1. 🎭 Gender-Aware Voice Output
Characters now speak with appropriate voices based on their gender!

**How it works:**
- Add `"gender": "male"` or `"gender": "female"` to character config
- Male characters get deeper, Australian English voice
- Female characters get standard US English voice
- Neutral/unspecified gets UK English voice

### 2. 🌍 Environmental Settings (Game Master Mode)
Set the world state once, and all characters know about it!

**Perfect for:**
- Campaign/session setup
- Current location details
- Active quests
- Known NPCs
- Weather, time, atmosphere
- Recent global events

### 3. 🧠 Session Continuity & Metadata
Characters remember previous sessions perfectly!

**Two methods:**
- **Per-Character Memory**: Load metadata with character config (private knowledge)
- **Shared Knowledge**: Add events to Environmental Settings (everyone knows)

### 4. 🔧 Better Python Detection
Launcher now finds Python even in Anaconda environments!

### 5. 📚 Updated to New Google GenAI SDK
No more deprecation warnings - using the latest official API.

---

## 📖 Complete Workflow Guide

### Session 0: Initial Setup

#### Step 1: Install & Configure

```bash
# Install dependencies
pip install -r requirements.txt

# Uninstall old package if you have it
pip uninstall google-generativeai

# Install new package
pip install google-genai
```

#### Step 2: Set API Key
Edit `run_bridge_ultimate.bat` with your key, or:
```bash
set GOOGLE_API_KEY=your-key-here
```

#### Step 3: Launch
Double-click `run_bridge_ultimate.bat` or run:
```bash
python dnd_bridge.py
```

---

### Session 1: Starting a New Campaign

#### 1. Load Environmental Settings

Click "🌍 Environmental Settings" accordion and paste:

```json
{
  "campaign_name": "The Shadow of Erebor",
  "current_arc": "Journey Begins",
  "current_location": "The Prancing Pony Inn, Bree",
  "time_of_day": "Evening, fireplace crackling",
  "active_quests": ["Meet the mysterious wizard"],
  "world_state": {
    "threat_level": "Rumors of darkness in the East",
    "mood": "Uneasy peace"
  }
}
```

Click "🌍 Load Environmental Settings"

#### 2. Create Players

- Select model (e.g., "pro3Flash")
- Click "➕ Add New Player" 
- Repeat for each character
- Click "🔄 Refresh Info" to verify

#### 3. Configure Each Player

For each player:
1. Set "Player Number"
2. Expand "⚙️ Player Configuration"
3. Paste character JSON (see examples below)
4. **IMPORTANT:** Include `"gender"` field!
5. Click "📥 Load Configuration"

**Example Character Config:**
```json
{
  "character_name": "Thorin Oakenshield",
  "gender": "male",
  "character_class": "Fighter",
  "race": "Dwarf",
  "personality": "Proud, brave, distrusts elves",
  "voice_style": "Gruff and commanding",
  "current_goals": ["Reclaim Erebor"],
  "inventory": ["Ancestral war axe", "Family shield"]
}
```

#### 4. Run the Session!

**Broadcast to all players:**
- Use "📢 Broadcast" section
- Click "🎤 Listen for Broadcast" or type narrative
- Click "📣 Send to All Players"
- All characters respond based on their personality!

**Individual interactions:**
- Select player number
- Type input or "🎤 Listen"
- Click "💬 Talk"
- Character responds (with gender-appropriate voice!)

---

### Between Sessions: Extract & Save Metadata

#### 1. Extract Metadata

For each player:
1. Enter player number
2. Click "📊 Extract Player Metadata"
3. Copy the JSON output
4. Save as `thorin_session1_metadata.json`

**Example extracted metadata:**
```json
{
  "character_id": 1,
  "character_name": "Thorin Oakenshield",
  "major_events": [
    "Accepted quest to clear kobolds",
    "Refused upfront payment",
    "Suspected darker forces at work"
  ],
  "emotional_journey": [
    "Initial pride",
    "Growing suspicion",
    "Resolute leadership"
  ],
  "inventory_changes": [
    {"item": "Gold pouch", "action": "Refused"}
  ],
  "relationships": [
    {
      "character": "Scarred merchant",
      "status": "Hostile",
      "details": "Threatened him if he lied"
    }
  ],
  "unresolved_threads": [
    "Identity of darker hand behind kobolds",
    "What kobolds are excavating"
  ]
}
```

#### 2. Update Environmental Settings

Add major events to your environmental JSON:

```json
{
  "campaign_name": "The Shadow of Erebor",
  "session_number": 2,
  "recent_events": [
    "Thorin refused upfront payment",
    "Party accepted contract",
    "Storm broke as party departed"
  ],
  "mysteries_and_hooks": [
    "What is the darker hand behind the kobolds?",
    "What are they excavating?"
  ]
}
```

---

### Session 2+: Continuing the Campaign

You have **two options** for continuity:

#### Option A: Per-Character Metadata (Private Memory)

Each character remembers their own experience:

1. Load Environmental Settings (shared world state)
2. Create players
3. For each player:
   - Paste character config in left box
   - Paste their metadata in right box
   - Click "📥 Load Configuration"

**Result:** Character has private memories + knows shared world state

#### Option B: Shared Knowledge Only

Everyone knows the same history:

1. Update Environmental Settings to include past events
2. Create players
3. Load character configs (without individual metadata)

**Result:** All characters know the same history

#### Option C: Hybrid (Recommended!)

Best of both worlds:

1. Load Environmental Settings with major public events
2. Load each character's config with their personal metadata
3. Characters know both public events AND private experiences

**Example:**
- **Environmental Settings**: "Village was attacked, kobolds defeated"
- **Thorin's Metadata**: "Thorin personally slew the kobold leader, claimed his axe"
- **Elara's Metadata**: "Elara detected ancient magic in the ruins"

Result: Both know about the attack, but each has unique memories!

---

## 🎯 Best Practices

### Gender Configuration

Always specify gender for proper voice:

```json
{
  "gender": "male",     // Australian accent (deeper)
  "gender": "female",   // US accent (lighter)  
  "gender": "neutral"   // UK accent (neutral)
}
```

### Environmental Settings Structure

```json
{
  // REQUIRED
  "campaign_name": "string",
  "current_location": "string",
  
  // RECOMMENDED
  "current_arc": "string",
  "session_number": 0,
  "time_of_day": "string",
  "weather": "string",
  "active_quests": [],
  "recent_events": [],
  "known_npcs": [],
  "world_state": {},
  "mysteries_and_hooks": []
}
```

### Metadata Management

**After each session:**
1. Extract metadata for ALL players
2. Save with descriptive names: `character_sessionX_metadata.json`
3. Update master environmental settings file
4. Back up everything!

**Next session:**
- Option 1: Load individual metadata (detailed continuity)
- Option 2: Merge key events into environmental settings (lighter)

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'google'"

**Solution:**
```bash
pip uninstall google-generativeai
pip install google-genai
```

### Batch File Can't Find Python (Anaconda Users)

**Solution 1:** Use the ultimate launcher
- It detects Anaconda automatically

**Solution 2:** Open Anaconda Prompt
```bash
cd D:\dndBridge
python dnd_bridge.py
```

**Solution 3:** Edit batch file paths
Find your Python location:
```bash
where python
```

Update batch file:
```batch
set PYTHON_CMD="C:\Users\YourName\anaconda3\python.exe"
```

### Character Has Wrong Voice Gender

**Check your config:**
```json
{
  "gender": "male"  // Make sure this matches character!
}
```

If not specified, defaults to female voice.

### Characters Don't Remember Previous Session

**Check:**
1. Did you extract metadata last session?
2. Did you paste it in the "Previous Session Metadata" box?
3. Did you click "Load Configuration" AFTER pasting both boxes?

### Environmental Settings Not Working

**Verify:**
1. Load environmental settings BEFORE creating players
2. Click "Load Environmental Settings" button
3. Check "Session Info" shows the settings

---

## 📊 Example: Full Session Flow

### Pre-Session
```
1. Open run_bridge_ultimate.bat
2. Load environmental_settings_session2.json
3. Create 2 players
4. Load Thorin config + session1 metadata
5. Load Elara config + session1 metadata
6. Click "Refresh Info" - verify both loaded
```

### During Session
```
Narrator (Broadcast):
"You approach the abandoned mill. The storm rages. 
Through the rain, you see flickering torchlight..."

Thorin (Individual):
"What does your axe sense?"

Elara (Individual):
"Do you detect any magic?"
```

### Post-Session
```
1. Extract metadata for Thorin → save
2. Extract metadata for Elara → save
3. Update environmental settings with:
   - Mill was explored
   - Discovered kobold excavation
   - Found strange runes
4. Save everything for next session
```

---

## 🎮 Pro Tips

1. **Gender matters!** Always specify for immersion
2. **Start broad:** Load environmental settings first
3. **Layer history:** Use both shared settings + individual metadata
4. **Extract often:** Get metadata after every session
5. **Backup metadata:** These are your campaign memory!
6. **NPCs in settings:** Put NPC info in environmental settings so all players know them
7. **Secrets in metadata:** Put character secrets in individual metadata
8. **Update settings:** Add session results to environmental settings for next time

---

## 📁 File Organization

Recommended structure:
```
dndBridge/
├── dnd_bridge.py
├── requirements.txt
├── run_bridge_ultimate.bat
│
├── configs/
│   ├── thorin_base.json
│   ├── elara_base.json
│   └── environmental_base.json
│
├── sessions/
│   ├── session1/
│   │   ├── thorin_metadata.json
│   │   ├── elara_metadata.json
│   │   └── environmental_session1.json
│   │
│   └── session2/
│       ├── thorin_metadata.json
│       ├── elara_metadata.json
│       └── environmental_session2.json
```

---

## 🚀 Quick Reference Card

| Action | Steps |
|--------|-------|
| **New Campaign** | 1. Load env settings<br>2. Create players<br>3. Load character configs |
| **Continue Campaign** | 1. Load env settings<br>2. Create players<br>3. Load configs + metadata |
| **Narrate Scene** | Use Broadcast → type/speak → send |
| **Individual Action** | Select player → type/speak → talk |
| **End Session** | Extract metadata for each player → save |
| **Wrong Voice** | Add `"gender": "male/female/neutral"` to config |

---

**Happy adventuring with perfect memory and appropriate voices!** 🎲⚔️🧙‍♂️
