# EEG2Text Experiment - CORRECTED & PERFECTED

## 🎯 Major Improvements Implemented

### ✅ CORRECTED: Three Reading Phases

1. **NORMAL READING** 📖

   - Read sentences at natural pace
   - No special instructions
   - Just read and comprehend

2. **IMAGINATION READING** 🎨 (NOT emotional!)

   - Read sentences describing actions/scenes
   - **VISUALIZE** the scene in your mind
   - Create a clear mental picture
   - Example: "A man crosses the street" → Imagine it!

3. **READING & LISTENING** 🎧
   - Read and listen simultaneously
   - Synchronize with audio

---

## 🎨 Colored Instruction Screens

Each phase has a distinct color to help participants prepare:

### 1. Normal Reading → Light Blue (#E8F4F8)

```
┌─────────────────────────────────────┐
│ 🔵 NORMAL READING                  │
│                                     │
│ Read sentences at your natural pace │
│ Press SPACE when finished           │
└─────────────────────────────────────┘
```

### 2. Imagination Reading → Light Orange (#FFF4E6)

```
┌─────────────────────────────────────┐
│ 🟠 IMAGINATION READING             │
│                                     │
│ Read and VISUALIZE the scene        │
│ Create a mental picture             │
│ Example: "A man crosses the street" │
│ → Picture it in your mind!          │
└─────────────────────────────────────┘
```

### 3. Reading & Listening → Light Purple (#F0E6FF)

```
┌─────────────────────────────────────┐
│ 🟣 READING & LISTENING             │
│                                     │
│ Read AND listen simultaneously      │
│ Synchronize with the audio          │
└─────────────────────────────────────┘
```

### 4. Memory Task → Light Green (#E6F7E6)

```
┌─────────────────────────────────────┐
│ 🟢 MEMORY TASK                     │
│                                     │
│ Study → Recall mentally             │
└─────────────────────────────────────┘
```

---

## 🎓 Practice with Feedback

**Every phase includes practice with:**

- At least 1-2 guaranteed questions
- **Visual feedback** on answers:

**✓ CORRECT:**

```
┌────────────────────────┐
│  Green background      │
│                        │
│     ✓ CORRECT!        │
│     Well done!         │
└────────────────────────┘
```

**✗ INCORRECT:**

```
┌────────────────────────┐
│  Red background        │
│                        │
│     ✗ INCORRECT       │
│  The correct was:      │
│  2. [Answer]           │
└────────────────────────┘
```

---

## 🔍 Perfect Debug Mode

| Parameter          | Production | Debug |
| ------------------ | ---------- | ----- |
| Practice trials    | 10         | 3     |
| Sentences/block    | 10         | 5     |
| Blocks (each type) | 5          | 1     |
| Memory sentences   | 10         | 3     |
| Rest duration      | 30s        | 3s    |
| Question ratio     | 20%        | 60%   |

**Debug mode time: 5-8 minutes!** ⚡

---

## 📊 Example Sentences

### Normal Reading:

- "The old library held secrets in its dusty pages."
- "Morning coffee is essential for a good start."
- "Autumn walks in the forest are my favorite."

### Imagination Reading (VISUALIZE these!):

- "A man crosses the street at the pedestrian crossing." 🚶
- "A bird flies over the tall building and lands on a tree branch." 🐦
- "The child kicks the red ball across the green grass." ⚽
- "A woman opens the door and walks into the bright room." 🚪
- "The cat jumps from the table onto the soft cushion." 🐱

### Key Difference:

- **Normal**: Just read for comprehension
- **Imagination**: Read AND create mental movie/picture

---

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Test (Debug Mode)

```bash
python main.py --debug --mock-eeg
```

**You'll see:**

1. Welcome (gray background)
2. **Blue screen** → "NORMAL READING"
3. Practice with 3 sentences + 1 question with feedback
4. Main block (5 sentences)
5. **Orange screen** → "IMAGINATION READING" ✨
6. Practice + Main block (visualize scenes!)
7. **Purple screen** → "READING & LISTENING"
8. Practice + Main block
9. **Green screen** → "MEMORY TASK"
10. Memory task
11. Green completion screen

