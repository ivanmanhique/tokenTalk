# test_chat_step3.sh - Test the chat interface

echo "🧪 Testing StoneWatch Chat Interface..."

# Test 1: Chat suggestions
echo "1️⃣ Getting chat suggestions:"
curl -s http://localhost:8000/api/chat/suggestions | python -m json.tool

echo -e "\n"

# Test 2: Test parsing without creating alerts
echo "2️⃣ Testing message parsing:"

# Test valid messages
curl -s -X POST "http://localhost:8000/api/chat/test-parsing?message=Alert%20me%20when%20ETH%20hits%20$4000" | python -m json.tool

echo -e "\n"

curl -s -X POST "http://localhost:8000/api/chat/test-parsing?message=BTC%20drops%20below%20$90000" | python -m json.tool

echo -e "\n"

# Test invalid message
curl -s -X POST "http://localhost:8000/api/chat/test-parsing?message=Hello%20there" | python -m json.tool

echo -e "\n"

# Test 3: Send actual chat message (creates alert)
echo "3️⃣ Sending real chat message:"
curl -s -X POST "http://localhost:8000/api/chat/message?message=Alert%20me%20when%20ETH%20hits%20$4000&user_id=test_user" | python -m json.tool

echo -e "\n"

# Test 4: Get conversation history
echo "4️⃣ Getting conversation history:"
curl -s "http://localhost:8000/api/chat/conversation/test_user" | python -m json.tool

echo -e "\n"

# Test 5: Verify alert was created
echo "5️⃣ Verifying alert was created:"
curl -s "http://localhost:8000/api/alerts/?user_id=test_user" | python -m json.tool

echo -e "\n✅ Chat interface tests completed!"

# Expected results:
# 1. Suggestions should return example messages
# 2. Valid messages should parse successfully 
# 3. Invalid messages should return null for parsed_condition
# 4. Real messages should create alerts
# 5. Conversation history should show the chat
# 6. Alerts API should show the created alert