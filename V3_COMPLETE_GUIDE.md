# 🎲 Complete Guide: D&D Bridge v3 - Reactive Edition

## 🌟 What's New in Version 3?

### 1. 🔄 **Reactive Conversations**
Players now have natural back-and-forth discussions with each other!
- Multiple rounds of conversation (2-8 rounds, 4 recommended)
- Players react to what others say
- Short, natural responses (not essays!)
- Auto-detects when GM intervention needed

### 2. 🎲 **Classical D&D Stat System**
Full ability score integration with checks!
- STR, DEX, CON, INT, WIS, CHA scores and modifiers
- Players can attempt stat-based actions
- GM rolls physical dice and broadcasts results
- Natural flow: attempt → roll → outcome → continue

### 3. 😊 **Emotional Tracking**
Characters develop emotional arcs throughout the session!
- Emotions tracked automatically after each response
- Influences future responses naturally
- Visible in real-time with emoji indicators
- Included in metadata extraction

### 4. 📊 **Stats Display**
Always see character capabilities!
- Ability scores shown in session summary
- Modifiers displayed during stat checks
- Skills and saving throws tracked
- Referenced naturally in roleplay

---

## 🎯 The Three Interaction Modes

### Mode 1: 💬 Free Discussion
**When to use:** Players talking to each other, planning, debating

**How it works:**
1. GM describes scene
2. Players have 4 rounds of conversation
3. Each player sees what others said
4. Natural back-and-forth emerges
5. Auto-stops when stat check detected

**Example:**
```
GM: "You stand before a locked door. What do you do?"

Round 1:
😎 Thorin: "I examine it for weaknesses."
🤔 Elara: "Let me check for magical wards first."

Round 2:
🤨 Thorin: "Well, wizard? Any magic?"
😊 Elara: "None! But the lock looks very complex."

Round 3:
💪 Thorin: "Using my Strength, I'll force it!"
[STAT CHECK DETECTED]
```

### Mode 2: 🎲 Stat Check Mode
**When to use:** Actions requiring ability checks

**The Flow:**
```
1. GM describes situation
   ↓
2. Players declare actions with stats
   "Using my 18 Strength, I force the door"
   ↓
3. System shows character's modifier
   [🎲 STR +4]
   ↓
4. GM rolls physical d20 → gets result
   ↓
5. GM enters complete result in resolution box:
   "Rolled 14 + 4 = 18. DC was 16. Door opens!"
   ↓
6. Flow continues naturally
```

**Key Point:** GM handles ALL math and dice logic!
- Initiative
- Advantage/disadvantage
- Situational modifiers
- Critical hits
- Just enter the final narrative result!

### Mode 3: 🎭 Individual Mode
**When to use:** Private conversations, detailed descriptions

**How it works:**
- Select specific player
- Full responses allowed
- Voice input/output with gender-appropriate voice
- For one-on-one GM interactions

---

## 📖 Complete Workflow

### Session Setup

#### 1. Launch
```bash
# Use the ultimate launcher
run_bridge_ultimate.bat

# Or manually
python dnd_bridge_v3.py
```

#### 2. Load Environmental Settings
```json
{
  "campaign_name": "The Shadow of Erebor",
  "current_location": "Thornhaven Village",
  "time_of_day": "Evening, storm approaching",
  "active_quests": ["Clear kobold infestation"],
  "recent_events": ["Party accepted contract"]
}
```

#### 3. Create & Configure Players

**Required fields now:**
- `character_name`
- `gender` (male/female/neutral)
- `ability_scores` (all 6 abilities)
- `modifiers` (calculated modifiers)

**Example minimal config:**
```json
{
  "character_name": "Thorin Oakenshield",
  "gender": "male",
  "character_class": "Fighter",
  "level": 5,
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
  }
}
```

---

## 🎮 Running a Session

### Opening Scene (Free Discussion)

**GM Input:**
```
"You approach the abandoned mill. Through broken windows, 
you see flickering torchlight. The storm rages around you. 
What do you do?"
```

**Set Rounds:** 4

**Result:**
```
📢 GAME MASTER: You approach the abandoned mill...

🔄 ROUND 1
--------------------
💪 Thorin: I grip my axe and approach cautiously, checking for guards.
🤔 Elara: I hang back and try to detect any magical auras in the building.

🔄 ROUND 2
--------------------
🤨 Thorin: Do you sense anything, wizard?
😊 Elara: Yes! Faint necromantic energy. Be careful!

🔄 ROUND 3
--------------------
😠 Thorin: Necromancy? In MY ancestral lands? We go in NOW!
😰 Elara: Wait! We should have a plan first!

🔄 ROUND 4
--------------------
💪 Thorin: The plan is simple - I charge in with my axe!
🤔 Elara: At least let me cast Mage Armor first...
```

