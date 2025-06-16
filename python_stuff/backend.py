from flask import Flask, request, jsonify, send_file
from flask_cors import CORS



# Import your existing modules
from compiler import main as compile

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])

@app.route('/api/compile', methods=['POST'])
def compile_music():
    code = request.data.decode('utf-8')
    code = code.replace('\r\n', '\n').replace('\r', '\n').strip()
    code = code + '\n'  # Ensure the code ends with a newline
    if not code:
        return jsonify({
            'hasError': True,
            'errorMessage': 'No code provided',
            'errorLine': -1,
            'sheetMusicImage': None
        })
    # Redirect stdout to capture any print statements
    print("Compiling code...")
    # Generate MIDI
    print(code)
    midi_data = compile(code)
    print("MIDI data generated successfully.")
    print("Writing MIDI data to file...")
    
    return jsonify({'status': 200})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)