import asyncio
from services.ai_service import AIService

sample = (
    "Alice: We need to finalize the UI designs by next Tuesday. "
    "Bob: I'll deliver the testing results by Friday. "
    "Charlie: I can prepare the demo slides for the client presentation. "
    "Team: The release date will have to move to next month due to backend API delays. "
    "Alice: That means we reschedule the client handoff. "
    "Bob: Agreed, shifting the release. "
    "Charlie: I'll adjust the presentation accordingly."
)

async def main():
    print("Testing AIService...")
    svc = AIService()
    print(f"Model loaded: {svc.model_name}")
    
    result = await svc.process_transcript(sample)
    import json
    print("\n=== RESULT ===")
    print(json.dumps(result, indent=2))
    
    # Verify structure matches expected output
    expected_keys = {"summary", "decisions", "agenda", "participants", "topics", "actionItems", "processed_at", "model_used"}
    actual_keys = set(result.keys())
    print(f"\n=== STRUCTURE CHECK ===")
    print(f"Expected keys: {expected_keys}")
    print(f"Actual keys: {actual_keys}")
    print(f"Missing keys: {expected_keys - actual_keys}")
    print(f"Extra keys: {actual_keys - expected_keys}")

if __name__ == "__main__":
    asyncio.run(main())
