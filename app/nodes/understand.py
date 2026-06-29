import json
from langsmith import traceable
from app.llm_provider import call_llm
from app.prompts import UNDERSTAND_PROMPT
from app.database import get_schema_summary


@traceable(name="understand_query")
async def understand_node(state: dict) -> dict:
    schema = get_schema_summary()

    response = await call_llm(
        provider=state["provider"],
        model=state["model"],
        api_key=state["api_key"],
        system_prompt=UNDERSTAND_PROMPT.format(schema=schema),
        user_prompt=state["question"],
    )

    understanding = json.loads(response)

    return {
        **state,
        "understanding": understanding,
        "schema": schema,
    }
