import React, { useState, useRef, useEffect, useCallback } from "react";

export default function SearchChatWidget() {
  const [results, setResults] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [totalResults, setTotalResults] = useState(0);
  const [pageToken, setPageToken] = useState(null);
  const [hasMore, setHasMore] = useState(false);

  const inputRef = useRef(null);
  const listRef = useRef(null);

  // Autofocus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Fetch search results
  const fetchResults = useCallback(
    async ({ append = false, token = null } = {}) => {
      if (!input.trim()) return;
      setIsLoading(true);

      try {
        const res = await fetch("http://localhost:4000/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: input,
            pageToken: token,
          }),
        });
        const data = await res.json();
        const rawResults = Array.isArray(data.results) ? data.results : [];
        
        const mapped = rawResults.map((r) =>
            r.document && r.document.structData
              ? {
                  id: r.document.id || Math.random(),
                  title: r.document.structData.title,
                  link: r.document.structData.link,
                }
              : null
          ).filter(Boolean);

        setResults((prev) => (append ? [...prev, ...mapped] : mapped));
        setTotalResults(data.totalSize ?? mapped.length ?? 0);
        setPageToken(data.nextPageToken || null);
        setHasMore(!!data.nextPageToken);
      } catch {
        if (!append) setResults([]);
        setHasMore(false);
      }
      setIsLoading(false);
    },
    [input]
  );

  // New search (reset)
  const startNewSearch = (e) => {
    if (e) e.preventDefault();
    setResults([]);
    setPageToken(null);
    setHasMore(false);
    fetchResults({ append: false });
  };

  // Infinite scroll event
  useEffect(() => {
    const onScroll = () => {
      const el = listRef.current;
      if (
        el &&
        hasMore &&
        !isLoading &&
        el.scrollHeight - el.scrollTop - el.clientHeight < 100
      ) {
        fetchResults({ append: true, token: pageToken });
      }
    };
    const el = listRef.current;
    if (el) el.addEventListener("scroll", onScroll);
    return () => {
      if (el) el.removeEventListener("scroll", onScroll);
    };
  }, [hasMore, isLoading, pageToken, fetchResults]);

  // Render
  return (
    <div
      style={{
        background: "#F6F8FB",
        borderRadius: 12,
        boxShadow: "0 2px 16px #0002",
        maxWidth: 400,
        width: "100%",
        margin: "18px auto",
        padding: "10px 16px 16px 16px",
        fontFamily: "Inter, Arial, sans-serif",
        border: "1px solid #eaeaea",
      }}
    >
      {/* Search Bar */}
      <form
        style={{ display: "flex", alignItems: "center", marginBottom: 12 }}
        onSubmit={startNewSearch}
        autoComplete="off"
      >
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Search…"
          style={{
            width: "100%",
            border: "1px solid #d6d9e0",
            borderRadius: 16,
            padding: "7px 13px",
            fontSize: 15,
            background: "#fff",
            outline: "none",
            height: 32,
          }}
          onKeyDown={e => {
            if (e.key === "Enter") startNewSearch(e);
          }}
        />
        <button
          type="submit"
          disabled={isLoading}
          style={{
            marginLeft: -34,
            border: "none",
            background: "none",
            cursor: isLoading ? "default" : "pointer",
            fontSize: 18,
            color: "#999",
            outline: "none",
            padding: "0 10px 0 2px",
          }}
          tabIndex={-1}
        >
          🔍
        </button>
      </form>

      {/* Results Count */}
      {input && !isLoading && results.length > 0 && (
        <div
          style={{
            color: "#888",
            fontSize: 12,
            margin: "0 0 6px 3px",
            textAlign: "left",
          }}
        >
          Showing {results.length}
          {totalResults ? ` of ${totalResults}` : ""} results
        </div>
      )}

      {/* Results List */}
      <div
        ref={listRef}
        style={{
          maxHeight: 220,
          overflowY: "auto",
          background: "#fff",
          borderRadius: 8,
          border: "1px solid #eee",
          padding: "5px 3px",
          minHeight: 30,
        }}
      >
        {results.length === 0 && input && !isLoading && (
          <div
            style={{
              color: "#bbb",
              textAlign: "center",
              fontSize: 15,
              marginTop: 19,
              marginBottom: 17,
              fontWeight: 500,
            }}
          >
            No results found.
          </div>
        )}
        {results.map((r) => (
          <div
            key={r.id}
            style={{
              padding: "7px 3px 6px 3px",
              borderBottom: "1px solid #f3f5fa",
              fontSize: 15,
              marginBottom: 1,
              display: "flex",
              alignItems: "center",
            }}
          >
            <a
              href={r.link}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                color: "#2154b6",
                fontWeight: 500,
                fontSize: 15.5,
                textDecoration: "none",
                wordBreak: "break-all",
              }}
              title={r.title}
            >
              {r.title}
            </a>
          </div>
        ))}
        {isLoading && (
          <div
            style={{
              color: "#bbb",
              textAlign: "center",
              padding: 9,
              fontSize: 15,
            }}
          >
            Loading…
          </div>
        )}
      </div>
    </div>
  );
}