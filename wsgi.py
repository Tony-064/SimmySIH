from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configure Gemini API endpoint
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def is_health_related(query):
    # Common diseases and conditions
    diseases = [
        'dengue', 'malaria', 'typhoid', 'cholera', 'tuberculosis', 'tb',
        'diabetes', 'cancer', 'hiv', 'aids', 'hepatitis', 'pneumonia',
        'asthma', 'bronchitis', 'arthritis', 'hypertension', 'bp',
        'heart disease', 'stroke', 'alzheimer', 'parkinson', 'epilepsy',
        'depression', 'anxiety', 'schizophrenia', 'ocd', 'autism',
        'influenza', 'measles', 'mumps', 'chickenpox', 'smallpox',
        'polio', 'rabies', 'tetanus', 'diphtheria', 'whooping cough',
        'meningitis', 'sepsis', 'ebola', 'zika', 'sars', 'covid',
        'coronavirus', 'flu', 'cold', 'fever', 'infection'
    ]
    
    # Symptoms and conditions
    symptoms = [
        'pain', 'ache', 'fever', 'cough', 'cold', 'rash', 'swelling',
        'inflammation', 'nausea', 'vomiting', 'diarrhea', 'constipation',
        'bleeding', 'bruising', 'dizziness', 'fatigue', 'weakness',
        'headache', 'migraine', 'backache', 'stomachache', 'sore throat',
        'runny nose', 'congestion', 'chest pain', 'shortness of breath',
        'wheezing', 'sneezing', 'itching', 'burning', 'numbness'
    ]
    
    # Medical terms and healthcare
    medical_terms = [
        'disease', 'syndrome', 'disorder', 'condition', 'illness',
        'treatment', 'medicine', 'medication', 'therapy', 'surgery',
        'doctor', 'hospital', 'clinic', 'pharmacy', 'prescription',
        'diagnosis', 'prognosis', 'vaccination', 'immunization',
        'prevention', 'cure', 'remedy', 'health', 'medical', 'emergency'
    ]
    
    # Combine all keywords
    health_keywords = diseases + symptoms + medical_terms
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in health_keywords)

def format_health_response(response_text):
    sections = {
        "Possible Causes": {"color": "bg-red-500", "items": []},
        "Prevention": {"color": "bg-blue-500", "items": []},
        "Home Remedies": {"color": "bg-green-500", "items": []},
        "Basic Medications": {"color": "bg-purple-500", "items": []},
        "When to See a Doctor": {"color": "bg-yellow-500", "items": []},
        "Disclaimer": {"color": "bg-gray-500", "items": []}
    }
    
    current_section = None
    lines = response_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a section header (more flexible matching)
        for section in sections.keys():
            if section.lower() in line.lower():
                current_section = section
                break
        else:
            # If no section header found, add content to current section
            if current_section and line:
                # Clean up bullet points and formatting
                line = line.lstrip('•-*').strip()
                if line:
                    sections[current_section]["items"].append(line)
    
    # Format the response as HTML with Tailwind CSS classes
    html_parts = []
    for section, data in sections.items():
        if data["items"]:
            # Section header with colorful background
            html_parts.append(f'<div class="mb-4">')
            html_parts.append(f'<h3 class="text-white font-bold py-2 px-4 rounded-lg {data["color"]} mb-2">{section}</h3>')
            # Section content
            html_parts.append('<ul class="space-y-2 pl-4">')
            for item in data["items"]:
                html_parts.append(f'<li class="flex items-start">')
                html_parts.append(f'<span class="text-gray-600 mr-2">•</span>')
                html_parts.append(f'<span class="text-gray-800">{item}</span>')
                html_parts.append('</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')
    
    # Add default disclaimer if none provided
    if not sections["Disclaimer"]["items"]:
        sections["Disclaimer"]["items"].append("This information is for general knowledge and does not constitute medical advice. Always consult a healthcare professional for diagnosis and treatment of any medical condition.")
    
    return "\n".join(html_parts)

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('query')
        if not user_message:
            return jsonify({"response": "No message received"}), 400
        
        # Check if the query is health-related
        if not is_health_related(user_message):
            return jsonify({
                "response": "I am a healthcare assistant. I can only help you with health-related questions. Please ask me about medical conditions, symptoms, treatments, or general health advice."
            }), 200
            
        # Create a comprehensive medical prompt
        prompt = f"""As a medical expert, provide detailed information about {user_message}. If this is a disease or medical condition, include:

        Possible Causes:
        - List the main causes and risk factors
        - Explain how it spreads or develops
        
        Prevention:
        - List specific preventive measures
        - Include lifestyle recommendations
        - Mention any available vaccines
        
        Home Remedies:
        - Safe home care methods
        - Dietary recommendations
        - Lifestyle adjustments
        
        Basic Medications:
        - Common treatment approaches
        - Types of medications typically prescribed
        - Important medication precautions
        
        When to See a Doctor:
        - Warning signs and symptoms
        - Emergency symptoms
        - High-risk situations
        
        Disclaimer:
        - Include standard medical disclaimer
        - Emphasize importance of professional medical advice

        Keep the information accurate, evidence-based, and easy to understand. If this is a serious condition, emphasize the importance of seeking professional medical care."""

        # Prepare request to Gemini API
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": api_key
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        # Make request to Gemini API
        response = requests.post(
            GEMINI_API_ENDPOINT,
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            print(f"Gemini API error: {response.status_code} - {response.text}")
            return jsonify({
                "response": "Sorry, there was an error getting a response from the AI.",
                "error": f"API Error {response.status_code}"
            }), 500
            
        # Extract and format answer from response
        response_data = response.json()
        raw_answer = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "")
        
        if not raw_answer:
            return jsonify({
                "response": "Sorry, I couldn't generate a response. Please try rephrasing your question."
            }), 500
            
        # Format the response as HTML
        formatted_html = format_health_response(raw_answer)
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "response": "Sorry, there was an error processing your request. Please try again.",
            "error": str(e)
        }), 500
    
    return jsonify({"html": formatted_html})

# Serve React build
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# React Router fallback
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")

# Health check (Render uses this)
@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)