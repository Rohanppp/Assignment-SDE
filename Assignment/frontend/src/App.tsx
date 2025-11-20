import { useMemo } from "react";
import { useReviews } from "./hooks/useReviews";

function formatDate(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function App() {
  const { reviews, loading, error, refresh } = useReviews();
  const hasData = reviews.length > 0;

  const headline = useMemo(() => {
    if (loading) return "Fetching latest reviews…";
    if (error) return "Could not load reviews";
    if (!hasData) return "No reviews yet";
    return "Latest WhatsApp reviews";
  }, [loading, error, hasData]);

  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">WhatsApp Product Review Collector</p>
          <h1>{headline}</h1>
          <p>
            Incoming WhatsApp reviews from Twilio are stored in Postgres and
            listed here in real time.
          </p>
        </div>
        <button className="refresh" onClick={refresh} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </header>

      {error && <p className="error">{error}</p>}

      <section className="card">
        {hasData ? (
          <table>
            <thead>
              <tr>
                <th>User</th>
                <th>Product</th>
                <th>Review</th>
                <th>WhatsApp</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((review) => (
                <tr key={review.id}>
                  <td>{review.user_name}</td>
                  <td>{review.product_name}</td>
                  <td className="review-body">{review.product_review}</td>
                  <td>{review.contact_number}</td>
                  <td>{formatDate(review.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty">
            <p>Start a WhatsApp conversation to see reviews appear here.</p>
          </div>
        )}
      </section>
    </div>
  );
}

