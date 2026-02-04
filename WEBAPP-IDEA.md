create a webapp (use folder webapp) using Next.js and popular opensource css framework. (also create Makefile at project root so that run make dev will start all necessary services for webapp and include webapp)

the web is design like a terminal

the first time the web is run we will run claude to get a session ID
and save this session ID

subsequent run we will always use this session ID

all conversation history in the terminal will be save in ChromaDB or file based db
in folder filedb/

as RAG Vector DB

we can utilise ollama open source model to help with information retrieval and organization of knowledge

but the interaction with user will be using claude with the session ID

the web app should provide way for llm agent to visualize data

for example



chart(x: [values], y: [values]) ---> draw x-y 2D chart

table(headers: [values], rows[values]) --> draw a table

pie([{title, value}]) --> draw pie chart


you can follow similar pattern to make more way for llm agent to visualize data
