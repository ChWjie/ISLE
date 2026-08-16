"""
测试得理开放平台检索调用
"""
import asyncio
import json
import sys
from dotenv import load_dotenv

load_dotenv()

from app.services.delilegal_client import get_delilegal_client

DEFAULT_QUERIES = [
    "APP 未经同意调用位置权限 个人信息保护法",
    "向第三方广告平台共享用户信息 个人信息保护",
    "个人信息保护法 第17条 明示同意 数据共享",
]


def pick_items(raw: dict):
    if not isinstance(raw, dict):
        return []
    if isinstance(raw.get("data"), list):
        return raw["data"]
    if isinstance(raw.get("data"), dict):
        data = raw["data"]
        for key in ("records", "list", "items", "result", "rows"):
            if isinstance(data.get(key), list):
                return data[key]
    for key in ("records", "list", "items", "result", "rows"):
        if isinstance(raw.get(key), list):
            return raw[key]
    return []


async def probe_query(query: str):
    client = get_delilegal_client()
    print(f"\n=== QUERY ===\n{query}\n")
    print("=== CLIENT CONFIG ===")
    print(f"Base URL: {client.base_url}")
    print(f"App ID: {client.app_id[:6]}***")
    print(f"Law field: {client.law_field_name}")

    case_raw = await client.search_cases(query)
    law_raw = await client.search_laws(query)
    pack = await client.retrieve_pack(query)

    case_items = pick_items(case_raw)
    law_items = pick_items(law_raw)

    print("\n=== RAW CASE RESPONSE SUMMARY ===")
    print(json.dumps({
        "has_error": bool(case_raw.get("_error")) if isinstance(case_raw, dict) else True,
        "error": case_raw.get("_error") if isinstance(case_raw, dict) else "non-dict",
        "top_level_keys": list(case_raw.keys())[:10] if isinstance(case_raw, dict) else [],
        "picked_count": len(case_items),
        "sample_item_keys": list(case_items[0].keys())[:10] if case_items and isinstance(case_items[0], dict) else [],
    }, ensure_ascii=False, indent=2))

    print("\n=== RAW LAW RESPONSE SUMMARY ===")
    print(json.dumps({
        "has_error": bool(law_raw.get("_error")) if isinstance(law_raw, dict) else True,
        "error": law_raw.get("_error") if isinstance(law_raw, dict) else "non-dict",
        "top_level_keys": list(law_raw.keys())[:10] if isinstance(law_raw, dict) else [],
        "picked_count": len(law_items),
        "sample_item_keys": list(law_items[0].keys())[:10] if law_items and isinstance(law_items[0], dict) else [],
    }, ensure_ascii=False, indent=2))

    print("\n=== PACK SUMMARY ===")
    print(json.dumps({
        "degraded": pack.get("degraded"),
        "degraded_reason": pack.get("degraded_reason"),
        "case_count": len(pack.get("cases", [])),
        "law_count": len(pack.get("laws", [])),
        "source_map": pack.get("source_map", []),
    }, ensure_ascii=False, indent=2))

    if case_items:
        print("\n=== SAMPLE CASE ITEM ===")
        print(json.dumps(case_items[0], ensure_ascii=False, indent=2)[:1200])
    if law_items:
        print("\n=== SAMPLE LAW ITEM ===")
        print(json.dumps(law_items[0], ensure_ascii=False, indent=2)[:1200])

    await client.close()


async def main():
    query = " ".join(sys.argv[1:]).strip()
    if query:
        await probe_query(query)
        return

    for item in DEFAULT_QUERIES:
        await probe_query(item)


if __name__ == "__main__":
    asyncio.run(main())
