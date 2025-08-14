import asyncio
import threading
import websockets

questions = [
    "What is meant by the “spatial turn” in historiography, and why has it had limited influence on general histories of Europe?",
    "How do sociologists like Johann P. Arnason and Gerard Delanty define Europe’s mesoregional structure?",
    "What is the concept of a historical mesoregion, and how did Holm Sundhaussen and Stefan Troebst describe it?",
    "How have geographers used “culture areas” (Kulturräume) to divide Europe, and what are some examples of these divisions?",
    "How have multivolume histories of Europe typically handled (or failed to handle) mesoregionalization?",
    "In what ways did Soviet and Russian historiography approach the regionalization of Europe differently from Western traditions?",
    "Why are “the Balkans” and “Southeastern Europe” often treated as special or exceptional categories in European historiography?",
    "What were the reasons for the Second world war to happen?",
    "Tell me more about the number of people who were impacted by the nuclear bomb in japan",
    "What was hitler's role in Austria before he came to germany",
    "Did England use Indian soldiers in the WW2",
    "Whom did France support in the WW2"
]

# questions = [
#     "What are the main causes of climate change in Europe?",
#     "How did the European Union form and what are its key treaties?",
#     "Describe the impact of the Renaissance on European art and science.",
#     "What are the major linguistic families present in Europe?",
#     "How has migration shaped modern European societies?",
#     "Explain the significance of the Industrial Revolution in Europe."
# ]

async def send_questions(qs):
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        for q in qs:
            await websocket.send(q)
            print(f"Sent: {q}")
            # Optionally receive a response
            response = await websocket.recv()
            print(f"Received: {response}")

def thread_func(qs):
    asyncio.run(send_questions(qs))

if __name__ == "__main__":
    # Split questions between two threads
    mid = len(questions) // 2
    t1 = threading.Thread(target=thread_func, args=(questions[:mid],))
    t2 = threading.Thread(target=thread_func, args=(questions[mid:],))

    t1.start()
    t2.start()
    t1.join()
    t2.join()