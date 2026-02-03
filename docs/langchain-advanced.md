# LangChain 高级特性 - VectorStore 和 Callbacks

## 📋 概述

LangChain 提供了许多高级特性，包括向量存储、回调函数、索引等，用于构建更强大的 AI 应用。

## 🧠 VectorStore（向量存储）

### 基本概念

向量存储用于存储和检索文本的嵌入向量，实现语义搜索和 RAG（检索增强生成）。

### 支持的向量数据库

| 数据库 | 安装 | 特点 |
|-------|------|------|
| ChromaDB | `pip install chromadb` | 轻量，本地运行 |
| FAISS | `pip install faiss-cpu` | 高性能，Meta 开源 |
| Pinecone | `pip install pinecone-client` | 云端，可扩展 |
| Weaviate | `pip install weaviate-client` | 开源，支持过滤 |
| Qdrant | `pip install qdrant-client` | 高性能，易于部署 |
| Milvus | `pip install pymilvus` | 开源，企业级 |

### ChromaDB 示例

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 初始化嵌入模型
embeddings = OpenAIEmbeddings()

# 示例文本
texts = [
    "Python 是一种高级编程语言",
    "LangChain 是一个用于开发 LLM 应用的框架",
    "向量存储用于实现语义搜索",
    "机器学习是人工智能的一个分支"
]

# 创建向量存储
vectorstore = Chroma.from_texts(texts, embeddings)

# 相似度搜索
query = "什么是 LangChain？"
results = vectorstore.similarity_search(query, k=2)

for i, doc in enumerate(results):
    print(f"Result {i+1}: {doc.page_content}")
    print(f"Score: {doc.metadata.get('score', 'N/A')}")
    print()
```

### 持久化向量存储

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# 创建并持久化
vectorstore = Chroma.from_documents(
    documents,
    OpenAIEmbeddings(),
    persist_directory="./chroma_db"
)

# 加载已存储的向量数据库
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=OpenAIEmbeddings()
)

# 搜索
results = vectorstore.similarity_search("查询内容")
```

### 文档加载和分块

```python
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 加载文档
loader = TextLoader("large_document.txt")
documents = loader.load()

# 分块
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # 每块 1000 字符
    chunk_overlap=200,    # 重叠 200 字符
    length_function=len
)

splits = text_splitter.split_documents(documents)

# 创建向量存储
vectorstore = Chroma.from_documents(splits, OpenAIEmbeddings())
```

### 相似度搜索类型

```python
from langchain.vectorstores import Chroma

# 1. 相似度搜索
results = vectorstore.similarity_search(query, k=3)

# 2. 相似度搜索（带分数）
results = vectorstore.similarity_search_with_score(query, k=3)
for doc, score in results:
    print(f"Score: {score:.4f} - {doc.page_content}")

# 3. 最大边际相关性（MMR）搜索
# 返回多样化结果，避免重复
results = vectorstore.max_marginal_relevance_search(
    query,
    k=3,
    fetch_k=10  # 从前 10 个结果中选择 3 个最多样化的
)

# 4. 按分数过滤
results = vectorstore.similarity_search_with_relevance_scores(
    query,
    score_threshold=0.7  # 只返回分数 >= 0.7 的结果
)
```

### 元数据过滤

```python
# 创建带元数据的文档
documents = [
    Document(page_content="Python 基础教程", metadata={"category": "python", "level": "beginner"}),
    Document(page_content="Python 高级技巧", metadata={"category": "python", "level": "advanced"}),
    Document(page_content="JavaScript 基础", metadata={"category": "javascript", "level": "beginner"}),
]

vectorstore = Chroma.from_documents(documents, embeddings)

# 过滤搜索
results = vectorstore.similarity_search(
    "编程教程",
    k=2,
    filter={"category": "python"}
)
```

### FAISS 示例

