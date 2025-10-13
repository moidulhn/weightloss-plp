import json
from plp_engine import PLPSystem
from config import LEARNING_QUESTIONS # Import your questions

def generate_data():
    """
    Uses the PLPSystem to run a batch of questions and save the results
    for evaluation.
    """
    print("Initializing PLP System...")
    plp = PLPSystem()
    
    # Use the first 5 learning questions for evaluation
    eval_questions = LEARNING_QUESTIONS
    eval_results = []
    
    print(f"Generating answers for {len(eval_questions)} questions...")
    for i, question in enumerate(eval_questions):
        print(f"  Processing question {i+1}/{len(eval_questions)}: '{question[:50]}...'")
        response = plp.ask(question)
        
        # Extract the required data for RAGAs
        result = {
            "question": question,
            "answer": response.get("answer", ""),
            "contexts": [doc.page_content for doc in response.get("context", [])]
        }
        eval_results.append(result)
        
    # Save the results to a JSON file
    output_file = "eval_data_full.json"
    with open(output_file, 'w') as f:
        json.dump(eval_results, f, indent=4)
        
    print(f"\n Evaluation data successfully generated and saved to '{output_file}'.")

if __name__ == "__main__":
    generate_data()