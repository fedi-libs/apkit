# apkit examples

This guide demonstrates how to use apkit to interact with other servers on
the Fediverse using the ActivityPub protocol. The example shows how to send a
message (Note) to another user using federation.

## Prerequisites

1. Python 3.11 or higher
2. Virtual environment (recommended)
3. ngrok installed (for local testing)
4. A Fediverse account to send messages to (<https://activitypub.academy> is a
   great place for experiments with temporary Mastodon accounts)

## Installation

1. Clone the repository and set up the environment:

```shell
# Clone the repository
git clone https://github.com/fedi-libs/apkit.git
cd apkit/examples

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install apkit[server]
```

1. Set up ngrok for local testing:

```shell
# Start ngrok on port 8000
ngrok http 8000
```

Save the ngrok URL (e.g., "12f8-197-211-61-33.ngrok-free.app") for configuration.

## Configuration

Set an environment variable:

```shell
export APKIT_DOMAIN=12f8-197-211-61-33.ngrok-free.app    # Your ngrok URL (without https://)
```

## Start the minimal server

Start the minimal server:

```shell
uvicorn --host=0.0.0.0 --port 8000 minimal_server:app
```

The server will handle node information, actor information and key management
automatically. It will also receive and validate requests to the inbox.

## Running the Example

Make sure that both ngrok and the minimal server are running.

Now you can try the various example actions:

### Send a message

```shell
python send_message.py alice@social.example.com   # <<< change this to your Fediverse account name
```

### Follow an account

```shell
python folow.py alice@social.example.com   # <<< change this to the account you want to follow
```

### Like a message

```shell
python like.py https://example.com/notes/fff17d24-9080-4c95-a406-1668b190c6c7  # <<< change this to a real URI
```

### Delete a message

```shell
python delete.py https://example.com/notes/fff17d24-9080-4c95-a406-1668b190c6c7  # <<< change this to a real URI
```
