curl -X POST http://127.0.0.1:8000/api/v1/get-clients -H "Content-Type: application/json" -d '{"session_token": "your_token_here"}'
curl -X POST http://127.0.0.1:8000/api/v1/get-client-config -H "Content-Type: application/json" -d '{ "session_token": "your_token_here", "config_name": "test2" }'
curl -X POST http://127.0.0.1:8000/api/v1/check-ip -H "Content-Type: application/json" -d '{ "session_token": "your_token_here", "name": "client1", "ip_address": "10.100.100.102" }'
curl -X POST http://127.0.0.1:8000/api/v1/add-client -H "Content-Type: application/json" -d '{ "session_token": "your_token_here", "name": "client1", "ip_address": "10.100.100.102" }'
