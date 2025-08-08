# Wei

![Wei Logo](assets/wei.png)

**Advancing Agent-Driven Protocol Development**

Wei develops autonomous agents for blockchain protocol development and governance, focusing on creating specialized agents that participate in core development, protocol optimization, and governance processes within the Ethereum ecosystem.

## Links

- 📖 **[Vision & Mission](https://wei-lite-paper.vercel.app/)** - Lite Paper
- 📋 **[Internal Documentation](https://www.notion.so/nethermind/Wei-Governance-Agents-231360fc38d0808ead4be02d94345198)** - Nethermind Notion
- 💬 **[Telegram](https://t.me/AgentWei)** - @AgentWei
- 🔗 **[GitHub](https://github.com/nethermindeth/wei)** - Main Repository

## Working with the Rust workspace

This repository is a Rust workspace with two crates: `crates/agent` and `crates/indexer`.

### Prerequisites

- **Rust toolchain**: Install via `rustup` (`https://rustup.rs`)
- **PostgreSQL 14+**: Local or Docker (for running migrations)
  - Example with Docker: `docker run --name wei-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16`
- (Optional) **sqlx-cli** for managing migrations from the terminal:
  - `cargo install sqlx-cli --no-default-features --features native-tls,postgres`

### Setup

- Ensure stable toolchain is installed and default:
  - `rustup toolchain install stable && rustup default stable`
- From the workspace root, fetch dependencies:
  - `cargo fetch`

### Build

- Build everything: `cargo build --workspace`
- Build a single crate:
  - Agent: `cargo build -p agent`
  - Indexer: `cargo build -p indexer`

### Run

- Run a specific crate:
  - Agent: `cargo run -p agent`
  - Indexer: `cargo run -p indexer`

### Test

- All tests: `cargo test`
- Per crate:
  - Agent: `cargo test -p agent`
  - Indexer: `cargo test -p indexer`

### Lint and format

- Format: `cargo fmt --all`
- Lint: `cargo clippy --workspace --all-targets -- -D warnings`
- Note: The workspace denies `missing_docs`; add doc comments to public items to avoid build failures.

### Database and migrations (sqlx)

Each crate has its own migrations under `crates/<crate>/migrations/`.

- Create databases (example):
  - `createdb wei_agent` and `createdb wei_indexer` (or use your preferred method)
- Run migrations via sqlx-cli:
  - Agent:
    - `export DATABASE_URL=postgres://postgres:postgres@localhost:5432/wei_agent`
    - `sqlx migrate run --source crates/agent/migrations`
  - Indexer:
    - `export DATABASE_URL=postgres://postgres:postgres@localhost:5432/wei_indexer`
    - `sqlx migrate run --source crates/indexer/migrations`

### Environment configuration

- Example `.env` for Agent:

```env
  todo
```

- Example `.env` for Indexer:

```env
  todo
```

Note:

- The binaries currently initialize logging and then wait for Ctrl+C. As services are implemented (API, DB pool, background tasks), they will use the above configuration and databases.
