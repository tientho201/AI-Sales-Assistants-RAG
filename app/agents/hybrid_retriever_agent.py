"""
Hybrid Retriever Agent.
Queries both Qdrant (Vector DB) and Neo4j (Graph DB),
and merges their results using Reciprocal Rank Fusion (RRF).
"""
from app.config import settings
from app.vector.vector_retriever import search_vector_products
from app.vector.hybird_retriever import search_bm25_products
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class HybridRetrieverAgent:
    def run(self, current_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Performs vector search and graph search in parallel,
        normalizes and merges results, and returns top suitable commercial vehicles.
        """
        top_k = settings.TOP_K_HYBRID_RETRIEVER or 3
        vector_limit = settings.VECTOR_TOP_K or 5
        graph_limit = settings.GRAPH_TOP_K or 5

        # 1. Build a descriptive semantic query for Qdrant Vector Search
        query_parts = []
        if current_requirements.get("brand"):
            query_parts.append(f"hãng {current_requirements['brand']}")
        if current_requirements.get("vehicle_type"):
            query_parts.append(f"xe {current_requirements['vehicle_type']}")
        if current_requirements.get("cargo_type"):
            query_parts.append(f"chở {current_requirements['cargo_type']}")
        if current_requirements.get("payload"):
            query_parts.append(
                f"tải trọng {current_requirements['payload']} kg")
        if current_requirements.get("fuel_type"):
            query_parts.append(
                f"nhiên liệu {current_requirements['fuel_type']}")
        if current_requirements.get("budget"):
            query_parts.append(
                f"giá dưới {current_requirements['budget']} triệu")

        semantic_query = " ".join(query_parts)
        if not semantic_query:
            semantic_query = "Xe tải thương mại xe van chở hàng"

        logger.info(
            f"HybridRetriever running queries for: '{semantic_query}'")

        # 2. Execute parallel DB retrievals (Vector + BM25)
        vector_results = search_vector_products(
            semantic_query, top_k=vector_limit)
        bm25_results = search_bm25_products(
            semantic_query, top_k=graph_limit)

        # 3. Merge results using Reciprocal Rank Fusion (RRF)
        merged_products = self._rrf_merge(
            vector_results, bm25_results, reqs=current_requirements, limit=top_k)

        # 4. Consultative fallback: if no exact matches found, search for alternative vehicle types (Van <-> Xe tải nhẹ)
        if not merged_products:
            logger.info(
                "No exact matches found. Searching for close alternative commercial vehicles...")
            relaxed_reqs = current_requirements.copy()
            if relaxed_reqs.get("vehicle_type") == "Van":
                relaxed_reqs["vehicle_type"] = "Xe tải nhẹ"
            elif relaxed_reqs.get("vehicle_type") == "Xe tải nhẹ":
                relaxed_reqs["vehicle_type"] = "Van"

            merged_products = self._rrf_merge(
                vector_results, bm25_results, reqs=relaxed_reqs, limit=top_k)
            for p in merged_products:
                p["is_alternative"] = True

        logger.info(
            f"HybridRetriever merged {len(merged_products)} products for recommendation.")
        return merged_products

    def _rrf_merge(self, vector_results: list, bm25_results: list, reqs: dict, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion (RRF) algorithm.
        Filters products strictly under hard constraints before ranking them.
        """
        rrf_constant = 60
        scores = {}
        product_pool = {}

        def passes_constraints(p: dict) -> bool:
            price = float(p.get("price", 0))
            payload = float(p.get("payload", 0))
            fuel = str(p.get("fuel_type", ""))
            vtype = str(p.get("vehicle_type", ""))

            # 1. Budget hard filter
            budget_max = reqs.get("budget_max", None)
            if budget_max is not None and price > float(budget_max):
                return False
            budget_min = reqs.get("budget_min", None)
            if budget_min is not None and price < float(budget_min):
                return False

            # 2. Fuel Type hard filter
            req_fuel = reqs.get("fuel_type")
            if req_fuel:
                if req_fuel.lower() == "xăng" and fuel.lower() != "xăng":
                    return False
                if req_fuel.lower() == "dầu" and fuel.lower() != "dầu":
                    return False
                if req_fuel.lower() == "điện" and fuel.lower() != "điện":
                    return False

            # 3. Vehicle Type hard filter
            req_vtype = reqs.get("vehicle_type")
            if req_vtype:
                if req_vtype.lower() == "van" and vtype.lower() != "van":
                    return False
                if req_vtype.lower() == "xe tải nhẹ" and vtype.lower() != "xe tải nhẹ":
                    return False
                if req_vtype.lower() == "xe tải nặng" and vtype.lower() != "xe tải nặng":
                    return False

            # 4. Payload hard filter
            payload_min = reqs.get("payload_min", None)
            if payload_min is not None and payload < float(payload_min):
                return False
            payload_max = reqs.get("payload_max", None)
            if payload_max is not None and payload > float(payload_max):
                return False

            return True

        # Process vector rankings with constraints check
        for rank, p in enumerate(vector_results):
            if not passes_constraints(p):
                continue
            pid = p["product_id"]
            product_pool[pid] = p
            scores[pid] = scores.get(pid, 0.0) + \
                (1.0 / (rrf_constant + rank + 1))

        # Process BM25 rankings with constraints check
        for rank, p in enumerate(bm25_results):
            if not passes_constraints(p):
                continue
            pid = p["product_id"]
            product_pool[pid] = p
            scores[pid] = scores.get(pid, 0.0) + \
                (1.0 / (rrf_constant + rank + 1))

        # Sort by final score
        sorted_pids = sorted(
            scores.keys(), key=lambda x: scores[x], reverse=True)

        final_results = []
        for pid in sorted_pids[:limit]:
            p = dict(product_pool[pid])
            p["rrf_score"] = float(scores[pid])
            final_results.append(p)

        return final_results


hybrid_retriever_agent = HybridRetrieverAgent()
