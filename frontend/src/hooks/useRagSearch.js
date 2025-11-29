// frontend/src/hooks/useRagSearch.js
import { useQuery } from "@tanstack/react-query";
import { ragSearch } from "../api/guriApi";

export const useRagSearch = (query) =>
  useQuery({
    queryKey: ["ragSearch", query],
    queryFn: () => ragSearch(query),
    enabled: Boolean(query),
  });
