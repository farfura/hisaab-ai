from typing import Any

from core.database import get_supabase, run_db
from utils.phone import normalize_phone


class UserService:
    async def get_or_create_by_phone(self, phone: str) -> dict[str, Any]:
        normalized = normalize_phone(phone)

        def _fetch() -> dict[str, Any]:
            db = get_supabase()
            existing = db.table("users").select("*").eq("phone", normalized).execute()
            if existing.data:
                return existing.data[0]
            created = db.table("users").insert({"phone": normalized}).execute()
            return created.data[0]

        return await run_db(_fetch)

    async def get_user_with_business(self, phone: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
        user = await self.get_or_create_by_phone(phone)
        business = None
        if user.get("active_business_id"):

            def _fetch_business() -> dict[str, Any] | None:
                db = get_supabase()
                biz = (
                    db.table("businesses")
                    .select("*")
                    .eq("id", user["active_business_id"])
                    .execute()
                )
                return biz.data[0] if biz.data else None

            business = await run_db(_fetch_business)
        return user, business

    async def complete_onboarding(
        self,
        user_id: str,
        business_name: str,
        category: str,
        mode: str,
        business_phone: str | None = None,
    ) -> dict[str, Any]:
        def _complete() -> dict[str, Any]:
            db = get_supabase()
            biz = (
                db.table("businesses")
                .insert(
                    {
                        "user_id": user_id,
                        "name": business_name,
                        "category": category,
                        "mode": mode,
                        "phone": business_phone,
                    }
                )
                .execute()
                .data[0]
            )
            db.table("users").update(
                {
                    "active_business_id": biz["id"],
                    "onboarding_complete": True,
                }
            ).eq("id", user_id).execute()
            return biz

        return await run_db(_complete)

    async def get_business_name(self, user: dict[str, Any]) -> str:
        if not user.get("active_business_id"):
            return "Aapka Business"

        def _fetch_name() -> str | None:
            db = get_supabase()
            biz = (
                db.table("businesses")
                .select("name")
                .eq("id", user["active_business_id"])
                .execute()
            )
            return biz.data[0]["name"] if biz.data else None

        name = await run_db(_fetch_name)
        return name or "Aapka Business"
