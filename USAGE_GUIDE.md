# Memory Bank DXT - Manual Session Recording Guide

**Created:** 2025-07-18.1910  
**Version:** 0.1.0 - Manual Triggers Phase  
**Purpose:** User guide for manual session recording with privacy controls

## 🚀 Quick Start

### 1. Install and Start
```bash
# Test the setup first
python test_dxt.py

# Build the DXT extension
dxt pack

# Install in Claude Desktop (double-click the .dxt file)
# Restart Claude Desktop
```

### 2. Initialize Your Session
```
start_session project_name="my_project"
```

**Claude will respond:**
> 🎯 **Session Started: my_project**
> 
> 📹 **Conversations are being recorded for posterity.**
> 
> **Available commands:**
> • `save_this` - Manually save current exchange  
> • `replay` - Show last recorded exchange
> • `off_the_record` - Toggle privacy mode
> • `session_status` - Check recording status
> 
> To opt out of recording, call `off_the_record`.

## 📋 Manual Commands

### Core Recording Commands

#### `save_this` - Save Current Exchange
**Usage:** When you want to preserve an important exchange
```
save_this note="This solution for authentication is brilliant"
```

**Claude responds:** `✅ Done.`

**What happens:**
- Captures Claude's response via AppleScript + clipboard
- Saves to exchanges table with your note
- Links to existing discussions/artifacts if relevant
- Makes content immediately searchable

#### `replay` - Show Last Exchange
**Usage:** Review what was last recorded
```
replay
```

**Claude responds:**
> 🔄 **Last Recorded Exchange**
> 
> **UUID:** abcd1234...
> **Timestamp:** 2025-07-18T19:15:30
> **Method:** manual_save_this
> 
> **Response:**
> [Claude's response content...]
> 
> **Note:** This solution for authentication is brilliant

### Privacy Controls

#### `off_the_record` - Privacy Mode
**Usage:** Stop recording for sensitive conversations
```
off_the_record
```

**Claude responds:**
> 🔴 **Off The Record Mode ENABLED**
> 
> Your exchanges will NOT be saved until you resume recording.
> Call `off_the_record` with enable=false to resume.

**Resume recording:**
```
off_the_record enable=false
```

#### `session_status` - Check Current State
**Usage:** See what's being recorded
```
session_status
```

**Claude responds:**
> 🟢 **Session Status**
> 
> **Project:** my_project
> **Recording:** Enabled
> **Mode:** RECORDING
> **Last Exchange:** abcd1234
> 
> **Database:** /path/to/context.db
> **Session Started:** Yes

## 🎯 Workflow Examples

### Basic Usage Pattern
```
# Start your session
start_session project_name="api_design"

# Work on your project...
[Discussion about API endpoints]

# Save important insights
save_this note="REST vs GraphQL decision rationale"

# Continue working...
[More discussion]

# Check what was saved
replay

# Need privacy for credentials discussion
off_the_record

# Discuss sensitive info...
[Credentials, secrets, etc.]

# Resume recording
off_the_record enable=false

# Continue with regular work...
```

### Privacy-First Session
```
# Start but opt out initially
start_session project_name="sensitive_project" opt_out=true

# Work privately first...
[Private discussion]

# Enable recording when ready
off_the_record enable=false

# Now start saving important parts
save_this note="Architecture decision"
```

## 🔧 Technical Details

### AppleScript Integration
The DXT extension uses AppleScript to:
- Detect Claude Desktop application
- Trigger clipboard copy of responses (`Cmd+Shift+C`)
- Capture conversation context automatically
- Operate silently in background

### Database Storage
Each `save_this` command:
- Generates unique exchange UUID
- Stores Claude's response + your note
- Links to related content in context.db
- Enables full-text search immediately
- Preserves conversation context

### Error Handling
Defensive programming ensures:
- Graceful failures with clear error messages
- Automatic retry for AppleScript operations
- Database validation before operations
- User-friendly error reporting

## 📊 Data Structure

### Exchange Record
```json
{
  "uuid": "exch-abc123...",
  "claude_response": "Full response text...",
  "user_note": "Why this is important",
  "capture_method": "manual_save_this",
  "timestamp": "2025-07-18T19:15:30",
  "session_recording": true,
  "project_name": "my_project"
}
```

### Privacy Controls
- `recording_enabled`: Master recording switch
- `off_the_record`: Temporary privacy mode
- `session_started`: Session initialization state
- User controls every save operation

## 🚀 Phase 2 Preview: Automatic Mode

**Coming next:** Fully automatic background monitoring
- Auto-detection of important exchanges
- Keyword-based significance scoring
- Background AppleScript monitoring
- Smart linking to existing content
- Silent operation with user control

**Manual triggers remain available** in automatic mode for explicit control.

## 🛠️ Troubleshooting

### "AppleScript failed"
- Ensure Claude Desktop is running
- Grant accessibility permissions to Terminal/Python
- Check: System Preferences > Security & Privacy > Accessibility

### "Database not found" 
- Verify context.db exists in memory-bank/ folder
- Run `session_status` to check database path
- Copy from original memory-bank_MCP project if needed

### "Capture failed"
- Try manually copying Claude's response first
- Check clipboard contains Claude's text
- Ensure Claude Desktop has focus when using `save_this`

### Tool not responding
- Check Claude Desktop MCP configuration
- Restart Claude Desktop after installing DXT
- Verify .dxt file installed correctly

## 💡 Pro Tips

### Effective Note-Taking
```
save_this note="bug-fix,authentication,security-pattern"
save_this note="decision: chose Redis over MongoDB for caching"
save_this note="TODO: implement rate limiting here"
```

### Session Organization
```
start_session project_name="sprint_23_backend"
# vs
start_session project_name="research_ai_tools"
```

### Privacy Best Practices
- Use `off_the_record` before discussing:
  - Credentials or API keys
  - Personal information
  - Confidential business details
  - Sensitive architectural decisions

### Replay for Context
```
# Before asking follow-up questions
replay

# Review what was important
session_status
```

---

**Remember:** This is Phase 1 with manual control. You decide what gets saved, when, and with what context. Nothing is recorded without your explicit `save_this` command (except session metadata).

**Next:** Once you're comfortable with manual triggers, we'll implement automatic background monitoring with the same privacy controls.
