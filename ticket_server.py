import http.server
import socketserver
import json
from collections import deque

PORT = 8000
# Initialize ticket numbers for each service
ticket_numbers = {
    1: 1000,
    2: 2000,
    3: 3000,
    4: 4000
}

# Initialize queues for each service
ticket_queues = {
    1: deque(),
    2: deque(),
    3: deque(),
    4: deque()
}

# Initialize current and previous ticket numbers for each service
current_tickets = {
    1: None,
    2: None,
    3: None,
    4: None
}

next_tickets = {
    1: None,
    2: None,
    3: None,
    4: None
}

# Service names
service_names = {
    1: "Bursary 1",
    2: "Bursary 2",
    3: "Student service 1",
    4: "Student service 2"
}

class TicketHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global ticket_numbers, ticket_queues, current_tickets, next_tickets, service_names

        if self.path.startswith('/get_ticket'):
            try:
                # Extract service number from query parameter
                service_number = int(self.path.split('?service=')[1])
                if service_number in ticket_numbers:
                    ticket_numbers[service_number] += 1
                    ticket_number = ticket_numbers[service_number]
                    ticket_queues[service_number].append(ticket_number)
                    if not current_tickets[service_number]:
                        current_tickets[service_number] = ticket_number
                    elif not next_tickets[service_number]:
                        next_tickets[service_number] = ticket_number
                    response = {'ticket_number': ticket_number}
                    self.send_response(200)
                else:
                    response = {'error': 'Invalid service number'}
                    self.send_response(400)
            except Exception as e:
                response = {'error': 'Invalid request'}
                self.send_response(400)

            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        elif self.path == '/get_all_tickets':
            # Return all current and next ticket numbers
            response = {
                'current_tickets': current_tickets,
                'next_tickets': next_tickets,
                'service_names': service_names
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        elif self.path.startswith('/complete_service'):
            try:
                # Extract service number from query parameter
                service_number = int(self.path.split('?service=')[1])
                if service_number in ticket_queues:
                    if ticket_queues[service_number]:
                        ticket_queues[service_number].popleft()  # Remove the current ticket
                        current_tickets[service_number] = ticket_queues[service_number][0] if ticket_queues[service_number] else None
                        next_tickets[service_number] = ticket_queues[service_number][1] if len(ticket_queues[service_number]) > 1 else None
                    else:
                        current_tickets[service_number] = None
                        next_tickets[service_number] = None
                    response = {'success': True}
                    self.send_response(200)
                else:
                    response = {'error': 'Invalid service number'}
                    self.send_response(400)
            except Exception as e:
                response = {'error': 'Invalid request'}
                self.send_response(400)

            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        else:
            super().do_GET()

with socketserver.TCPServer(("", PORT), TicketHandler) as httpd:
    print("Serving at port", PORT)
    httpd.serve_forever()
