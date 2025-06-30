# Chroma

> Chroma is the open-source AI application database.
> Chroma makes it easy to build LLM apps by making knowledge,
> facts, and skills pluggable for LLMs.

> Chroma can also be configured to run in client/server mode.
> In this mode, the Chroma client connects to a Chroma server
> running in a separate process.

> ChromaDB can be run in-memory using its EphemeralClient() method,
> making it suitable for temporary storage or testing. 
> This in-memory mode stores data in RAM and does not persist it when 
> the program or application is closed, so it's ideal for development 
> or scenarios where data doesn't need to be saved. 
> For persistent storage, ChromaDB offers options like the PersistentClient() 
> or running it in a client-server mode. 


## Referencs

> Chroma - the open-source embedding database.
> The fastest way to build Python or JavaScript LLM apps with memory!

- https://pypi.org/project/chromadb/
- https://github.com/chroma-core/chroma
- https://www.trychroma.com
- https://docs.trychroma.com/docs/overview/getting-started
- https://docs.trychroma.com/docs/overview/introduction
- https://docs.trychroma.com/production/chroma-server/client-server-mode
- https://docs.trychroma.com/production/containers/docker 

- https://pypistats.org/packages/chromadb

## Installation

```
$ pip install chromadb 
```

```
$ chroma run


                (((((((((    (((((####
             ((((((((((((((((((((((#########
           ((((((((((((((((((((((((###########
         ((((((((((((((((((((((((((############
        (((((((((((((((((((((((((((#############
        (((((((((((((((((((((((((((#############
         (((((((((((((((((((((((((##############
         ((((((((((((((((((((((((##############
           (((((((((((((((((((((#############
             ((((((((((((((((##############
                (((((((((    #########

Saving data to: ./chroma
Connect to Chroma at: http://localhost:8000
Getting started guide: https://docs.trychroma.com/docs/overview/getting-started

OpenTelemetry is not enabled because it is missing from the config.
Listening on localhost:8000
```

## Docker

Use this for client-server mode.

See https://docs.trychroma.com/production/chroma-server/client-server-mode

```
docker run -v ./chroma-data:/data -p 8000:8000 chromadb/chroma
```

Sync:

```
import chromadb
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
```

Async:

```
import asyncio
import chromadb

async def main():
    client = await chromadb.AsyncHttpClient()
    collection = await client.create_collection(name="my_collection")
    await collection.add(
        documents=["hello world"],
        ids=["id1"]
    )

asyncio.run(main())
```