```python
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# 创建 FAISS 索引
vectorstore = FAISS.from_documents(documents, embeddings)

# 保存索引
vectorstore.save_local("faiss_index")

# 加载索引
vectorstore = FAISS.load_local("faiss_index", embeddings)

# 搜索
results = vectorstore.similarity_search(query)
```

### Pinecone 示例

```python
import pinecone
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings

# 初始化 Pinecone
pinecone.init(
    api_key="your-api-key",
    environment="us-east-1-aws"
)

# 创建索引
index_name = "my-index"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        dimension=1536,  # OpenAI 嵌入维度
        metric="cosine"
    )

# 创建向量存储
vectorstore = Pinecone.from_documents(
    documents,
    OpenAIEmbeddings(),
    index_name=index_name
)

# 搜索
results = vectorstore.similarity_search(query, k=5)
```

## 🔔 Callbacks（回调函数）

### 基本概念

回调函数用于在 LangChain 执行过程中监听和处理事件，如日志记录、性能监控、错误处理等。

### 内置回调处理器

```python
from langchain.callbacks import StdOutCallbackHandler

# 标准输出回调
handler = StdOutCallbackHandler()

# 使用回调
chain = LLMChain(llm=llm, prompt=prompt, callbacks=[handler])
chain.run("Hello")
```

### 自定义回调处理器

```python
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List, Optional

class MyCustomHandler(BaseCallbackHandler):
    def __init__(self):
        self.token_count = 0
        self.start_time = None

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any
    ) -> Any:
        """当 LLM 开始生成时调用"""
        print(f"\n{'='*50}")
        print(f"LLM Start - Prompts: {prompts}")
        self.start_time = time.time()

    def on_llm_new_token(
        self,
        token: str,
        **kwargs: Any
    ) -> Any:
        """每当生成新 token 时调用"""
        self.token_count += 1
        print(token, end="", flush=True)

    def on_llm_end(
        self,
        response: Any,
        **kwargs: Any
    ) -> Any:
        """当 LLM 完成生成时调用"""
        duration = time.time() - self.start_time
        print(f"\n{'='*50}")
        print(f"LLM End - Tokens: {self.token_count}, Time: {duration:.2f}s")
        print(f"Speed: {self.token_count / duration:.2f} tokens/s")

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any
    ) -> Any:
        """当链开始执行时调用"""
        print(f"\n[Chain Start] {serialized.get('id', ['unknown'])[0]}")

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        **kwargs: Any
    ) -> Any:
        """当链完成执行时调用"""
        print(f"[Chain End] Output: {outputs}")

    def on_chain_error(
        self,
        error: Exception,
        **kwargs: Any
    ) -> Any:
        """当链执行出错时调用"""
        print(f"[Chain Error] {error}")

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any
    ) -> Any:
        """当工具开始执行时调用"""
        print(f"[Tool Start] {serialized['name']}: {input_str}")

    def on_tool_end(
        self,
        output: str,
        **kwargs: Any
    ) -> Any:
        """当工具完成执行时调用"""
        print(f"[Tool End] Result: {output}")

    def on_agent_action(
        self,
        action: Any,
        **kwargs: Any
    ) -> Any:
        """当 Agent 执行动作时调用"""
        print(f"[Agent Action] {action.tool}: {action.tool_input}")
```

### 使用自定义回调

```python
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType

# 初始化
handler = MyCustomHandler()
llm = ChatOpenAI(temperature=0, callbacks=[handler])

# 创建 Agent
tools = [
    Tool(
        name="Calculator",
        func=lambda x: str(eval(x)),
        description="Useful for math calculations"
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True
)

# 运行 Agent
agent.run("What is 123 * 456?")
```

### LangSmith 回调

```python
from langchain.callbacks.tracers import LangChainTracer
from langchain.smith import LangSmith

# 初始化 LangSmith
tracer = LangChainTracer(
    project_name="my-project",
    client=LangSmith(
        api_key="your-api-key",
        api_url="https://api.smith.langchain.com"
    )
)

# 使用回调
chain = LLMChain(llm=llm, prompt=prompt, callbacks=[tracer])
result = chain.run("Hello")

# 查看执行详情在 https://smith.langchain.com
```

