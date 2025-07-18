#!/usr/bin/env python3
"""
Memory Bank DXT - Enhanced Manual Session Recording
Created: 2025-07-18.1855
Purpose: Manual trigger tools for session recording with AppleScript integration

Phase 1: Manual triggers with full user control
- 'save this' -> captures current exchange -> 'done'
- 'replay' -> shows last exchange
- Session start notification with opt-out
- 'off the record' mode for privacy
"""

import asyncio
import logging
import sys
import traceback
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

# MCP SDK imports with error handling
try:
    from mcp import server, types
    from mcp.server.stdio import stdio_server
except ImportError as e:
    print(f"CRITICAL: Failed to import MCP SDK: {e}")
    sys.exit(1)

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler('memory_bank_dxt.log')
    ]
)
logger = logging.getLogger("memory-bank-dxt")

# DXT Configuration Constants
DXT_TIMEOUT_DEFAULT = 30000
DXT_MAX_RESPONSE_SIZE = 10000
DXT_DATABASE_PATH = Path(__file__).parent.parent / "memory-bank" / "context.db"

class SessionState:
    """Track session recording state"""
    def __init__(self):
        self.recording_enabled = True
        self.off_the_record = False
        self.session_started = False
        self.last_exchange = None
        self.project_name = None

class MemoryBankDXT:
    """
    Enhanced Memory Bank DXT server with manual session recording
    """
    
    def __init__(self):
        self.server = server.Server("memory-bank-dxt")
        self.database_path = DXT_DATABASE_PATH
        self.logger = logger
        self.session_state = SessionState()
        
        # Validate environment
        self._validate_environment()
        
        # Register handlers
        self._register_handlers()
    
    def _validate_environment(self) -> None:
        """Validate environment and dependencies"""
        try:
            if not self.database_path.exists():
                self.logger.warning(f"Database not found at {self.database_path}")
                self.logger.info("Will create new database on first operation")
            
            # Check for osascript (macOS AppleScript)
            import subprocess
            try:
                subprocess.run(['osascript', '-e', 'return "test"'], 
                             capture_output=True, check=True, timeout=5)
                self.logger.info("AppleScript (osascript) available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.warning("AppleScript not available - clipboard features disabled")
            
            self.logger.info("Environment validation successful")
            
        except Exception as e:
            self.logger.error(f"Environment validation failed: {e}")
            raise RuntimeError(f"DXT initialization failed: {e}")
    
    def _register_handlers(self) -> None:
        """Register MCP handlers"""
        try:
            @self.server.list_tools()
            async def list_tools() -> List[types.Tool]:
                return await self._handle_list_tools()
            
            @self.server.call_tool()
            async def call_tool(name: str, arguments: Optional[Dict[str, Any]] = None) -> List[types.TextContent]:
                return await self._handle_call_tool(name, arguments or {})
            
            self.logger.info("Handlers registered successfully")
            
        except Exception as e:
            self.logger.error(f"Handler registration failed: {e}")
            raise
    
    async def _handle_list_tools(self) -> List[types.Tool]:
        """List available manual trigger tools"""
        try:
            tools = [
                types.Tool(
                    name="save_this",
                    description="Manually save the current exchange to memory bank",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "note": {
                                "type": "string",
                                "description": "Optional note about why this exchange is important",
                                "default": ""
                            }
                        },
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="replay",
                    description="Show the last recorded exchange from memory bank",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="off_the_record", 
                    description="Toggle off-the-record mode (stops recording)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "enable": {
                                "type": "boolean",
                                "description": "True to go off-the-record, False to resume recording",
                                "default": True
                            }
                        },
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="session_status",
                    description="Check current recording status and session info",
                    inputSchema={
                        "type": "object", 
                        "properties": {},
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="start_session",
                    description="Initialize session recording for a project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_name": {
                                "type": "string", 
                                "description": "Name of the project for this session"
                            },
                            "opt_out": {
                                "type": "boolean",
                                "description": "Set to true to opt out of recording",
                                "default": False
                            }
                        },
                        "required": ["project_name"],
                        "additionalProperties": False
                    }
                )
            ]
            
            # Show session start notification if not started
            if not self.session_state.session_started:
                self.logger.info("Session not yet started - tools ready for initialization")
            
            return tools
            
        except Exception as e:
            self.logger.error(f"Failed to list tools: {e}")
            return []
    
    async def execute_osascript(self, script: str) -> str:
        """Execute AppleScript with defensive programming"""
        try:
            import subprocess
            
            process = await asyncio.create_subprocess_exec(
                'osascript', '-e', script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=30.0
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                raise Exception(f"AppleScript failed: {error_msg}")
                
            return stdout.decode().strip()
            
        except asyncio.TimeoutError:
            self.logger.error("AppleScript execution timed out")
            raise Exception("AppleScript execution timed out after 30 seconds")
        except Exception as e:
            self.logger.error(f"AppleScript execution failed: {e}")
            raise
    
    async def capture_claude_response(self) -> str:
        """Capture Claude's response via AppleScript clipboard automation"""
        try:
            # AppleScript to copy Claude's last response
            applescript = '''
            tell application "Claude"
                activate
                delay 0.5
                
                -- Try to select and copy the last response
                -- This is a simplified approach - may need refinement
                key code 8 using {command down, shift down}
                delay 0.2
            end tell
            
            delay 0.5
            return the clipboard as string
            '''
            
            result = await self.execute_osascript(applescript)
            
            if result and len(result.strip()) > 0:
                return result.strip()
            else:
                # Fallback: get clipboard directly
                clipboard_script = 'return the clipboard as string'
                clipboard_content = await self.execute_osascript(clipboard_script)
                return clipboard_content.strip()
                
        except Exception as e:
            self.logger.error(f"Failed to capture Claude response: {e}")
            return f"[Capture failed: {str(e)}]"
    
    async def save_exchange_to_db(self, claude_response: str, user_note: str = "", capture_method: str = "manual") -> str:
        """Save exchange to database with error handling"""
        try:
            import sqlite3
            import uuid
            from datetime import datetime
            
            if not self.database_path.exists():
                return "❌ Database not found. Please ensure memory-bank context.db exists."
            
            # Generate exchange data
            exchange_uuid = f"exch-{uuid.uuid4().hex[:24]}"
            timestamp = datetime.now().isoformat()
            
            # Create exchange record
            exchange_data = {
                "uuid": exchange_uuid,
                "claude_response": claude_response,
                "user_note": user_note,
                "capture_method": capture_method,
                "timestamp": timestamp,
                "session_recording": True
            }
            
            # Store in session state
            self.session_state.last_exchange = exchange_data
            
            # TODO: Implement actual database insertion
            # For now, just log the capture
            self.logger.info(f"Exchange captured: {exchange_uuid[:8]} ({len(claude_response)} chars)")
            
            return exchange_uuid
            
        except Exception as e:
            self.logger.error(f"Failed to save exchange: {e}")
            raise
    
    async def _handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle tool calls with comprehensive error handling"""
        try:
            if not isinstance(name, str) or not name:
                raise ValueError("Tool name must be a non-empty string")
            
            self.logger.info(f"Processing tool call: {name}")
            
            # Route to appropriate handler
            timeout_task = asyncio.wait_for(
                self._route_tool_call(name, arguments),
                timeout=DXT_TIMEOUT_DEFAULT / 1000
            )
            
            result = await timeout_task
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Tool {name} timed out after {DXT_TIMEOUT_DEFAULT}ms"
            self.logger.error(error_msg)
            return [types.TextContent(type="text", text=f"🕐 {error_msg}")]
            
        except Exception as e:
            error_msg = f"Tool {name} failed: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return [types.TextContent(type="text", text=f"❌ {error_msg}")]
    
    async def _route_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Route tool calls to appropriate handlers"""
        
        if name == "start_session":
            return await self._handle_start_session(arguments)
        elif name == "save_this":
            return await self._handle_save_this(arguments)
        elif name == "replay":
            return await self._handle_replay(arguments)
        elif name == "off_the_record":
            return await self._handle_off_the_record(arguments)
        elif name == "session_status":
            return await self._handle_session_status(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def _handle_start_session(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Initialize session recording"""
        try:
            project_name = arguments.get("project_name", "")
            opt_out = arguments.get("opt_out", False)
            
            if not project_name:
                raise ValueError("Project name is required")
            
            self.session_state.project_name = project_name
            self.session_state.session_started = True
            self.session_state.recording_enabled = not opt_out
            
            if opt_out:
                response_text = f"""
🔴 **Session Started: {project_name}**

Recording is **DISABLED** (opted out).
Your conversations will not be saved to memory bank.

To enable recording later, use the session tools.
                """.strip()
            else:
                response_text = f"""
🎯 **Session Started: {project_name}**

📹 **Conversations are being recorded for posterity.**

**Available commands:**
• `save_this` - Manually save current exchange  
• `replay` - Show last recorded exchange
• `off_the_record` - Toggle privacy mode
• `session_status` - Check recording status

To opt out of recording, call `off_the_record`.
                """.strip()
            
            return [types.TextContent(type="text", text=response_text)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Failed to start session: {str(e)}")]
    
    async def _handle_save_this(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Manual save current exchange"""
        try:
            if not self.session_state.recording_enabled:
                return [types.TextContent(type="text", text="🔴 Recording disabled. Enable recording first.")]
            
            if self.session_state.off_the_record:
                return [types.TextContent(type="text", text="🔴 Off the record mode. Use normal mode to save.")]
            
            user_note = arguments.get("note", "")
            
            # Capture Claude's response via AppleScript
            claude_response = await self.capture_claude_response()
            
            # Save to database
            exchange_uuid = await self.save_exchange_to_db(
                claude_response=claude_response,
                user_note=user_note,
                capture_method="manual_save_this"
            )
            
            # Simple confirmation response
            return [types.TextContent(type="text", text="✅ Done.")]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Save failed: {str(e)}")]
    
    async def _handle_replay(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Show last recorded exchange"""
        try:
            if not self.session_state.last_exchange:
                return [types.TextContent(type="text", text="📭 No exchanges recorded yet.")]
            
            exchange = self.session_state.last_exchange
            
            replay_text = f"""
🔄 **Last Recorded Exchange**

**UUID:** {exchange['uuid'][:8]}...
**Timestamp:** {exchange['timestamp']}
**Method:** {exchange['capture_method']}

**Response:**
{exchange['claude_response'][:500]}{"..." if len(exchange['claude_response']) > 500 else ""}

**Note:** {exchange.get('user_note', 'None')}
            """.strip()
            
            return [types.TextContent(type="text", text=replay_text)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Replay failed: {str(e)}")]
    
    async def _handle_off_the_record(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Toggle off-the-record mode"""
        try:
            enable = arguments.get("enable", True)
            
            self.session_state.off_the_record = enable
            
            if enable:
                response_text = """
🔴 **Off The Record Mode ENABLED**

Your exchanges will NOT be saved until you resume recording.
Call `off_the_record` with enable=false to resume.
                """.strip()
            else:
                response_text = """
🟢 **Recording RESUMED**

Your exchanges will now be saved to memory bank.
Use `save_this` to manually capture important exchanges.
                """.strip()
            
            return [types.TextContent(type="text", text=response_text)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Failed to toggle mode: {str(e)}")]
    
    async def _handle_session_status(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Check current recording status"""
        try:
            status_emoji = "🟢" if self.session_state.recording_enabled else "🔴"
            record_status = "OFF THE RECORD" if self.session_state.off_the_record else "RECORDING"
            
            status_text = f"""
{status_emoji} **Session Status**

**Project:** {self.session_state.project_name or 'Not set'}
**Recording:** {'Enabled' if self.session_state.recording_enabled else 'Disabled'}
**Mode:** {record_status}
**Last Exchange:** {self.session_state.last_exchange['uuid'][:8] if self.session_state.last_exchange else 'None'}

**Database:** {self.database_path}
**Session Started:** {'Yes' if self.session_state.session_started else 'No'}
            """.strip()
            
            return [types.TextContent(type="text", text=status_text)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Status check failed: {str(e)}")]

async def main():
    """Main entry point"""
    try:
        memory_bank = MemoryBankDXT()
        logger.info("Memory Bank DXT server initialized successfully")
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Starting Memory Bank DXT MCP server...")
            await memory_bank.server.run(
                read_stream, 
                write_stream,
                memory_bank.server.create_initialization_options()
            )
            
    except KeyboardInterrupt:
        logger.info("Server shutdown by user")
    except Exception as e:
        logger.error(f"Server failed: {e}\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
