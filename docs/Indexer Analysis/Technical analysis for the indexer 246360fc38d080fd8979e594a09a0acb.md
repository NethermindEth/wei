# Technical analysis for the indexer

## Overview

The project aims to collect DAO/Governance proposals (and accounts) from various ecosystems and their metadata and store them in a database. This is needed to collect a training dataset of good/bad proposals for the AI agent. The vector database will be used in the future to retrieve similar proposals and train AI on them. For the data collection, this is possible to use a relational DB as well. The service itself should be extensible for adding new networks or DAOs. 

## Data requirements

Data could be fetched using existing APIs such as [https://docs.snapshot.box](https://snapshot.box/#/explore)/ or [https://docs.tally.xyz/](https://docs.tally.xyz/set-up-and-technical-documentation/tally-architecture). Data fetching must be implemented for the chains that are not yet available on those APIs. 

In the context of the Wei project, the proposal object should have at least the following fields:

```jsx
{
	"title": "Title of the proposal",
	"description": "Description of proposal",
	"status": "ACCEPTED/REJECTED/...",
	"protocol-id": "Ethereum",
	"choices": [ /* possible choices */ ],
	"author": "proposal author",
	"comments": [ /* string array of discussion made */ ]
}
```

Note, that `title` , `description` and `network` are the most important fields, other ones could be missed. Protocol id - is a unique identifier of the network. For simplicity of use - it will be retrieved from the snapshot/tally API, but later should be extended to use combination of name, chain id and other metadata (`chain-id:protocol-id`).

Also, it’s important to have the actor entity indexed as well. It should have at least following fields:

```jsx
{
	"address": "0xaddress",
	"ens": "ens name",
	"name": "organisation name",
	"description": "Description of the entity",
	"votingPower": "Voting power of the entity",
	"protocl-id": "Network of the account (if any specific)"
}
```

In the future, user data will be updated periodically by a separate service that monitors public discourse and their on-chain activity.

> Note: in the future we need to add comments flow to the indexer service to pass it to the agent through webhooks
> 

## API

The following REST API endpoints need to be implemented:

| Endpoint (GET) | Description |
| --- | --- |
| /proposals/:id | Get a proposal by a specific ID. The ID will be a combination of protocol ID and proposal ID in the protocol (chain-id:protocol-id:proposal-id) |
| /proposals/:network | Get proposals by specific network (paginated) |
| /proposals?description=xyz | Find a proposal in a database by description/title  |
| /proposals/search?description=xyz | Find a proposal in a database by description/title  |
| /accounts?address=0x123 | Get an account by it’s address |
| /accounts?ens=abc.eth | Get an account by it’s ens |
| /hooks [POST] | Registers a webhook to pass fresh events to the agent (needs auth) |

For those methods the following status codes will occur: `200` , `404` , `500`

## Flow

![image.png](Technical%20analysis%20for%20the%20indexer%20246360fc38d080fd8979e594a09a0acb/image.png)

## Technology stack

Rust, Tokio, Axum, graphql_client, reqwest + client library for vector DB, sqlx, tracing, tracing-subscriber, tower

## Major consideration

- Make the service be very extendible by using abstracting the data sources (using Strategy pattern), so it will be easy to extend the project
- Add inner thread that will monitor for a new updates on proposals
- Discuss possible streaming feature (instead of webhooks)

## Testing strategy

The project should have unit and integration tests per each service level (database, application, endpoints).