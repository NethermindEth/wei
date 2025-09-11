/// Database query macros to reduce repetition in SQLx query building

/// Macro for building and executing a SQLx query with parameters
/// 
/// # Examples
/// 
/// ```
/// let result = db_query!(pool, "DELETE FROM cache_entries WHERE cache_key = $1", cache_key).await?;
/// ```
#[macro_export]
macro_rules! db_query {
    ($pool:expr, $query:expr) => {
        sqlx::query($query)
            .execute($pool)
            .await
    };
    ($pool:expr, $query:expr, $($param:expr),+) => {
        sqlx::query($query)
            $(.bind($param))*
            .execute($pool)
            .await
    };
}

/// Macro for building and executing a SQLx query that returns a single row
/// 
/// # Examples
/// 
/// ```
/// let row = db_query_one!(pool, "SELECT * FROM cache_entries WHERE cache_key = $1", cache_key).await?;
/// ```
#[macro_export]
macro_rules! db_query_one {
    ($pool:expr, $query:expr) => {
        sqlx::query($query)
            .fetch_one($pool)
            .await
    };
    ($pool:expr, $query:expr, $($param:expr),+) => {
        sqlx::query($query)
            $(.bind($param))*
            .fetch_one($pool)
            .await
    };
}

/// Macro for building and executing a SQLx query that returns an optional row
/// 
/// # Examples
/// 
/// ```
/// let row = db_query_optional!(pool, "SELECT * FROM cache_entries WHERE cache_key = $1", cache_key).await?;
/// ```
#[macro_export]
macro_rules! db_query_optional {
    ($pool:expr, $query:expr) => {
        sqlx::query($query)
            .fetch_optional($pool)
            .await
    };
    ($pool:expr, $query:expr, $($param:expr),+) => {
        sqlx::query($query)
            $(.bind($param))*
            .fetch_optional($pool)
            .await
    };
}

/// Macro for building and executing a SQLx query that returns all rows
/// 
/// # Examples
/// 
/// ```
/// let rows = db_query_all!(pool, "SELECT * FROM cache_entries WHERE expires_at > $1", now).await?;
/// ```
#[macro_export]
macro_rules! db_query_all {
    ($pool:expr, $query:expr) => {
        sqlx::query($query)
            .fetch_all($pool)
            .await
    };
    ($pool:expr, $query:expr, $($param:expr),+) => {
        sqlx::query($query)
            $(.bind($param))*
            .fetch_all($pool)
            .await
    };
}

/// Macro for building and executing a SQLx query that maps to a specific type
/// 
/// # Examples
/// 
/// ```
/// let row = db_query_as_one!(CacheEntryRow, pool, "SELECT * FROM cache_entries WHERE cache_key = $1", cache_key).await?;
/// ```
#[macro_export]
macro_rules! db_query_as_one {
    ($type:ty, $pool:expr, $query:expr) => {
        sqlx::query_as::<_, $type>($query)
            .fetch_one($pool)
            .await
    };
    ($type:ty, $pool:expr, $query:expr, $($param:expr),+) => {
        sqlx::query_as::<_, $type>($query)
            $(.bind($param))*
            .fetch_one($pool)
            .await
    };
}

/// Macro for building and executing a SQLx query that maps to a specific type and returns an optional row
/// 
/// # Examples
/// 
/// ```
/// let row = db_query_as_optional!(CacheEntryRow, pool, "SELECT * FROM cache_entries WHERE cache_key = $1", cache_key).await?;
/// ```
#[macro_export]
macro_rules! db_query_as_optional {
    ($type:ty, $pool:expr, $query:expr) => {
        sqlx::query_as::<_, $type>($query)
            .fetch_optional($pool)
            .await
    };
    ($type:ty, $pool:expr, $query:expr, $($param:expr),+) => {
        sqlx::query_as::<_, $type>($query)
            $(.bind($param))*
            .fetch_optional($pool)
            .await
    };
}

/// Macro for building and executing a SQLx query that maps to a specific type and returns all rows
/// 
/// # Examples
/// 
/// ```
/// let rows = db_query_as_all!(CacheEntryRow, pool, "SELECT * FROM cache_entries WHERE expires_at > $1", now).await?;
/// ```
#[macro_export]
macro_rules! db_query_as_all {
    ($type:ty, $pool:expr, $query:expr) => {
        sqlx::query_as::<_, $type>($query)
            .fetch_all($pool)
            .await
    };
    ($type:ty, $pool:expr, $query:expr, $($param:expr),+) => {
        sqlx::query_as::<_, $type>($query)
            $(.bind($param))*
            .fetch_all($pool)
            .await
    };
}