### 流式输出回调

```python
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# 流式输出到标准输出
llm = ChatOpenAI(
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

result = llm.predict("Tell me a story")
```

### 自定义流式回调

```python
from typing import Any, Dict
from langchain.callbacks.base import BaseCallbackHandler

class TokenCollector(BaseCallbackHandler):
    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        self.tokens.append(token)

# 使用
collector = TokenCollector()
llm = ChatOpenAI(streaming=True, callbacks=[collector])

result = llm.predict("Hello")
print(f"All tokens: {collector.tokens}")
```

### 组合多个回调

```python
from langchain.callbacks import get_openai_callback

# OpenAI 调用统计回调
with get_openai_callback() as cb:
    result = chain.run("Hello")

    print(f"Total Tokens: {cb.total_tokens}")
    print(f"Prompt Tokens: {cb.prompt_tokens}")
    print(f"Completion Tokens: {cb.completion_tokens}")
    print(f"Total Cost (USD): ${cb.total_cost:.4f}")
```

### 异步回调

```python
from langchain.callbacks.base import AsyncCallbackHandler

class AsyncTokenHandler(AsyncCallbackHandler):
    async def on_llm_new_token(self, token: str, **kwargs) -> Any:
        # 异步处理 token
        await self.send_to_websocket(token)

    async def send_to_websocket(self, token: str):
        # 发送到 WebSocket
        pass

# 使用
handler = AsyncTokenHandler()
llm = ChatOpenAI(streaming=True, callbacks=[handler])
result = await llm.apredict("Hello")
```

## 🎯 实际应用示例

### RAG（检索增强生成）

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# 1. 加载文档
loader = TextLoader("knowledge_base.txt")
documents = loader.load()

# 2. 分块
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(documents)

# 3. 创建向量存储
vectorstore = Chroma.from_documents(splits, OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 4. 创建 RAG 链
llm = ChatOpenAI(temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# 5. 查询
query = "什么是 LangChain？"
result = qa_chain({"query": query})

print(f"Answer: {result['result']}")
print(f"\nSources:")
for doc in result["source_documents"]:
    print(f"- {doc.page_content[:100]}...")
```

### 带回调的 RAG

```python
from langchain.callbacks.base import BaseCallbackHandler

class RAGCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.retrieved_docs = []
        self.generated_tokens = []

    def on_retriever_start(self, query: str, **kwargs):
        print(f"\n🔍 Retrieving documents for: {query}")

    def on_retriever_end(self, documents, **kwargs):
        self.retrieved_docs = documents
        print(f"📚 Retrieved {len(documents)} documents")

    def on_llm_new_token(self, token: str, **kwargs):
        self.generated_tokens.append(token)
        print(token, end="", flush=True)

# 使用
handler = RAGCallbackHandler()
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(streaming=True, callbacks=[handler]),
    chain_type="stuff",
    retriever=retriever
)

result = qa_chain.run("查询内容")
```

## 📊 性能监控

```python
from langchain.callbacks import get_openai_callback
import time

# 监控性能和成本
with get_openai_callback() as cb:
    start_time = time.time()

    result = chain.run("复杂查询")

    duration = time.time() - start_time

    print(f"\n{'='*40}")
    print(f"Performance Report")
    print(f"{'='*40}")
    print(f"Duration: {duration:.2f}s")
    print(f"Total Tokens: {cb.total_tokens}")
    print(f"Prompt Tokens: {cb.prompt_tokens}")
    print(f"Completion Tokens: {cb.completion_tokens}")
    print(f"Total Cost: ${cb.total_cost:.4f}")
    print(f"Tokens/Second: {cb.total_tokens/duration:.2f}")
```

---

**更新时间**: 2026-02-03