Notice:
- ✅ Natural conversation flow
- ✅ Emotional reactions (emojis show current state)
- ✅ Players reference each other
- ✅ Conflict emerges naturally (Thorin wants to charge, Elara wants to plan)

### Stat Check Resolution

**Player declares in Free Discussion:**
```
💪 Thorin: "Using my Strength, I kick down the door!"
```

**System detects:** ⚠️ STAT CHECK DETECTED

**Switch to Stat Check Mode:**

**GM Prompt:**
```
"Thorin attempts to kick down the door. Roll Strength check!"
```

**System shows:**
```
🎭 Thorin [🎲 STR +4]:
"I take a running start and slam my boot into the door with all my might!"
```

**GM rolls physical d20:**
- Rolls: 10
- Adds modifier: +4
- Total: 14
- Compares to DC (16)
- Result: Failure

**GM Resolution Input:**
```
"Thorin rolled 10 + 4 (STR) = 14. The DC was 16. 
The door shudders but holds! Your foot stings from the impact. 
The noise echoes through the mill - anyone inside definitely heard that! 
What do you do?"
```

**System broadcasts to all players**

**Continue with Free Discussion:**
```
Round 1:
😤 Thorin: "Curse this door! Wizard, try your magic!"
😨 Elara: "They heard us - we've lost surprise! I'll try Knock spell..."
```

---

## 🎯 Handling Complex Situations

### Initiative / Combat

**When two players take conflicting actions:**

```
Round X:
💪 Thorin: "I charge the orc chieftain!"
🔥 Elara: "I cast Fireball at the orc chieftain!"
```

**GM handles initiative:**
1. Roll initiative for both
2. Determine order
3. Resolve in order

**GM Resolution:**
```
"Initiative: Elara (18) goes first, Thorin (12) second.

Elara's fireball explodes! The orc takes 28 damage but survives, 
badly burned. Thorin, you charge through the smoke - the orc is 
staggering, an easy target! What do you do?"
```

### Advantage/Disadvantage

**Player declares:**
```
💪 Thorin: "Using my Strength, I attack while he's distracted!"
```

**GM notes advantage (distracted enemy):**
- Rolls 2d20, takes higher
- Rolls: 8 and 15
- Uses 15 + 4 = 19
- Hits!

**GM Resolution:**
```
"Thorin rolled 19 (advantage from distraction). The orc's AC is 16 - 
you hit! Roll damage!"
```

**Thorin declares damage:**
```
💪 Thorin: "My axe bites deep! I roll... 12 damage!"
```

**GM:**
```
"Your axe cleaves through the orc's shoulder! He roars in pain 
and swings at you! Everyone, what do you do?"
```

### Multiple Checks

**Situation:** Picking a lock while guards patrol

```
🤔 Elara: "Using my Intelligence, I try to pick the lock quietly."

GM rolls:
- Sleight of Hand: 15 + 4 (DEX) = 19 → Success!
- Stealth: 8 + 2 (DEX) = 10 → Failure!

GM Resolution:
"You pick the lock successfully, but your tools clink loudly! 
A guard calls out: 'Who's there?' 
Everyone, what do you do?"
```

---

## 😊 Emotional Tracking in Action

### How It Works

**Automatic:** System tracks emotions based on:
- Keywords in responses
- Current situation context
- Previous emotional state

**Example Progression:**
```
Start of session:
😐 Thorin: neutral

After insult:
😠 Thorin: angry (detected "growl", "rage")

After victory:
😎 Thorin: confident (detected "pride", "bold")

After friend injured:
😢 Thorin: sad (detected "sorrow", "worry")

Next session:
💪 Thorin: determined (character development)
```

### Emotional Influence

**Emotions subtly affect future responses:**

**When Angry:**
```
GM: "The merchant offers a discount."
😠 Thorin: "I don't want your pity coins! Name a fair price or step aside!"
```

**When Joyful:**
```
GM: "The merchant offers a discount."  
😊 Thorin: "Ha! A fair merchant! Rare as dragon teeth! Done, friend!"
```

### Emotional Arcs

