import { ApolloClient, HttpLink, InMemoryCache } from "@apollo/client";

import { RetryLink } from "@apollo/client/link/retry";

const maxRetries = Number(process.env.NEXT_PUBLIC_GRAPHQL_MAX_QUERY_RETRIES || 5);
const delayBetweenRetries = Number(process.env.NEXT_PUBLIC_GRAPHQL_DELAY_BETWEEN_QUERY_RETRIES || 15000);
const snapshotGraphqlUrl = process.env.NEXT_PUBLIC_SNAPSHOT_GRAPHQL_URL || 'https://hub.snapshot.org/graphql';




const retryLink = new RetryLink({
    delay: {
        initial: delayBetweenRetries,
        max: delayBetweenRetries,
    },
    attempts: {
        max: maxRetries,
        retryIf: (error) => {
            // Retry on network errors
            const shouldRetry = (
                error.message.includes("429")  || // Rate limiting
                error.message.includes("timeout") ||
                error.message.includes("network")
            );

            console.warn(`Attempt failed: ${error.message}. Retrying: ${shouldRetry}`);
            return shouldRetry;
        }
    }
});

const httpLink = new HttpLink({
    uri: snapshotGraphqlUrl
});

// Combine links - chain them directly
const link = retryLink.concat(httpLink);

const cache = new InMemoryCache({
    typePolicies: {
        Query: {
            fields: {
                proposals: {
                    merge(existing = [], incoming) {
                        return [...existing, ...incoming];
                    },
                },
            },
        },
    },
});

export const apolloClient = new ApolloClient({
    cache,
    link,
    defaultOptions: {
        watchQuery: {
            fetchPolicy: "cache-and-network",
            errorPolicy: "all",
            nextFetchPolicy: "cache-first", 
        },
        query: {
            fetchPolicy: "cache-first", 
            errorPolicy: "all",
        },
        mutate: {
            errorPolicy: "all",
        },
    },
});