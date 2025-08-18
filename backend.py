from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json

students = [] 
class Student:
    def __init__(self, name, roll, class_name, total_fee):
        self.name = name
        self.roll = roll
        self.class_name = class_name
        self.total_fee = int(total_fee)
        self.paid = 0

    def pay(self, amount):
        self.paid += int(amount)
    

    def to_dict(self):
        return {
            "name": self.name,
            "roll": self.roll,
            "class": self.class_name,
            "total_fee": self.total_fee,
            "paid": self.paid,
            "balance": self.total_fee - self.paid
        }

class MyHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        data = parse_qs(body)

        if self.path == "/register":
            name = data.get("name", [""])[0]
            roll = data.get("roll", [""])[0]
            class_name = data.get("class", [""])[0]
            total_fee = data.get("total_fee", ["0"])[0]

            for s in students:
                if s.roll == roll:
                    self._send_json({"message": "Student already registered with same roll no"}, status=400)
                    return 

            student = Student(name, roll, class_name, total_fee)
            students.append(student)
            self._send_json({"message": "Student Registered", "student": student.to_dict()})

        elif self.path == "/pay":
            name = data.get("name", [""])[0]
            amount = data.get("amount", ["0"])[0]

            for s in students:
                if s.name.lower() == name.lower():
                    s.pay(amount)
                    self._send_json({"message": "Payment Done", "student": s.to_dict()})
                    return

            self._send_json({"error": "Student not found"}, status=404)

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)

        if self.path.startswith("/search"):
            name = query.get("name", [""])[0].lower()
            results = [s.to_dict() for s in students if name in s.name.lower()]
            self._send_json(results)

        elif self.path.startswith("/all"):
            self._send_json([s.to_dict() for s in students])

        else:
            return super().do_GET()

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == "__main__":
    PORT = 8000
    print(f" Server running at http://localhost:{PORT}")
    HTTPServer(("localhost", PORT), MyHandler).serve_forever()