**Extracted in metadata:**
```json
{
  "emotional_journey": [
    "Started proud and confident",
    "Became suspicious after betrayal",
    "Turned angry when gold was stolen",
    "Ended determined to recover honor"
  ]
}
```

**Next session:** Character remembers this journey!

---

## 📊 Stats in Practice

### Reading the Display

**Session Summary shows:**
```
🎭 Player 1: Thorin Oakenshield
   Class: Fighter (Level 5) | Gender: male
   Current Emotion: 💪 determined
   Stats: STR: 18 (+4) | DEX: 12 (+1) | CON: 16 (+3)
          INT: 10 (+0) | WIS: 13 (+1) | CHA: 14 (+2)
```

### Natural Stat References

**Players will naturally use their strengths:**

**High STR character:**
```
💪 "Using my Strength, I..."
- Force doors
- Grapple enemies
- Intimidate through physicality
```

**High INT character:**
```
🤓 "Using my Intelligence, I..."
- Decipher ancient texts
- Remember lore
- Solve puzzles
```

**High CHA character:**
```
😎 "Using my Charisma, I..."
- Persuade guards
- Deceive enemies
- Lead the group
```

---

## 🎬 Example: Full Scene

### The Locked Treasury

**Setup: Free Discussion Mode, 4 rounds**

```
📢 GM: "You've fought your way to the dwarven treasury. 
A massive stone door blocks your path, covered in ancient runes. 
You hear footsteps echoing behind you - guards approaching! 
What do you do?"

🔄 ROUND 1
--------------------
😨 Thorin: "Those are MY family's runes! Let me examine them!"
🤔 Elara: "I'll check for magical locks while you do."

🔄 ROUND 2
--------------------
😤 Thorin: "These runes... they're a puzzle, not a lock! Give me a moment..."
😊 Elara: "No magical traps detected. But those footsteps are getting closer!"

🔄 ROUND 3
--------------------
💪 Thorin: "Using my Wisdom, I try to solve the rune puzzle!"
⚠️ STAT CHECK DETECTED
```

**Switch to Stat Check Mode:**

```
🎭 Thorin [🎲 WIS +1]:
"I trace my fingers over the runes, remembering my grandfather's teachings. 
The third rune from the top... it's the key!"
```

**GM rolls:** d20 = 16 + 1 = 17 (DC was 15)

**GM Resolution:**
```
"Thorin rolled 17 (WIS). Success! The runes glow blue and the massive door 
begins to grind open! But the guards round the corner - three of them, 
weapons drawn! You have seconds before they reach you. What do you do?"
```

**Back to Free Discussion, 3 rounds:**

```
🔄 ROUND 1
--------------------
😤 Thorin: "Elara, get inside! I'll hold them here!"
😰 Elara: "You can't fight three alone!"

🔄 ROUND 2
--------------------
💪 Thorin: "I'm a dwarf defending his ancestral treasury - watch me!"
🔥 Elara: "Fine! I'll cast Fireball at their feet to slow them down!"

🔄 ROUND 3
--------------------
😎 Thorin: "That's the spirit! Using my Strength, I ready my axe for their charge!"
💪 Elara: "Casting now!"
⚠️ STAT CHECK DETECTED - COMBAT INITIATIVE
```

**GM rolls initiative and resolves combat...**

---

## 💡 Pro Tips

### 1. Response Length Control

**Problem:** Players write too much

**Solution:** Use Reaction Mode!
- Free Discussion automatically limits to brief responses
- Prompts emphasize: "1-3 sentences maximum"
- "Quick gesture or statement"

### 2. Stat Check Timing

**When players spontaneously attempt checks in Free Discussion:**
- System auto-detects keywords
- Stops discussion
- Prompts for GM resolution

**When to prompt for checks:**
- Use Stat Check Mode when situation clearly requires rolls
- Example: "You see a cliff. How do you cross it?"

### 3. Emotional Realism

**Let emotions flow naturally:**
- Don't force them
- LLM expresses emotions naturally in roleplay
- Tracking is for continuity, not constraints

### 4. Round Management

**Recommended rounds:**
- Simple scenes: 2-3 rounds
- Complex discussions: 4-5 rounds
- Critical planning: 6-8 rounds

**Stop early if:**
- Natural conclusion reached
- Stat check needed
- Combat starts

### 5. Conflict Resolution

**When players disagree:**
- Let them talk it out in Free Discussion
- If deadlock, GM makes ruling
- If combat starts, roll initiative

---

## 🔧 Technical Notes

