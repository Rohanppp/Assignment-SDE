import { useCallback, useEffect, useState } from "react";

export type Review = {
  id: number;
  contact_number: string;
  user_name: string;
  product_name: string;
  product_review: string;
  created_at: string;
};

const rawBase = import.meta.env.VITE_API_BASE_URL ?? "";
const apiBase = rawBase.replace(/\/$/, "");
const reviewsEndpoint = apiBase ? `${apiBase}/api/reviews` : "/api/reviews";

export function useReviews() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReviews = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(reviewsEndpoint);
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Request failed with status ${response.status}: ${errorText}`);
      }
      const payload = (await response.json()) as Review[];
      setReviews(payload);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unexpected error";
      console.error("Error fetching reviews:", err);
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchReviews();
  }, [fetchReviews]);

  return { reviews, loading, error, refresh: fetchReviews };
}


