# Memory Bank DXT - Reliable AI Context Management

**Created:** 2025-07-18.1840  
**Version:** 0.1.0  
**Type:** Desktop Extension (DXT) for Claude Desktop

## Overview

Memory Bank DXT is a Desktop Extension that provides reliable AI context management built with defensive programming principles. This extension addresses critical reliability issues found in traditional memory bank systems by implementing proper MCP protocol validation, structured error handling, and comprehensive session memory storage.

## Key Features

✅ **Defensive Programming** - All operations validated and error-checked  
✅ **Silent Failure Detection** - Monitors and prevents data loss  
✅ **Proper MCP Validation** - Structured tool responses and clear schemas  
✅ **Auto-Save Monitoring** - Ensures conversation data persistence  
✅ **FTS Sync Validation** - Prevents search index corruption  
✅ **Timeout Management** - Prevents hanging operations  

## DXT Architecture

```
memory_bank_DXT/
├── manifest.json       # DXT extension metadata
├── server/            
│   └── main.py        # Python MCP server with defensive programming
├── memory-bank/       
│   └── context.db     # SQLite database with full context
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Installation

### Prerequisites
- Claude Desktop (macOS/Windows) with DXT support
- Python 3.8+ 
- Node.js and npm (for DXT CLI)

### Build and Install

1. **Install DXT CLI:**
```bash
npm install -g @anthropic-ai/dxt
```

2. **Build Extension:**
```bash
cd memory_bank_DXT
dxt pack
```

3. **Install in Claude Desktop:**
- Double-click the generated `.dxt` file
- Claude Desktop will show installation dialog
- Click "Install" to add the extension

## Usage

Once installed, Memory Bank DXT provides these tools in Claude Desktop:

### `memory_bank_help`
Show comprehensive help and feature overview

### `get_memory_bank_status` 
Get database status with health monitoring and validation checks

### `search_all_content`
Universal full-text search across all content types
- **Parameters:**
  - `query` (required): Search terms
  - `limit` (optional): Max results (1-100, default: 20)

## Reliability Improvements

This DXT implementation addresses specific issues found in the original memory-bank system:

### Silent Failure Prevention
- **FTS Sync Validation:** Verifies search index updates complete successfully
- **Auto-Save Monitoring:** Confirms conversation data persistence  
- **Operation Timeouts:** Prevents hanging on database operations
- **Error Recovery:** Graceful handling of database corruption or access issues

### Defensive Programming
- **Input Validation:** All parameters checked before processing
- **Type Safety:** Comprehensive type checking and validation
- **Response Validation:** Ensures all tool responses follow MCP schema
- **Resource Management:** Proper connection handling and cleanup

### Error Handling
- **Structured Logging:** Comprehensive error tracking and debugging
- **User-Friendly Messages:** Clear error communication without technical jargon
- **Graceful Degradation:** Continues operating when non-critical components fail
- **Recovery Procedures:** Automatic recovery from common failure scenarios

## Development

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests (when implemented)
pytest

# Type checking
mypy server/main.py
```

### Database Schema
The extension uses the existing context.db schema from the original memory-bank project, ensuring full compatibility with existing data.

## Migration from Original Memory Bank

This DXT extension includes the complete context database from the original memory-bank_MCP project, preserving:
- All conversation history
- Decision logs
- Project documentation  
- Full-text search indexes
- Reliability issue analysis

## Contributing

This is a clean implementation following DXT best practices. Future improvements should maintain:
- Defensive programming principles
- Comprehensive error handling
- DXT compliance standards
- Clear documentation and logging

## License

This project builds upon the original memory-bank_MCP work and follows the same licensing terms.

## Support

For issues or questions:
1. Check the comprehensive help: `memory_bank_help`
2. Review logs: `memory_bank_dxt.log`
3. Verify database status: `get_memory_bank_status`

---

**Built with DXT architecture for maximum reliability and user experience.**