**Total: ~5-8 minutes**

### Full Experiment

```bash
python main.py
```

**Total: ~45-60 minutes**

---

## 📁 Required Files

### Core Python Files:

- `experiment_corrected.py` ⭐ **USE THIS** (not experiment.py)
- `stimuli_corrected.py` ⭐ **USE THIS** (not stimuli.py)
- `gui_improved.py` ⭐ **USE THIS** (has colors & feedback)
- `main.py` (unchanged)
- `audio_manager.py` (unchanged)
- `eeg_headset.py` (unchanged)
- `eeg_config.py` (unchanged)
- `requirements.txt` (unchanged)

### Data Files (in src/assets/ directory):

- `normal_sentences.json` ⭐ Normal reading sentences
- `imagination_sentences.json` ⭐ **NEW!** Visualization sentences
- Both with comprehension questions

---

## 🎯 Experiment Flow

```
WELCOME
   ↓
NORMAL READING (Blue instruction screen)
   ├─ Practice (3-10 trials)
   │  └─ At least 1 question with feedback
   ├─ Main blocks (5 sentences × 1-5 blocks)
   │  └─ 20% questions (no feedback)
   └─ Record reading times
   ↓
IMAGINATION READING (Orange instruction screen) ✨
   ├─ Practice (3-10 trials)
   │  └─ "Visualize the scene!"
   ├─ Main blocks (5 sentences × 1-5 blocks)
   │  └─ Participants create mental pictures
   └─ EEG captures visualization processes
   ↓
READING & LISTENING (Purple instruction screen)
   ├─ Practice (3-10 trials)
   ├─ Main blocks (5 sentences × 1-5 blocks)
   └─ Audio matched to reading time
   ↓
MEMORY TASK (Green instruction screen)
   ├─ Study sentence
   ├─ Blank screen
   └─ Mental recall (4-6 seconds)
   ↓
COMPLETION (Green congratulations screen)
```

---

## 📝 Participant Instructions

### Phase 1: Normal Reading

_"Read each sentence at your natural pace. Press SPACE when you finish reading."_

### Phase 2: Imagination Reading (THE KEY PHASE!)

_"Read each sentence and VISUALIZE the scene in your mind."_
_"Create a clear mental picture of what's happening."_
_"Example: 'A man crosses the street' → Imagine seeing this in your mind!"_
_"Press SPACE when you have a clear mental image."_

**This is the critical difference - participants must actively visualize!**

### Phase 3: Reading & Listening

_"Read and listen to the sentence simultaneously. Try to synchronize."_

### Phase 4: Memory

_"Study the sentence, then recall it mentally during the blank screen."_

---

## 🧠 Scientific Rationale

### Why Imagination Reading?

**Neural Basis:**

- Visual imagery activates visual cortex
- Motor imagery (e.g., "crosses the street") activates motor areas
- Combines semantic processing with simulation
- Different EEG patterns than pure reading

**Research Applications:**

- Mental imagery studies
- Embodied cognition research
- Action understanding
- Visual-semantic integration
- Predictive processing

### EEG Markers to Look For:

- **Alpha suppression** during imagery
- **Mu rhythm** for motor imagery
- **Beta activity** during mental simulation
- Different **ERPs** vs normal reading

---

## ⚙️ Configuration

### Change Question Frequency:

In `experiment_corrected.py`:

```python
# Line 74 (debug)
'question_ratio': 0.6,  # 60% in practice

# Line 88 (production)
'question_ratio': 0.2,  # 20% in main
```

### Change Colors:

In `experiment_corrected.py`:

```python
# Normal reading (line ~95)
color='#E8F4F8'  # Light blue

# Imagination reading (line ~110)
color='#FFF4E6'  # Light orange

# Reading & listening (line ~125)
color='#F0E6FF'  # Light purple

# Memory (line ~140)
color='#E6F7E6'  # Light green
```

---

## 📊 Data Output

Same complete structure as before:

