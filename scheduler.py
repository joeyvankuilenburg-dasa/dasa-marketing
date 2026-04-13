import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Create a session
session = client.beta.sessions.create(
    agent="agent_011CZsidNP8yM3LsnPSfx9wV",
    environment_id="env_01YaA6CpUPdzdqrHzVj3QYLS",
    resources=[{
        "type": "github_repository",
        "url": "https://github.com/joeyvankuilenburg-dasa/dasa-marketing",
        "authorization_token": os.environ["GITHUB_TOKEN"],
        "mount_path": "/workspace/posts",
        "checkout": {"type": "branch", "name": "main"}
    }],
    betas=["managed-agents-2026-04-01"],
)

print(f"Session created: {session.id}")

# Send the trigger message
client.beta.sessions.events.send(
    session_id=session.id,
    events=[{
        "type": "user.message",
        "content": [{"type": "text", "text": f"GITHUB_TOKEN={os.environ['GITHUB_TOKEN']}\n\nCheck the current time and publish the next scheduled post if we are within a posting window."}]
    }],
    betas=["managed-agents-2026-04-01"],
)

print("Message sent, waiting for response...")

# Poll for events instead of streaming
import time
last_id = None
deadline = time.time() + 300  # 5 minute timeout

while time.time() < deadline:
    events = client.beta.sessions.events.list(
        session_id=session.id,
        after_id=last_id,
        betas=["managed-agents-2026-04-01"],
    )
    
    for event in events.data:
        last_id = event.id
        print(f"Event: {event.type}")
        if event.type == 'agent.message':
            for block in event.content:
                if hasattr(block, 'text'):
                    print(block.text)
        elif event.type == 'session.status_terminated':
            print("Session terminated.")
            exit(0)
        elif event.type == 'session.error':
            print(f"Session error: {event}")
            exit(1)
    
    time.sleep(5)

print("Timeout reached.")