### Calculating Modifiers

**Formula:** (Ability Score - 10) / 2, round down

**Examples:**
- STR 18 → (18-10)/2 = +4
- DEX 8 → (8-10)/2 = -1
- INT 10 → (10-10)/2 = 0

**Quick Reference:**
```
Score: 8-9   → -1
Score: 10-11 → +0
Score: 12-13 → +1
Score: 14-15 → +2
Score: 16-17 → +3
Score: 18-19 → +4
Score: 20-21 → +5
```

### Metadata Structure

**Now includes:**
```json
{
  "character_id": 1,
  "emotional_journey": [...],
  "stat_checks_attempted": [
    {
      "ability": "strength",
      "action": "forced door",
      "success": false,
      "consequence": "Lost surprise, hurt foot"
    }
  ],
  "major_events": [...],
  "relationships": [...],
  "unresolved_threads": [...]
}
```

---

## 🚨 Common Mistakes

### ❌ DON'T: Micromanage conversations
```
GM: "Thorin, what do you say?"
[wait for response]
GM: "Elara, what do you say?"
[wait for response]
```

### ✅ DO: Let them talk naturally
```
GM: "You're at the tavern. Discuss your plan." 
[Free Discussion 4 rounds]
[Players naturally go back and forth]
```

### ❌ DON'T: Over-explain the system
```
GM: "Roll d20 and add your modifier which is calculated from..."
```

### ✅ DO: Keep it natural
```
GM: "Rolled 14, DC was 16. The door holds. What now?"
```

### ❌ DON'T: Ignore emotions
```
[Thorin just failed critical save, ally died]
Next scene: Thorin acts normal
```

### ✅ DO: Let emotions persist
```
[Thorin failed save, ally died]
Next scene: 😢 Thorin: "I should have saved him..."
[Emotion influences behavior naturally]
```

---

## 🎓 Advanced Techniques

### Group Checks

**Situation:** Party sneaking past guards

```
Each player rolls Stealth:
- Thorin (DEX+1): 8 → Failure
- Elara (DEX+2): 18 → Success

GM: "Elara moves silently, but Thorin's armor clinks. 
Guards turn toward the noise! What do you do?"
```

### Contested Checks

**Arm wrestling NPC:**

```
Thorin: "Using my Strength to out-wrestle him!"

GM rolls:
- Thorin: 16 + 4 (STR) = 20
- NPC: 12 + 2 (STR) = 14

GM: "Your dwarven might overwhelms him! He slams the table 
in frustration and buys you an ale!"
```

### Skill Challenges

**Multi-step problem:**

```
GM: "To cross the chasm, you need 3 successful checks:
1. Someone scouts the path (Perception/Investigation)
2. Someone secures rope (Athletics/Acrobatics)  
3. Someone encourages the scared NPC (Persuasion/Intimidation)"

Let players coordinate, roll, resolve each step!
```

---

## 🎯 Quick Reference

| Situation | Mode | Rounds | GM Action |
|-----------|------|--------|-----------|
| Planning | Free Discussion | 4 | Listen |
| Ability check | Stat Check | N/A | Roll & resolve |
| Combat start | Stat Check | N/A | Roll initiative |
| Private talk | Individual | N/A | Respond |
| Debate | Free Discussion | 6 | Let them argue |
| Quick reaction | Free Discussion | 2 | Fast-paced |

---

## 📚 Example Character Stats

### Fighter (STR-based)
```
STR: 18 (+4) - Primary combat stat
DEX: 12 (+1) - Initiative, AC
CON: 16 (+3) - HP, survivability
INT: 10 (+0) - Average
WIS: 13 (+1) - Perception
CHA: 14 (+2) - Leadership
```

### Wizard (INT-based)
```
STR: 8  (-1) - Weak physically
DEX: 14 (+2) - AC, initiative
CON: 12 (+1) - HP
INT: 18 (+4) - Spellcasting!
WIS: 13 (+1) - Insight
CHA: 10 (+0) - Average
```

### Rogue (DEX-based)
```
STR: 10 (+0) - Average
DEX: 18 (+4) - Stealth, AC, attacks!
CON: 14 (+2) - HP
INT: 13 (+1) - Investigation
WIS: 12 (+1) - Perception
CHA: 14 (+2) - Deception
```

---

**You're ready to run the most immersive D&D session ever!** 🎲⚔️🧙‍♂️

Natural conversations + Stat checks + Emotional arcs = EPIC GAMEPLAY!
