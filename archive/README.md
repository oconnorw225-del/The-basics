# Archive Directory

This directory contains deprecated and superseded files that are no longer actively used in the project but are preserved for historical reference.

## Contents

### Scripts

#### `consolidate.sh` (Archived: 2025-12-12)
- **Original Location**: `automation/consolidate.sh`
- **Purpose**: Old repository consolidation script used in early GitHub Actions workflows
- **Reason for Archival**: The consolidation process is now complete, and this script is no longer needed for ongoing operations
- **Replacement**: Modern deployment uses AWS automated workflows and the unified system

#### `install_unified_system.sh` (Archived: 2025-12-12)
- **Original Location**: Root directory
- **Purpose**: Early version of system installation script
- **Reason for Archival**: Superseded by more comprehensive installation scripts
- **Replacement**: Use `auto_install.sh` or `install_chimera_production.sh` for new installations

## Why Archive Instead of Delete?

These files are archived rather than deleted to:
1. Maintain historical context for the project's evolution
2. Allow recovery if specific functionality needs to be referenced
3. Provide audit trail for past deployment methods
4. Enable learning from previous approaches

## Guidelines

- **Do not modify** archived files
- **Do not reference** archived files in active code or documentation
- If you need functionality from an archived file, implement it in the current codebase rather than un-archiving