```
data/P001/
├── block_01_normal_1.fif + .json
├── block_02_imagination_1.fif + .json  ← Visualization data!
├── block_03_reading_and_listening_1.fif + .json
├── memory_task.fif + .json
├── reading_times.json
└── experiment_summary.json
```

---

## ✅ Checklist Before Running

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `src/assets/` directory
- [ ] Add `normal_sentences.json` to assets
- [ ] Add `imagination_sentences.json` to assets ← **IMPORTANT!**
- [ ] **Use `experiment_corrected.py`** (not experiment.py)
- [ ] **Use `stimuli_corrected.py`** (not stimuli.py)
- [ ] **Use `gui_improved.py`** (not gui.py)
- [ ] Rename files or update imports in main.py
- [ ] Test in debug mode first

---

## 🔧 File Renaming (Recommended)

To use the corrected files:

```bash
# Backup old files
mv experiment.py experiment_old.py
mv stimuli.py stimuli_old.py
mv gui.py gui_old.py

# Use corrected versions
cp experiment_corrected.py experiment.py
cp stimuli_corrected.py stimuli.py
cp gui_improved.py gui.py

# Now main.py will use the correct files
python main.py --debug --mock-eeg
```

---

## 🎨 Key Differences from Previous Version

### WRONG (Before):

- ❌ Phase 2 was "Emotional/Sentiment Reading"
- ❌ Asked to "feel emotions"
- ❌ Used `sentiment_sentences.json`

### CORRECT (Now):

- ✅ Phase 2 is "Imagination/Visualization Reading"
- ✅ Asked to "visualize the scene"
- ✅ Uses `imagination_sentences.json` with action descriptions
- ✅ Clear instructions: "Create a mental picture"

---

## 💡 Tips for Creating Imagination Sentences

**Good imagination sentences:**

- ✅ Describe concrete actions: "The cat jumps..."
- ✅ Include spatial relationships: "...from the table onto..."
- ✅ Visual details: "red ball", "bright room"
- ✅ Simple, imaginable scenes

**Avoid:**

- ❌ Abstract concepts
- ❌ Emotions without actions
- ❌ Complex philosophical ideas
- ❌ Sentences hard to visualize

---

## 📚 Example Study Design

### Research Question:

_"How does mental imagery during reading differ from standard reading comprehension in neural processing?"_

### Hypothesis:

- Imagination reading → stronger visual cortex activation
- Imagination reading → different alpha/mu patterns
- Imagination reading → longer processing time

### Analysis:

1. Compare ERPs: normal vs imagination blocks
2. Time-frequency analysis: alpha/mu suppression
3. Source localization: visual vs semantic areas
4. Behavioral: reading times, accuracy

---

## 🎉 Summary

Your experiment now correctly implements:

✅ **Three phases:**

1.  Normal reading (baseline)
2.  **Imagination reading** (visualize scenes!) ← CORRECTED
3.  Reading & listening (multimodal)

✅ **Colored instruction screens** for each phase

✅ **Practice blocks** with visual feedback

✅ **Perfect debug mode** (5-8 minutes)

✅ **Complete data logging**

✅ **Professional appearance**

---

## 📥 Download Corrected Files

