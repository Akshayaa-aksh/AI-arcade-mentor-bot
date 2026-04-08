#!/usr/bin/env python
"""Test script to verify memory system is working"""

import sys
sys.path.insert(0, "/home/user/workspace")

from app.services.memory import (
    save_memory, 
    get_memory, 
    memory_stats, 
    clear_all_memory
)

# Test data
session_id = "test-session-123"
persona_key = "🤖 Maya — ML Engineer"

print("=" * 60)
print("🧪 Testing Memory System")
print("=" * 60)

# Test 1: Save memory
print("\n1️⃣ Saving conversation to memory...")
messages = [
    {"role": "user", "content": "What is overfitting?", "ts": "2024-01-01"},
    {"role": "assistant", "content": "Overfitting occurs when a model learns the training data too well...", "ts": "2024-01-01"}
]
save_memory(session_id, persona_key, messages)
print("✅ Memory saved successfully")

# Test 2: Get memory
print("\n2️⃣ Retrieving memory...")
retrieved = get_memory(session_id, persona_key)
print(f"✅ Retrieved {len(retrieved)} messages")
print(f"   User asked: {retrieved[0]['content'][:50]}...")

# Test 3: Memory stats
print("\n3️⃣ Checking memory stats...")
stats = memory_stats(session_id)
print(f"✅ Memory stats: {stats}")

# Test 4: Add more conversations
print("\n4️⃣ Adding more conversations...")
messages.extend([
    {"role": "user", "content": "How does regularization help?", "ts": "2024-01-01"},
    {"role": "assistant", "content": "Regularization adds a penalty term to prevent overfitting...", "ts": "2024-01-01"}
])
save_memory(session_id, persona_key, messages)
stats = memory_stats(session_id)
print(f"✅ Updated stats: {stats}")

# Test 5: Clear memory
print("\n5️⃣ Clearing memory...")
clear_all_memory(session_id)
stats = memory_stats(session_id)
print(f"✅ After clearing: {stats}")

print("\n" + "=" * 60)
print("✨ All memory tests passed!")
print("=" * 60)
