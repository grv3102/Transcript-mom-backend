import asyncio
import json
from services.ai_service import AIService

# Enhanced test sample with more realistic meeting content
sample = """
Alice: Good morning everyone. Let's start today's project status meeting.
Bob: Thanks Alice. I've completed the user authentication module and it's ready for testing.
Charlie: Great! I'll handle the testing for Bob's module. I should have results by Friday.
Alice: Perfect. What about the database optimization work?
Bob: I'm planning to start that next week. Should take about 3 days to complete.
Charlie: I've identified some performance bottlenecks in the API layer. We need to address them before the release.
Alice: Good point Charlie. Let's prioritize the API fixes. Bob, can you help Charlie with that?
Bob: Absolutely. I'll work with Charlie on the API optimization starting tomorrow.
Alice: Excellent. One more thing - the client wants to move the release date to the 15th of next month.
Charlie: That gives us more time. I think we can deliver a more polished product.
Bob: Agreed. The extra time will help us address the performance issues properly.
Alice: Great! So our action items are: Bob completes database optimization, Charlie provides test results by Friday, and Bob helps with API optimization.
"""

async def main():
    print("=" * 60)
    print("Testing Optimized AIService with OpenAI Integration")
    print("=" * 60)
    
    try:
        # Initialize service
        svc = AIService()
        print(f"✅ AI Service initialized successfully")
        print(f"📊 Model: {svc.model_name}")
        print(f"🔗 Provider: {svc.provider}")
        print(f"🔑 API Key: {'Present' if svc.api_key else 'Missing'}")
        
        # Test health check
        print("\n" + "-" * 40)
        print("Health Check Test")
        print("-" * 40)
        health = svc.health_check()
        print(f"Status: {health.get('status', 'unknown')}")
        print(f"Timestamp: {health.get('timestamp', 'unknown')}")
        
        # Test transcript processing
        print("\n" + "-" * 40)
        print("Processing Test Transcript...")
        print("-" * 40)
        print(f"Input length: {len(sample)} characters")
        
        result = await svc.process_transcript(sample)
        
        print("\n" + "=" * 60)
        print("PROCESSING RESULTS")
        print("=" * 60)
        
        # Pretty print the result
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Verify structure matches expected output
        print("\n" + "-" * 40)
        print("Structure Validation")
        print("-" * 40)
        
        expected_keys = {
            "summary", "decisions", "agenda", "participants", 
            "topics", "actionItems", "processed_at", "model_used"
        }
        
        actual_keys = set(result.keys())
        
        print(f"✅ Expected keys: {sorted(expected_keys)}")
        print(f"✅ Actual keys: {sorted(actual_keys)}")
        
        missing_keys = expected_keys - actual_keys
        extra_keys = actual_keys - expected_keys
        
        if missing_keys:
            print(f"❌ Missing keys: {missing_keys}")
        else:
            print("✅ All required keys present")
            
        if extra_keys:
            print(f"ℹ️  Extra keys: {extra_keys}")
        
        # Validate data quality
        print("\n" + "-" * 40)
        print("Data Quality Check")
        print("-" * 40)
        
        participants = result.get('participants', [])
        action_items = result.get('actionItems', [])
        decisions = result.get('decisions', [])
        
        print(f"📝 Participants found: {len(participants)}")
        print(f"✅ Action items found: {len(action_items)}")
        print(f"🎯 Decisions found: {len(decisions)}")
        
        # Check for participant name quality
        if participants:
            print(f"👥 Participant names: {', '.join(participants)}")
            
        # Check action items structure
        if action_items:
            print("📋 Action Items:")
            for i, item in enumerate(action_items, 1):
                print(f"   {i}. {item.get('task', 'N/A')} (Owner: {item.get('owner', 'N/A')})")
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())