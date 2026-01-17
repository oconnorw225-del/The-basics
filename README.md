# Project Chimera

An AI-powered trading platform built with a modern monorepo architecture.

## Architecture

This is a monorepo managed with Turborepo and pnpm workspaces containing:

### Apps
- **dashboard** - Next.js-based trading dashboard with real-time data visualization
- **trading-api** - Backend API for trading operations and data management

### Packages
- **shared-types** - TypeScript type definitions shared across the monorepo
- **shared-utils** - Common utility functions and helpers
- **trading-engine** - Core trading logic and execution engine
- **ai-strategies** - AI/ML-powered trading strategies
- **ui-components** - Reusable React components library

### Infrastructure
- **docker** - Docker configurations for containerized deployment

## Getting Started

### Prerequisites
- Node.js >= 18.0.0
- pnpm >= 8.0.0
- Docker (optional, for containerized development)

### Installation

```bash
# Install dependencies
pnpm install

# Build all packages
pnpm build

# Start development servers
pnpm dev
```

### Docker Development

```bash
# Start all services
docker-compose up

# Build and start
docker-compose up --build
```

## Project Structure

```
project-chimera/
├── apps/
│   ├── dashboard/           # Trading dashboard (Next.js)
│   └── trading-api/         # Backend API (Node.js/Express)
├── packages/
│   ├── shared-types/        # Shared TypeScript types
│   ├── shared-utils/        # Shared utilities
│   ├── trading-engine/      # Core trading engine
│   ├── ai-strategies/       # AI trading strategies
│   └── ui-components/       # UI component library
├── infrastructure/
│   └── docker/              # Docker configurations
├── package.json             # Root package configuration
├── pnpm-workspace.yaml      # pnpm workspace configuration
├── turbo.json               # Turborepo configuration
└── docker-compose.yml       # Docker Compose configuration
```

## Development

### Available Scripts

- `pnpm dev` - Start all development servers
- `pnpm build` - Build all packages and apps
- `pnpm test` - Run tests across all packages
- `pnpm lint` - Lint all packages
- `pnpm format` - Format code with Prettier
- `pnpm clean` - Clean build artifacts and dependencies

### Adding Dependencies

```bash
# Add to root
pnpm add -w <package>

# Add to specific workspace
pnpm add <package> --filter <workspace-name>
```

## License

Proprietary - All rights reserved
