import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

model_identifier = "urahara119/qazaqai"  # Replace with your actual model identifier

# Load model and tokenizer from Hugging Face
tokenizer = AutoTokenizer.from_pretrained(model_identifier)
model = AutoModelForQuestionAnswering.from_pretrained(model_identifier)
model.eval()

def get_model_answer(question: str, context: str):
    """Use the QA model to get an answer for the given question and context."""
    inputs = tokenizer(question, context, max_length=384, truncation=True, padding="max_length", return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    start_idx = torch.argmax(outputs.start_logits, dim=1).item()
    end_idx = torch.argmax(outputs.end_logits, dim=1).item()
    model_answer = tokenizer.decode(inputs["input_ids"][0][start_idx:end_idx + 1], skip_special_tokens=True)

    return model_answer.strip()
