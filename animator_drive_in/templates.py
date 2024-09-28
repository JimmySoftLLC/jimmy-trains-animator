def return_text_template(self, rq_d):
    self.send_response(200)
    self.send_header("Content-type", "text/plain")  # Change the content type to text/plain
    self.end_headers()
    response = "your response message"
    self.wfile.write(response.encode('utf-8'))  # Write the string directly
    print("Response sent:", response)

def return_object_template(self, rq_d):
    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    response = {"message": "your response message"}
    self.wfile.write(json.dumps(response).encode('utf-8'))
    print("Response sent:", response)