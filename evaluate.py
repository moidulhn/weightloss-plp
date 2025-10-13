# evaluate.py
import json
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from dotenv import load_dotenv

# Import the Gemini models for both LLM and embeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
load_dotenv()

# Load your evaluation data
with open('eval_data_full.json', 'r') as f:
    eval_data = json.load(f)

eval_dataset = Dataset.from_list(eval_data)

# --- Configure RAGAs to use only Gemini Models ---
gemini_llm_judge = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
gemini_embeddings_judge = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
metrics = [
    faithfulness,
    answer_relevancy,
]

# Run the evaluation using the specified Gemini models
print("Running Gemini-only RAGAs evaluation...")
result = evaluate(
    dataset=eval_dataset,
    metrics=metrics,
    llm=gemini_llm_judge,
    embeddings=gemini_embeddings_judge  
)

df = result.to_pandas()
print(df)

# Updated output filename for clarity
output_filename = "evaluation_results_gemini_full.csv"
df.to_csv(output_filename, index=False)
print(f"\nRAGAs evaluation complete. Results saved to '{output_filename}'.")