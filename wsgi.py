from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# Get API key and validate
api_key = os.getenv('GEMINI_API_KEY')
print("API Key Status:", "Present" if api_key else "Missing")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Verify API key format (basic check)
if not api_key.startswith('AIza'):
    print("WARNING: API key doesn't match expected format")
    
print("Initialization: API key validated")

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
        "⚠️ Causes": {"color": "text-red-600", "important": True, "items": []},
        "Prevention": {"color": "text-blue-600", "important": False, "items": []},
        "Home Care": {"color": "text-blue-600", "important": False, "items": []},
        "Medications": {"color": "text-blue-600", "important": False, "items": []},
        "⚠️ Warning Signs": {"color": "text-red-600", "important": True, "items": []},
        "Note": {"color": "text-blue-600", "important": False, "items": []}
    }
    
    current_section = None
    lines = response_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a section header (more flexible matching)
        for section in sections.keys():
            if any(s.lower() in line.lower() for s in [
                "cause" if section == "⚠️ Causes" else
                "warning" if section == "⚠️ Warning Signs" else
                section.lower()
            ]):
                current_section = section
                break
        else:
            # If no section header found, add content to current section
            if current_section and line:
                # Clean up bullet points and formatting
                line = line.lstrip('•-*').strip()
                if line and len(line) > 3:  # Skip very short lines
                    sections[current_section]["items"].append(line)
    
    # Format the response as HTML with Tailwind CSS classes
    html_parts = []
    for section, data in sections.items():
        if data["items"]:
            # Section header with colored text
            html_parts.append(f'<div class="mb-3">')  # Reduced margin
            html_parts.append(f'<h3 class="font-bold {data["color"]} text-lg mb-1">{section}</h3>')  # Colored text
            # Section content - more compact
            html_parts.append('<ul class="space-y-1 pl-3">')  # Reduced spacing and padding
            for item in data["items"]:
                html_parts.append(f'<li class="flex items-start text-sm">')  # Smaller text
                html_parts.append(f'<span class="mr-1">•</span>')  # Smaller bullet margin
                html_parts.append(f'<span>{item}</span>')
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
        # Validate request data
        if not request.is_json:
            return jsonify({"response": "Request must be JSON", "error": "Invalid content type"}), 400
            
        user_message = request.json.get('query')
        if not user_message:
            return jsonify({"response": "No message received", "error": "Missing query"}), 400
        
        # Check if API key is available
        if not api_key:
            return jsonify({"response": "API key not configured", "error": "Missing API key"}), 500
            
        # Check if the query is health-related
        if not is_health_related(user_message):
            return jsonify({
                "response": "I am a healthcare assistant. I can only help you with health-related questions. Please ask me about medical conditions, symptoms, treatments, or general health advice."
            }), 200
            
        # Create a concise medical prompt with error handling guidance
        prompt = f"""As a medical expert, provide brief, clear information about {user_message}. Structure your response with these sections:

        Causes:
        - List only the most common causes (2-3 points)
        
        Prevention:
        - Key preventive measures (2-3 points)
        
        Home Care:
        - Essential self-care tips (2-3 points)
        
        Medications:
        - Main treatment approaches (1-2 points)
        
        Warning Signs:
        - Critical symptoms requiring medical attention (2-3 points)
        
        Note:
        - Brief medical disclaimer

        Keep each point concise and focused. Use simple language. For serious conditions, emphasize the importance of medical care.
        
        If you cannot provide accurate information about this condition, respond with 'NO_INFORMATION' and I will handle the error appropriately."""

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
        
        # Log request details (without API key)
        print(f"\nRequest Details:")
        print(f"Endpoint: {GEMINI_API_ENDPOINT}")
        print(f"Request Data: {json.dumps(data, indent=2)}")
        
        # Make request to Gemini API with timeout and error handling
        try:
            print("\nMaking API request...")
            response = requests.post(
                GEMINI_API_ENDPOINT,
                headers=headers,
                json=data,
                timeout=15  # Increased timeout to 15 seconds
            )
            print(f"Response received. Status: {response.status_code}")
            
        except requests.exceptions.Timeout:
            print("ERROR: API request timed out after 15 seconds")
            return jsonify({
                "response": "The AI service is taking too long to respond. Please try again in a moment.",
                "error": "Request timeout"
            }), 504
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR: API request failed: {str(e)}")
            error_details = str(e)
            if "Failed to establish a new connection" in error_details:
                return jsonify({
                    "response": "Unable to connect to the AI service. Please check your internet connection and try again.",
                    "error": "Connection failed"
                }), 503
            elif "SSLError" in error_details:
                return jsonify({
                    "response": "Secure connection to the AI service failed. This might be a temporary issue.",
                    "error": "SSL Error"
                }), 503
            else:
                return jsonify({
                    "response": "There was a problem connecting to the AI service. Please try again.",
                    "error": error_details
                }), 503
            
        # Print response details for debugging
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Headers: {response.headers}")
        print(f"API Response Content: {response.text[:500]}...")  # First 500 chars
        
        # Check response status and parse response
        try:
            print("\nParsing API response...")
            
            if response.status_code != 200:
                error_message = f"Gemini API error: {response.status_code}"
                try:
                    error_details = response.json()
                    api_error = error_details.get('error', {})
                    error_message = f"API Error: {api_error.get('message', 'Unknown error')}"
                    error_code = api_error.get('code', 500)
                    print(f"ERROR: {error_message}")
                    print(f"Full error details: {json.dumps(error_details, indent=2)}")
                    
                    if error_code == 400:
                        return jsonify({
                            "response": "The request was invalid. This might be a temporary issue.",
                            "error": error_message
                        }), 400
                    elif error_code == 401:
                        return jsonify({
                            "response": "API authentication failed. Please check the system configuration.",
                            "error": "Authentication error"
                        }), 401
                    elif error_code == 429:
                        return jsonify({
                            "response": "The AI service is currently busy. Please try again in a moment.",
                            "error": "Rate limit exceeded"
                        }), 429
                    else:
                        return jsonify({
                            "response": "Sorry, there was an error getting a response from the AI.",
                            "error": error_message
                        }), error_code or 500
                        
                except json.JSONDecodeError:
                    print(f"ERROR: Non-JSON error response: {response.text[:200]}...")
                    return jsonify({
                        "response": "The AI service returned an unexpected response format.",
                        "error": f"HTTP {response.status_code}: {response.text[:100]}"
                    }), 500
            
            # Parse successful response
            try:
                response_data = response.json()
                print("Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse JSON response: {str(e)}")
                print(f"Response content: {response.text[:200]}...")
                return jsonify({
                    "response": "Received invalid response from the AI service.",
                    "error": "Invalid JSON response"
                }), 500
            
        if not response_data.get('candidates'):
            print("No candidates in response")
            return jsonify({
                "response": "Sorry, I couldn't generate a response. Please try rephrasing your question.",
                "error": "No response candidates"
            }), 500
        
        raw_answer = response_data['candidates'][0].get('content', {}).get('parts', [{}])[0].get('text', "")
        
        if not raw_answer or raw_answer == "NO_INFORMATION":
            print("Empty or NO_INFORMATION response")
            return jsonify({
                "response": "I apologize, but I don't have enough accurate information about this specific condition. Please try asking about a different health topic or consult a healthcare professional.",
                "error": "No information available"
            }), 404
            
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