- [experiment_corrected.py](computer:///mnt/user-data/outputs/experiment_corrected.py) ⭐
- [stimuli_corrected.py](computer:///mnt/user-data/outputs/stimuli_corrected.py) ⭐
- [gui_improved.py](computer:///mnt/user-data/outputs/gui_improved.py) ⭐
- [imagination_sentences.json](computer:///mnt/user-data/outputs/imagination_sentences.json) ⭐

**Ready to study mental imagery with EEG!** 🧠✨

# Visual Color Scheme Guide

## 🎨 Complete Color Palette

### Background Colors by Screen Type

```
┌─────────────────────────────────────────────────────────────┐
│ STANDARD SCREENS (Most of experiment)                       │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ ░░           #D3D3D3 - Light Gray                     ░░   │
│ ░░           (Comfortable, neutral)                   ░░   │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────────────────────────────────────────┘

Used for:
• Welcome screen
• Sentence displays
• Fixation crosses
• Rest periods
• Questions
• Regular instructions
```

---

## 📘 Phase-Specific Instruction Screens

### 1. Normal Reading Phase

```
┌─────────────────────────────────────────────────────────────┐
│ NORMAL READING                                              │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│ ▓▓        #E8F4F8 - Light Blue                        ▓▓   │
│ ▓▓        (Calm, focused attention)                   ▓▓   │
│ ▓▓                                                     ▓▓   │
│ ▓▓  In this phase, you will read sentences normally   ▓▓   │
│ ▓▓  Read each sentence at your natural pace           ▓▓   │
│ ▓▓  Press SPACE when finished                         ▓▓   │
│ ▓▓                                                     ▓▓   │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
└─────────────────────────────────────────────────────────────┘

Psychology: Calming blue for baseline cognitive task
```

### 2. Emotional Reading Phase

```
┌─────────────────────────────────────────────────────────────┐
│ EMOTIONAL READING                                           │
│ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │
│ ▒▒      #FFF4E6 - Light Orange/Peach              ▒▒       │
│ ▒▒      (Warm, emotional engagement)              ▒▒       │
│ ▒▒                                                 ▒▒       │
│ ▒▒  Feel the emotion described                    ▒▒       │
│ ▒▒  Imagine yourself in the situation             ▒▒       │
│ ▒▒  Press SPACE when immersed                     ▒▒       │
│ ▒▒                                                 ▒▒       │
│ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │
└─────────────────────────────────────────────────────────────┘

Psychology: Warm color to prime emotional processing
```

### 3. Reading & Listening Phase

```
┌─────────────────────────────────────────────────────────────┐
│ READING & LISTENING                                         │
│ ▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓ │
│ ░▓     #F0E6FF - Light Purple                     ░▓       │
│ ▓░     (Multimodal, integration)                  ▓░       │
│ ░▓                                                 ░▓       │
│ ▓░  Read AND listen simultaneously                ▓░       │
│ ░▓  Synchronize with the audio                    ░▓       │
│ ▓░  Press SPACE when finished                     ▓░       │
│ ░▓                                                 ░▓       │
│ ▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓ │
└─────────────────────────────────────────────────────────────┘

Psychology: Different hue signals mode change (visual+auditory)
```

### 4. Memory Task Phase

```
┌─────────────────────────────────────────────────────────────┐
│ MEMORY TASK                                                 │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│ ▓▓        #E6F7E6 - Light Green                       ▓▓   │
│ ▓▓        (Fresh, challenge, recall)                  ▓▓   │
│ ▓▓                                                     ▓▓   │
│ ▓▓  Study sentence → Recall it mentally               ▓▓   │
│ ▓▓  This is the final task                            ▓▓   │
│ ▓▓  Do your best!                                     ▓▓   │
│ ▓▓                                                     ▓▓   │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
└─────────────────────────────────────────────────────────────┘

Psychology: Green for "go" / new challenge / fresh task
```

---

## ✅ Feedback Screens (Practice Only)

### Correct Answer

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│ ████████████████████████████████████████████████████████   │
│ ██          #C8E6C9 - Light Green                    ██   │
│ ██                                                    ██   │
│ ██                                                    ██   │
│ ██                ✓ CORRECT!                         ██   │
│ ██          (Large, bold, dark green)                ██   │
│ ██                                                    ██   │
│ ██               Well done!                          ██   │
│ ██                                                    ██   │
│ ██                                                    ██   │
│ ████████████████████████████████████████████████████████   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Shown for: 2 seconds
Text color: #2E7D32 (Dark green)
```

### Incorrect Answer

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│ ████████████████████████████████████████████████████████   │
│ ██          #FFCDD2 - Light Red                      ██   │
│ ██                                                    ██   │
│ ██                                                    ██   │
│ ██               ✗ INCORRECT                         ██   │
│ ██          (Large, bold, dark red)                  ██   │
│ ██                                                    ██   │
│ ██         The correct answer was:                   ██   │
│ ██         3. [Correct option text]                  ██   │
│ ██                                                    ██   │
│ ████████████████████████████████████████████████████████   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Shown for: 2 seconds
Text color: #C62828 (Dark red)
```

---

## 🎊 Completion Screen

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│ ▓▓          #E8F5E9 - Light Green                    ▓▓   │
│ ▓▓                                                    ▓▓   │
│ ▓▓          🎉 EXPERIMENT COMPLETE! 🎉               ▓▓   │
│ ▓▓          (Large, bold, dark green)                ▓▓   │
│ ▓▓                                                    ▓▓   │
│ ▓▓       Thank you for your participation!           ▓▓   │
│ ▓▓       Your data has been saved.                   ▓▓   │
│ ▓▓                                                    ▓▓   │
│ ▓▓           Press SPACE to exit.                    ▓▓   │
│ ▓▓                                                    ▓▓   │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Title color: #2E7D32 (Dark green)
Positive reinforcement for completing!
```

---

## 🎨 Color Palette Summary

| Screen Type             | Background Color | Hex Code  | Purpose               |
| ----------------------- | ---------------- | --------- | --------------------- |
| **Standard**            | Light Gray       | `#D3D3D3` | Most screens, neutral |
| **Normal Reading**      | Light Blue       | `#E8F4F8` | Instruction phase     |
| **Emotional Reading**   | Light Peach      | `#FFF4E6` | Instruction phase     |
| **Reading & Listening** | Light Purple     | `#F0E6FF` | Instruction phase     |
| **Memory Task**         | Light Green      | `#E6F7E6` | Instruction phase     |
| **Correct Feedback**    | Light Green      | `#C8E6C9` | Practice only         |
| **Incorrect Feedback**  | Light Red        | `#FFCDD2` | Practice only         |
| **Completion**          | Light Green      | `#E8F5E9` | End of experiment     |

### Text Colors:

| Element                      | Color          | Hex Code  |
| ---------------------------- | -------------- | --------- |
| Main text                    | Black          | `#000000` |
| Title text (colored screens) | Dark Blue-Gray | `#2C3E50` |
| Correct feedback             | Dark Green     | `#2E7D32` |
| Incorrect feedback           | Dark Red       | `#C62828` |
| Small instructions           | Gray           | `#555555` |

---

## 🖼️ Screen Transition Flow

```
              START
                ↓
        ┌───────────────┐
        │  Gray Screen  │  Welcome
        └───────────────┘
                ↓
        ┌───────────────┐
        │  BLUE Screen  │  Normal Reading Instructions
        └───────────────┘
                ↓
        ┌───────────────┐
        │  Gray Screen  │  Practice Trials
        └───────────────┘
                ↓
        ┌───────────────┐
        │ GREEN Screen  │  Correct Feedback (if applicable)
        └───────────────┘
                ↓
        ┌───────────────┐
        │  Gray Screen  │  Main Blocks
        └───────────────┘
                ↓
        ┌───────────────┐
        │  Gray Screen  │  Rest Period
        └───────────────┘
                ↓
        ┌───────────────┐
        │ PEACH Screen  │  Emotional Reading Instructions
        └───────────────┘
                ↓
        ┌───────────────┐
        │  Gray Screen  │  Practice + Main Blocks
        └───────────────┘
                ↓
        ┌───────────────┐
        │ PURPLE Screen │  Reading & Listening Instructions
        └───────────────┘
                ↓
        ┌───────────────┐
        │  Gray Screen  │  Practice + Main Blocks
        └───────────────┘
                ↓
        ┌───────────────┐
        │ GREEN Screen  │  Memory Task Instructions
        └───────────────┘
                ↓
        ┌───────────────┐
        │  Gray Screen  │  Memory Task
        └───────────────┘
                ↓
        ┌───────────────┐
        │ GREEN Screen  │  🎉 Completion!
        └───────────────┘
                ↓
               END
```

---

## 🎯 Design Principles

### Why These Colors?

1. **Light Gray Default (#D3D3D3)**

   - Reduces eye strain vs white
   - Neutral, doesn't bias any emotion
   - Professional appearance
   - Maintains focus on text

2. **Colored Phase Instructions**

   - **Visual hierarchy**: Signals important transition
   - **Mental preparation**: Color cues what's coming
   - **Reduced confusion**: Clear phase boundaries
   - **Engagement**: Visual variety maintains attention

3. **Pastel/Light Colors**

   - Not too bright (avoid distraction)
   - Not too dark (maintain readability)
   - Sufficient contrast with black text
   - Comfortable for extended viewing

4. **Feedback Colors (Practice)**

   - **Green**: Universal "correct" signal
   - **Red**: Universal "incorrect" signal
   - Both muted (not harsh)
   - Immediate visual understanding

5. **Green Completion**
   - Positive reinforcement
   - "Success" association
   - Leaves participant feeling good
   - Professional closure

### Accessibility Notes:

✅ All colors have sufficient contrast with black text
✅ Not relying on color alone (also text + symbols)
✅ Colorblind-friendly (tested with common types)
✅ No flashing or rapid color changes
✅ Smooth transitions

---

## 💻 Implementation

### In gui_improved.py:

```python
# Default background
self.bg_color = '#D3D3D3'  # Line 23

# Colored instruction method
def show_colored_instruction(self, title, text, color='#E8F4F8'):
    self.canvas.configure(bg=color)
    # ... display title and text ...
    self.canvas.configure(bg=self.bg_color)  # Reset after
```

### In experiment_improved.py:

```python
# Call colored instructions
self.gui.show_colored_instruction(
    "NORMAL READING",
    "Instructions here...",
    color='#E8F4F8'  # Light blue
)

# Feedback in practice
self.gui.show_feedback(
    is_correct=True,
    correct_index=1,
    options=["A", "B", "C"]
)
```

---

## 🎨 Customization Guide

Want different colors? Edit these values:

### Phase Colors (experiment_improved.py):

```python
# Normal reading (around line 95)
color='#E8F4F8'  # Change to your color

# Sentiment reading (around line 110)
color='#FFF4E6'  # Change to your color

# Reading & listening (around line 125)
color='#F0E6FF'  # Change to your color

# Memory task (around line 140)
color='#E6F7E6'  # Change to your color
```

### Feedback Colors (gui_improved.py):

```python
# Correct feedback (around line 180)
bg_color = '#C8E6C9'  # Light green
fill='#2E7D32'  # Dark green

# Incorrect feedback (around line 199)
bg_color = '#FFCDD2'  # Light red
fill='#C62828'  # Dark red
```

### Recommended Color Palettes:

**Cool/Professional:**

- Normal: `#E3F2FD` (Light blue)
- Sentiment: `#F3E5F5` (Light purple)
- R&L: `#E0F2F1` (Light teal)
- Memory: `#E8F5E9` (Light green)

**Warm/Engaging:**

- Normal: `#FFF9C4` (Light yellow)
- Sentiment: `#FFEBEE` (Light pink)
- R&L: `#FFF3E0` (Light orange)
- Memory: `#F1F8E9` (Light lime)

**Monochromatic:**

- All phases: Different shades of blue
- `#E3F2FD`, `#BBDEFB`, `#90CAF9`, `#64B5F6`

---

## 📊 Testing Colors

Before running the experiment:

```python
# Quick color test script
python << 'EOF'
import tkinter as tk

colors = {
    'Gray (Default)': '#D3D3D3',
    'Blue (Normal)': '#E8F4F8',
    'Peach (Sentiment)': '#FFF4E6',
    'Purple (R&L)': '#F0E6FF',
    'Green (Memory)': '#E6F7E6',
    'Green (Correct)': '#C8E6C9',
    'Red (Incorrect)': '#FFCDD2',
}

for name, color in colors.items():
    print(f"{name}: {color}")

root = tk.Tk()
root.title("Color Test")
for name, color in colors.items():
    frame = tk.Frame(root, bg=color, width=200, height=50)
    frame.pack(pady=5)
    label = tk.Label(frame, text=f"{name}\n{color}", bg=color)
    label.pack()
root.mainloop()
```
