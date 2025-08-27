# Wei

![Wei Logo](assets/wei.png)

**Advancing Agent-Driven Protocol Development**

Wei develops autonomous agents for blockchain protocol development and governance, focusing on creating specialized agents that participate in core development, protocol optimization, and governance processes within the Ethereum ecosystem. The platform consists of a Rust-based backend (agent and indexer services) and a React-based frontend UI.

## Links

- 📖 **[Vision & Mission](https://wei.nethermind.io/)** - Lite Paper
- 📋 **[Internal Documentation](https://www.notion.so/nethermind/Wei-Governance-Agents-231360fc38d0808ead4be02d94345198)** - Nethermind Notion
- 💬 **[Telegram](https://t.me/agentwei)** - @AgentWei
- 🔗 **[GitHub](https://github.com/nethermindeth/wei)** - Main Repository
- 🐳 **[Docker Setup](DOCKER.md)** - Docker Documentation

## Project Structure

The Wei project consists of three main components:

1. **Agent Service** (`crates/agent`) - Core AI agent functionality for governance analysis
2. **Indexer Service** (`crates/indexer`) - Blockchain data indexing and processing
3. **UI** (`ui/`) - React-based frontend for interacting with the agents

## Working with the Rust Backend

This repository is a Rust workspace with two crates: `crates/agent` and `crates/indexer`.

### Prerequisites

- **Rust toolchain**: Install via `rustup` (`https://rustup.rs`)
- **PostgreSQL 14+**: Local or Docker (for running migrations)
  - Example with Docker: `docker run --name wei-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16`
- **sqlx-cli** for managing migrations:
  - `cargo install sqlx-cli --no-default-features --features native-tls,postgres`
- **OpenRouter API key**: Required for AI agent functionality
  - Sign up at [OpenRouter](https://openrouter.ai/) and get an API key

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nethermindeth/wei.git
   cd wei
   ```

2. **Set up Rust**:
   ```bash
   rustup toolchain install stable
   rustup default stable
   cargo fetch
   ```

3. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration values
   ```

4. **Database Setup**:

   **Start PostgreSQL with Docker:**
   ```bash
   # Start PostgreSQL container
   docker run --name wei-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
   ```

   **Configure Environment Variables:**
   Make sure your `.env` file contains the correct database URL:
   ```
   WEI_AGENT_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wei_agent
   ```

### Build

- **Build everything**:
  ```bash
  cargo build --workspace
  ```

- **Build specific crates**:
  ```bash
  cargo build -p agent
  cargo build -p indexer
  ```

- **Expected output for Agent**:

The Wei Agent now features automatic database creation and migration management. When you run the agent for the first time, it will:
   - Check if the database exists
   - Create the database if needed
   - Run migrations automatically for new databases
   - Skip migrations for existing databases

   **First-time run output:**
   ```
   Running `target/debug/agent`
   2025-08-27T09:42:49.343451Z  INFO main ThreadId(01) Starting Wei Agent service...
   2025-08-27T09:42:49.343686Z  INFO main ThreadId(01) Connecting to postgres database to check if wei_agent exists
   2025-08-27T09:42:49.479824Z  INFO main ThreadId(01) Database wei_agent does not exist, creating it
   2025-08-27T09:42:49.569456Z  INFO main ThreadId(01) Created database: wei_agent
   2025-08-27T09:42:49.645587Z  INFO main ThreadId(01) New database detected, running migrations
   2025-08-27T09:42:49.708811Z  INFO main ThreadId(01) Database migrations completed successfully
   2025-08-27T09:42:49.708928Z  INFO main ThreadId(01) Database initialized successfully with migrations
   2025-08-27T09:42:49.708944Z  INFO main ThreadId(01) Wei Agent service started successfully
   ```

   **Subsequent runs output:**
   ```
   Running `target/debug/agent`
   2025-08-27T09:41:28.760128Z  INFO main ThreadId(01) Starting Wei Agent service...
   2025-08-27T09:41:28.760593Z  INFO main ThreadId(01) Connecting to postgres database to check if wei_agent exists
   2025-08-27T09:41:28.850690Z  INFO main ThreadId(01) Database wei_agent already exists
   2025-08-27T09:41:28.914459Z  INFO main ThreadId(01) Using existing database, skipping migrations
   2025-08-27T09:41:28.914484Z  INFO main ThreadId(01) Database initialized successfully with migrations
   2025-08-27T09:41:28.914489Z  INFO main ThreadId(01) Wei Agent service started successfully
   ```

### Run

- **Run agent service**:
  ```bash
  cargo run -p agent
  ```

- **Run indexer service**:
  ```bash
  cargo run -p indexer
  ```

### Test

- **Run all tests**:
  ```bash
  cargo test
  ```

- **Run specific crate tests**:
  ```bash
  cargo test -p agent
  cargo test -p indexer
  ```

- **Run specific test**:
  ```bash
  cargo test -p agent --test e2e_proposal_questions_test
  ```

### Lint and Format

- **Format code**:
  ```bash
  cargo fmt --all
  ```

- **Run linter**:
  ```bash
  cargo clippy --workspace --all-targets -- -D warnings
  ```

### Environment configuration

See the `env.example` file for a complete list of environment variables. Copy this file to `.env` and update the values as needed.

### API Authentication

The Agent service includes API key authentication for protected endpoints:

- **Configuration** (in `.env`):
  ```env
  # Comma-separated list of valid API keys
  WEI_AGENT_API_KEYS=key1,key2,key3
  
  # Enable/disable API key authentication (default: true)
  WEI_AGENT_API_KEY_AUTH_ENABLED=true
  ```

- **Usage**:
  - Public endpoints (e.g., `/health`) are accessible without authentication
  - Protected endpoints require an API key in the `x-api-key` header
  - Invalid requests receive `401 Unauthorized` or `403 Forbidden` responses

## UI Development

The Wei UI is built with React, Next.js, and TypeScript.

### Prerequisites

- **Node.js**: v18+ recommended
- **npm** or **yarn**: Latest version

### Setup

1. **Navigate to the UI directory**:
   ```bash
   cd ui
   ```

2. **Install dependencies**:
   ```bash
   pnpm install
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration values
   ```

### Development

1. **Start the development server**:
   ```bash
   pnpm dev
   ```

2. **Access the UI**:
   Open [http://localhost:3000](http://localhost:3000) in your browser

### Build

- **Create production build**:
  ```bash
  pnpm build
  ```

- **Run production build**:
  ```bash
  pnpm start
  ```

### Testing

- **Run tests**:
  ```bash
  pnpm  test
  ```

## Docker Setup

The project can be run using Docker and Docker Compose for easier setup and deployment.

### Prerequisites

- **Docker**: Install from [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
- **Docker Compose**: Usually included with Docker Desktop

### Quick Start

1. **Copy the environment file**:
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` with your configuration values**:
   - Set `WEI_AGENT_OPEN_ROUTER_API_KEY` to your OpenRouter API key
   - Configure database settings if needed
   - Set API keys for authentication

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **View logs**:
   ```bash
   docker-compose logs -f
   ```

5. **Access the services**:
   - UI: [http://localhost:3000](http://localhost:3000)
   - Agent API: [http://localhost:8080](http://localhost:8080)
   - Indexer API: [http://localhost:8081](http://localhost:8081)

For more detailed Docker instructions, see the [Docker documentation](DOCKER.md).

## Troubleshooting

### Common Issues

#### Database Connection

- **Error**: `sqlx::error::Error: error connecting to database: connection refused`
  - **Solution**: Ensure PostgreSQL is running and accessible with the configured credentials

#### API Key Authentication

- **Error**: `401 Unauthorized` or `403 Forbidden`
  - **Solution**: Check that you're using a valid API key in the `x-api-key` header

#### OpenRouter API

- **Error**: `Failed to get response from OpenRouter API`
  - **Solution**: Verify your OpenRouter API key is valid and properly configured

#### UI Development

- **Error**: `Module not found: Can't resolve '@apollo/client'`
  - **Solution**: Run `npm install` or `yarn install` in the `ui` directory

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/nethermindeth/wei/issues) for similar problems
2. Join the [Telegram group](https://t.me/agentwei) for community support
3. Create a new issue with detailed information about your problem

