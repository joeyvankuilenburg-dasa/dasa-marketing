import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Create a session
session = client.beta.sessions.create(
    agent="your_agent_id",
    environment_id="your_environment_id",
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
        "content": [{"type": "text", "text": "Check the current time and publish the next scheduled post if we are within a posting window."}]
    }],
    betas=["managed-agents-2026-04-01"],
)

# Stream the output
with client.beta.sessions.events.stream(
    session_id=session.id,
    betas=["managed-agents-2026-04-01"],
) as stream:
    for event in stream:
        if hasattr(event, 'type'):
            if event.type == 'agent.message':
                for block in event.content:
                    if hasattr(block, 'text'):
                        print(block.text)
            elif event.type == 'session.status_terminated':
                break
            elif event.type == 'session.error':
                print(f"Error: {event}")
                break
